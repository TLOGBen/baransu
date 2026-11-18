---- MODULE CodexHooks ----
(* The Codex adapter (.claude/think/codex-lint-adapter.md): every hook event is
   its own node process that takes a lock in PLUGIN_DATA, reads LintState back,
   runs one engine method, answers Codex, writes the state back and releases the
   lock. Any process may be killed at any step (Codex timeout, crash). The engine
   is abstracted to what touches owed items and the hold-once record; its own
   logic is the lint-mod-state model.

   Scenario (one turn and the user's next message):
     response 1: calls 1 and 2, the same repeated act (a delete preview / check),
                 sent in parallel in one model response (rule C4's case)
     response 2: call 3, the same act sent again after the model saw the result
     then Stop, then the user's next message (UserPromptSubmit).
   Item i1 is owed from before the turn; the Stop queues item i2 for the next step.

   LockMode "code" is the lock as adapters/codex/store.ts writes it (8.49.0):
     - the lock is created in one step (a temp file hard-linked into place);
     - a lock is stale when its holder is dead, or when it has not been touched
       for 150 s: the holder touches it every 10 s (heartbeat), so only a holder
       that stalls (suspended, hung) looks stale while alive (Stall);
     - a stale lock is removed under a second lock, the reaper's: take the reap
       lock, check the lock is still stale, remove it, drop the reap lock; a dead
       reaper's reap lock is removed by the next waiter;
     - WriteGuard: before writing back, a process checks the lock is still its
       own and does not write when it is not.
   Premise, not modelled: no process stalls between a reaper's check and its
   removal (two file calls), so the reap lock itself never goes stale under a
   live reaper.

   Sources: engine.ts callBefore/callAfter (take at call start, deliver with the
   result; a refused call delivers with its reason), timing.ts hold-once,
   adapters/codex/{main,store}.ts, PoC Q3/Q9/Q10 for Codex behaviour. *)
EXTENDS Naturals, FiniteSets

CONSTANTS LockMode,   \* "pid" (design: break only a dead holder's lock), "code" (store.ts), "none",
                      \* "timeout" (break a live holder's), "noreclaim"
          Order,      \* "outfirst" (design, reading D2: answer Codex, then write back), "writefirst"
          GiveUpDeny, \* FALSE (design: a hook that gives up lets the act through); TRUE is a planted bug
          GiveUpOn,   \* TRUE (design: a hook waiting behind a slow live holder gives up); FALSE: hooks always answer
          MaxKills,
          Stalls,     \* "code": how many holders may stall long enough for their lock to look stale
          WriteGuard  \* "code": a process checks its lock is still its own before writing back

Items == {"i1", "i2"}
Calls == {1, 2, 3}
Events == {"pre1", "pre2", "pre3", "post1", "post2", "post3", "stop", "prompt"}
Active == {"wait", "reap", "reapdrop", "read", "out", "write", "rel"}

PreOf(c) == CASE c = 1 -> "pre1" [] c = 2 -> "pre2" [] c = 3 -> "pre3"
PostOf(c) == CASE c = 1 -> "post1" [] c = 2 -> "post2" [] c = 3 -> "post3"
CallOf(e) == CASE e \in {"pre1", "post1"} -> 1 [] e \in {"pre2", "post2"} -> 2 [] OTHER -> 3
Resp(c) == IF c = 3 THEN 2 ELSE 1
IsPre(e) == e \in {"pre1", "pre2", "pre3"}
IsPost(e) == e \in {"post1", "post2", "post3"}

VARIABLES pc, holder, file, loc, rver, outI, ans, rel, answered, kills,
          delivered, extra, lostG, generated, holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen,
          reaper, stalled, stallsUsed

lockVars == <<reaper, stalled, stallsUsed>>
vars == <<pc, holder, file, loc, rver, outI, ans, rel, answered, kills,
          delivered, extra, lostG, generated, holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen,
          reaper, stalled, stallsUsed>>

NoPend == [c \in Calls |-> {}]
Init0 == [owed |-> {"i1"}, pend |-> NoPend, hasPend |-> {}, held |-> {}, ver |-> 0]

Finished(e) == pc[e] \in {"done", "dead"}
\* What Codex acts on for a PreToolUse: its answer, or allow when the hook died before answering (fail-open, PoC Q10).
Eff(e) == IF answered[e] # "none" THEN answered[e] ELSE IF pc[e] = "dead" THEN "allow" ELSE "pending"
\* A call is over: refused, or its PostToolUse finished, or it never got one (cancelled).
CallOver(c) == Finished(PreOf(c)) /\ (Eff(PreOf(c)) = "deny" \/ Finished(PostOf(c)) \/ pc[PostOf(c)] = "idle")
\* "code": what a waiter sees as stale -- a dead holder (pid check) or one that stopped touching its lock.
StaleL(x) == pc[x] = "dead" \/ x \in stalled
\* "code" with WriteGuard: the lock is no longer this process's own (it was declared dead) -- it neither hands
\* anything over nor writes back.
Skip(e) == LockMode = "code" /\ WriteGuard /\ holder # e

CanStart(e) ==
  CASE e \in {"pre1", "pre2"} -> pc["stop"] = "idle"
    [] e = "pre3" -> pc["stop"] = "idle" /\ CallOver(1) /\ CallOver(2)
                     /\ pc["post1"] \notin Active /\ pc["post2"] \notin Active
    [] IsPost(e) -> LET c == CallOf(e) IN
                      /\ pc["stop"] = "idle" /\ Finished(PreOf(c)) /\ Eff(PreOf(c)) = "allow"
                      /\ (c \in {1, 2} => pc["pre3"] = "idle")
    [] e = "stop" -> /\ \A c \in Calls : (pc[PreOf(c)] = "idle" \/ CallOver(c))
                     /\ \A x \in Events \ {"stop", "prompt"} : pc[x] \notin Active
    [] e = "prompt" -> Finished("stop")

Init ==
  /\ pc = [e \in Events |-> "idle"]
  /\ holder = "free"
  /\ file = Init0
  /\ loc = [e \in Events |-> Init0]
  /\ rver = [e \in Events |-> 0]
  /\ outI = [e \in Events |-> {}]
  /\ ans = [e \in Events |-> "none"]
  /\ rel = [e \in Events |-> FALSE]
  /\ answered = [e \in Events |-> "none"]
  /\ kills = 0
  /\ delivered = [i \in Items |-> 0]
  /\ extra = [i \in Items |-> 0]
  /\ lostG = FALSE
  /\ generated = {"i1"}
  /\ holdOut = {}
  /\ releaseOut = {}
  /\ failDeny = FALSE
  /\ gaveUpDead = FALSE
  /\ promptOk = FALSE
  /\ promptSeen = {}
  /\ reaper = "free"
  /\ stalled = {}
  /\ stallsUsed = 0

Start(e) ==
  /\ pc[e] = "idle" /\ CanStart(e)
  /\ pc' = [pc EXCEPT ![e] = "wait"]
  /\ UNCHANGED <<holder, file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

\* Take the lock: free, or no lock at all, or break it (pid: only a dead holder's; timeout: anyone's). "code"
\* takes only a free lock; a stale one is first removed by Reap*.
Acquire(e) ==
  /\ pc[e] = "wait"
  /\ \/ LockMode = "none"
     \/ holder = "free"
     \/ LockMode = "pid" /\ holder \in Events /\ pc[holder] = "dead"
     \/ LockMode = "timeout" /\ holder \in Events /\ holder # e
  /\ holder' = IF LockMode = "none" THEN holder ELSE e
  /\ pc' = [pc EXCEPT ![e] = "read"]
  /\ UNCHANGED <<file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

\* "code": a waiter behind a stale lock takes the reap lock (store.ts #reap, #create on `.reap`).
ReapTake(e) ==
  /\ LockMode = "code" /\ pc[e] = "wait"
  /\ holder \in Events /\ holder # e /\ StaleL(holder)
  /\ reaper = "free"
  /\ reaper' = e
  /\ pc' = [pc EXCEPT ![e] = "reap"]
  /\ UNCHANGED <<holder, file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen, stalled, stallsUsed>>

\* Under the reap lock: check again that the lock is stale, and remove it only then. Removing a stalled live
\* holder's lock declares it dead: under WriteGuard it will not write back, so what it already handed over and
\* has not written is counted now, as a kill before writing is (C2's allowance).
ReapDo(e) ==
  /\ pc[e] = "reap"
  /\ LET breaks == holder \in Events /\ StaleL(holder)
         declared == breaks /\ pc[holder] # "dead" /\ WriteGuard /\ Order = "outfirst" /\ pc[holder] = "write"
     IN /\ holder' = IF breaks THEN "free" ELSE holder
        /\ extra' = IF declared THEN [i \in Items |-> IF i \in outI[holder] THEN extra[i] + 1 ELSE extra[i]] ELSE extra
  /\ pc' = [pc EXCEPT ![e] = "reapdrop"]
  /\ UNCHANGED <<file, loc, rver, outI, ans, rel, answered, kills, delivered, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

\* Drop the reap lock (only one's own) and go back to waiting for the lock.
ReapDrop(e) ==
  /\ pc[e] = "reapdrop"
  /\ reaper' = IF reaper = e THEN "free" ELSE reaper
  /\ pc' = [pc EXCEPT ![e] = "wait"]
  /\ UNCHANGED <<holder, file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen, stalled, stallsUsed>>

\* A dead reaper's reap lock is removed by a waiter (its pid is dead, or it is older than 10 s).
ReapBreak(e) ==
  /\ LockMode = "code" /\ pc[e] = "wait"
  /\ reaper \in Events /\ pc[reaper] = "dead"
  /\ reaper' = "free"
  /\ UNCHANGED <<pc, holder, file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen, stalled, stallsUsed>>

\* "code": the holder stops touching its lock for 150 s while alive (suspended, hung); it goes on later.
Stall(e) ==
  /\ LockMode = "code" /\ stallsUsed < Stalls
  /\ holder = e /\ pc[e] \in {"read", "out", "write", "rel"} /\ e \notin stalled
  /\ stalled' = stalled \cup {e}
  /\ stallsUsed' = stallsUsed + 1
  /\ UNCHANGED <<pc, holder, file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, failDeny, gaveUpDead, promptOk, promptSeen, reaper>>

\* Waiting too long: answer without running the engine (fail-open). With pid breaking (and "code"), a stale
\* holder's lock is broken instead, so giving up happens only behind a live, fresh holder.
GiveUp(e) ==
  /\ GiveUpOn
  /\ pc[e] = "wait" /\ LockMode # "none"
  /\ holder \in Events /\ holder # e
  /\ (LockMode = "pid" => pc[holder] # "dead")
  /\ (LockMode = "code" => ~StaleL(holder))
  /\ answered' = [answered EXCEPT ![e] = IF GiveUpDeny THEN "deny" ELSE "allow"]
  /\ failDeny' = (failDeny \/ GiveUpDeny)
  /\ gaveUpDead' = (gaveUpDead \/ pc[holder] = "dead")
  /\ pc' = [pc EXCEPT ![e] = "done"]
  /\ UNCHANGED <<holder, file, loc, rver, outI, ans, rel, kills, delivered, extra, lostG, generated,
                 holdOut, releaseOut, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

\* Read the state back and run the engine method on it (local work only).
Orphans(L) == UNION {L.pend[c] : c \in L.hasPend}
Read(e) ==
  /\ pc[e] = "read"
  /\ LET L == file
         c == CallOf(e)
         release == \E r \in L.held : r < Resp(c)
     IN
     /\ rver' = [rver EXCEPT ![e] = L.ver]
     /\ CASE IsPre(e) /\ release ->
               /\ loc' = [loc EXCEPT ![e] = [L EXCEPT !.owed = {}, !.pend[c] = L.owed, !.hasPend = L.hasPend \cup {c}]]
               /\ outI' = [outI EXCEPT ![e] = {}]
               /\ ans' = [ans EXCEPT ![e] = "allow"]
               /\ rel' = [rel EXCEPT ![e] = TRUE]
          [] IsPre(e) ->
               /\ loc' = [loc EXCEPT ![e] = [L EXCEPT !.owed = {}, !.held = L.held \cup {Resp(c)}]]
               /\ outI' = [outI EXCEPT ![e] = L.owed]
               /\ ans' = [ans EXCEPT ![e] = "deny"]
               /\ UNCHANGED rel
          [] IsPost(e) ->
               /\ loc' = [loc EXCEPT ![e] = [L EXCEPT !.pend[c] = {}, !.hasPend = L.hasPend \ {c}]]
               /\ outI' = [outI EXCEPT ![e] = IF c \in L.hasPend THEN L.pend[c] ELSE {}]
               /\ ans' = [ans EXCEPT ![e] = "allow"]
               /\ UNCHANGED rel
          [] e = "stop" ->
               /\ loc' = [loc EXCEPT ![e] = [L EXCEPT !.owed = {"i2"}, !.pend = NoPend, !.hasPend = {}]]
               /\ outI' = [outI EXCEPT ![e] = L.owed \cup Orphans(L)]
               /\ ans' = [ans EXCEPT ![e] = "allow"]
               /\ UNCHANGED rel
          [] e = "prompt" ->
               /\ loc' = [loc EXCEPT ![e] = [L EXCEPT !.owed = {}, !.pend = NoPend, !.hasPend = {}]]
               /\ outI' = [outI EXCEPT ![e] = L.owed \cup Orphans(L)]
               /\ ans' = [ans EXCEPT ![e] = "allow"]
               /\ UNCHANGED rel
  /\ pc' = [pc EXCEPT ![e] = IF Order = "outfirst" THEN "out" ELSE "write"]
  /\ UNCHANGED <<holder, file, answered, kills, delivered, extra, lostG, generated, holdOut, releaseOut,
                 failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

\* Answer Codex: the items reach the model, a refusal carries its reason. Under WriteGuard, a process whose lock
\* was taken away (declared dead) answers as a dead hook does -- `{}`, Codex lets the act through, nothing is
\* handed over -- and does not write back.
Out(e) ==
  /\ pc[e] = "out"
  /\ IF Skip(e)
     THEN /\ answered' = [answered EXCEPT ![e] = "allow"]
          /\ pc' = [pc EXCEPT ![e] = "rel"]
          /\ UNCHANGED <<delivered, holdOut, releaseOut, promptOk, promptSeen>>
     ELSE /\ answered' = [answered EXCEPT ![e] = ans[e]]
          /\ delivered' = [i \in Items |-> IF i \in outI[e] THEN delivered[i] + 1 ELSE delivered[i]]
          /\ holdOut' = IF IsPre(e) /\ ans[e] = "deny" THEN holdOut \cup {Resp(CallOf(e))} ELSE holdOut
          /\ releaseOut' = IF IsPre(e) /\ rel[e] THEN releaseOut \cup {Resp(CallOf(e))} ELSE releaseOut
          /\ promptOk' = (promptOk \/ e = "prompt")
          /\ promptSeen' = IF e = "prompt" THEN {i \in Items : delivered'[i] >= 1} ELSE promptSeen
          /\ pc' = [pc EXCEPT ![e] = IF Order = "outfirst" THEN "write" ELSE "rel"]
  /\ UNCHANGED <<holder, file, loc, rver, outI, ans, rel, kills, extra, lostG, generated, failDeny, gaveUpDead>>
  /\ UNCHANGED lockVars

\* Write the state back (atomic replace of the file). Under WriteGuard, a process whose lock is no longer its
\* own does not write: for the state it is as if it had been killed before writing (ReapDo counted it).
Write(e) ==
  /\ pc[e] = "write"
  /\ IF Skip(e)
     THEN UNCHANGED <<file, generated, lostG>>
     ELSE /\ lostG' = (lostG \/ rver[e] # file.ver)
          /\ file' = [loc[e] EXCEPT !.ver = file.ver + 1]
          /\ generated' = IF e = "stop" THEN generated \cup {"i2"} ELSE generated
  /\ pc' = [pc EXCEPT ![e] = IF Order = "outfirst" THEN "rel" ELSE "out"]
  /\ UNCHANGED <<holder, loc, rver, outI, ans, rel, answered, kills, delivered, extra, holdOut,
                 releaseOut, failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

Release(e) ==
  /\ pc[e] = "rel"
  /\ holder' = IF holder = e THEN "free" ELSE holder
  /\ pc' = [pc EXCEPT ![e] = "done"]
  /\ UNCHANGED <<file, loc, rver, outI, ans, rel, answered, kills, delivered, extra, lostG, generated, holdOut,
                 releaseOut, failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

\* Codex (or a crash) ends the process at any step; a lock or reap lock it held stays behind.
Kill(e) ==
  /\ pc[e] \in Active /\ kills < MaxKills
  /\ pc' = [pc EXCEPT ![e] = "dead"]
  /\ kills' = kills + 1
  /\ extra' = IF Order = "outfirst" /\ pc[e] = "write"
              THEN [i \in Items |-> IF i \in outI[e] THEN extra[i] + 1 ELSE extra[i]]
              ELSE extra
  /\ UNCHANGED <<holder, file, loc, rver, outI, ans, rel, answered, delivered, lostG, generated, holdOut,
                 releaseOut, failDeny, gaveUpDead, promptOk, promptSeen>>
  /\ UNCHANGED lockVars

Next == \E e \in Events :
          \/ Start(e) \/ Acquire(e) \/ GiveUp(e) \/ Read(e) \/ Out(e) \/ Write(e) \/ Release(e) \/ Kill(e)
          \/ ReapTake(e) \/ ReapDo(e) \/ ReapDrop(e) \/ ReapBreak(e) \/ Stall(e)

Spec == Init /\ [][Next]_vars

\* ---- what the judge reads that is a function of the state
AllDoneDef == Finished("prompt") /\ \A e \in Events : pc[e] \notin Active
StrandedDef == \E i \in generated :
                 /\ delivered[i] = 0
                 /\ i \notin file.owed
                 /\ ~(\E c \in file.hasPend : i \in file.pend[c])

\* Codex ran the act of call c: its PreToolUse finished and Codex acted on allow (answered, or fail-open).
RanDef == {Resp(c) : c \in {x \in Calls : Finished(PreOf(x)) /\ Eff(PreOf(x)) = "allow"}}

J == INSTANCE CodexRules WITH allDone <- AllDoneDef, stranded <- StrandedDef, ranG <- RanDef

C1 == J!C1
C2 == J!C2
C3 == J!C3
C4 == J!C4
C5 == J!C5
C6 == J!C6
\* Tightness of C2's allowance: without it, a kill between answering and writing back is a second delivery.
C2Strict == \A i \in Items : delivered[i] <= 1
====
