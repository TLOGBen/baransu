------------------------------- MODULE Fidelity -------------------------------
(***************************************************************************)
(* Does a model that does not match its source get past /hypothesis and   *)
(* get declared established with a false verdict?                          *)
(*                                                                         *)
(* SK = plugins/baransu/skills/hypothesis/SKILL.md            (8.27.0)     *)
(* FO = plugins/baransu/skills/hypothesis/references/formal.md             *)
(* SO = plugins/baransu/skills/hypothesis/references/sources.md            *)
(* DF = sources/dogfood-2026-10-25.md  (the dogfood record, frozen copy)   *)
(*                                                                         *)
(* One run of one area, one rule judged by the model checker, code that   *)
(* either breaks the rule ("bug") or not. A model is "faithful", "strict" *)
(* (forbids something the code does, so it may hide a real break) or      *)
(* "loose" (allows something the code cannot do, so it may report a break *)
(* that is not there). Out of this model, and in the README's left-out    *)
(* list: maintenance across source changes (bound by the source hashes of *)
(* seen faithful, FO:73), the comparison rule's own verdict and a real    *)
(* behaviour change found by it (SO), several readings of an ambiguity    *)
(* (FO:63), hand edits of an area, and a rules-side document compared     *)
(* against code (SO --satisfies), which also has two models but no blind  *)
(* pair. Choosing a fairness assumption is part of extracting a model     *)
(* (FO:63) and each one is an item of the list (FO:70), so it sits inside *)
(* Extract and Facts, not beside them.                                     *)
(***************************************************************************)
EXTENDS Naturals

CONSTANTS
    Process,    \* "facts"       = 8.27.0 as written: one model, never-happens list refuted (SK:70)
                \* "blind2facts" = 8.27.0 code against code: two blind models, each refuted, then compared (SO)
                \* "v826"        = 8.26.0: one model, two gates only (broken variant: the old text)
                \* "blind2"      = two blind models compared, no list (broken variant)
    UserKnows,  \* TRUE: the user confirming the rules knows this code (SK:54-60)
    Checker,    \* the agent refuting the list: "independent" = never saw the model,
                \* reads back from the writes (FO:71); "shared" = shares the modellers' blind spot
    Replay,     \* TRUE: SK:77 replays every path of a broken rule before the area counts; FALSE: broken variant
    Kind        \* "code" = replayed on the app by /prove-it; "document" = replayed by a fresh agent against
                \* the quoted passages (SK:77). A /draft sketch is out of this model (its paths wait for code).

Fid == {"faithful", "strict", "loose"}

VARIABLES
    code,     \* does the code really break the rule: "ok" | "bug" (observer: fixed at Init)
    fid,      \* [1..2 -> fidelity of each extracted model, "none" before extraction]
    verdict,  \* the model's verdict on the rule: "none" | "held" | "violated"
    pc,       \* where the run is
    did       \* the steps already done for this model: subset of {"facts", "compare", "replay"}

vars == <<code, fid, verdict, pc, did>>

PCs == {"extract", "check", "trace", "facts", "compare", "gates", "replay",
        "established"}

TypeOK ==
    /\ code \in {"ok", "bug"}
    /\ fid \in [1..2 -> Fid \cup {"none"}]
    /\ verdict \in {"none", "held", "violated"}
    /\ pc \in PCs
    /\ did \subseteq {"facts", "compare", "replay"}

Two == Process \in {"blind2", "blind2facts"}
Lists == Process \in {"facts", "blind2facts"}

\* After a check: the list is refuted (the third gate, SK:70), then the other
\* gates; code against code compares the two sides only once each has passed
\* its gates (SO "passes all three evidence gates on its own").
After(d) == IF Lists /\ "facts" \notin d THEN "facts" ELSE "gates"

\* After the gates (and a comparison): a broken rule is replayed before the area
\* counts as established (SK:77; the status script shows it draft until then).
Publish == IF verdict = "violated" /\ Replay THEN "replay" ELSE "established"

Init ==
    /\ code \in {"ok", "bug"}
    /\ fid = [i \in 1..2 |-> "none"]
    /\ verdict = "none"
    /\ pc = "extract"
    /\ did = {}

\* The model follows the source once a difference was traced back to it
\* (FO:72 refuted items fixed from the source; FO:67 a step the source cannot
\* take; DF:63 differences fixed against the code). Every check runs again, and
\* the changed model's list is refuted again and the sides compared again
\* (FO:73 bound to the model it judged; SO "the comparison runs again").
FixAll == /\ fid' = [i \in 1..2 |-> "faithful"]
          /\ verdict' = "none"
          /\ pc' = "check"
          /\ did' = {}

-----------------------------------------------------------------------------
\* SK:46 read the source; FO:63 true to the source. Any extraction may be off.
\* Two extractors who cannot see each other for code against code (SO; DF:99).
Extract ==
    /\ pc = "extract"
    /\ \E a, b \in Fid :
         fid' = IF Two THEN [i \in 1..2 |-> IF i = 1 THEN a ELSE b]
                       ELSE [i \in 1..2 |-> IF i = 1 THEN a ELSE "none"]
    /\ pc' = "check"
    /\ UNCHANGED <<code, verdict, did>>

\* SK:66 run the check. A faithful model gives the code's own answer; a
\* strict one may lose the break; a loose one may invent one.
Check ==
    /\ pc = "check"
    /\ verdict' \in
         CASE fid[1] = "faithful" -> {IF code = "bug" THEN "violated" ELSE "held"}
           [] fid[1] = "strict"   -> IF code = "bug" THEN {"held", "violated"} ELSE {"held"}
           [] fid[1] = "loose"    -> IF code = "ok"  THEN {"held", "violated"} ELSE {"violated"}
    /\ pc' = "trace"
    /\ UNCHANGED <<code, fid, did>>

\* FO:67 every step of a counterexample is checked against the source before
\* publish: an invented break (a loose model, code that is fine) may be seen
\* here as a step the source cannot take — or missed, and left to the replay.
Trace ==
    /\ pc = "trace"
    /\ IF verdict = "violated" /\ code = "ok"
         THEN \/ FixAll
              \/ /\ pc' = After(did) /\ UNCHANGED <<fid, verdict, did>>
         ELSE /\ pc' = After(did) /\ UNCHANGED <<fid, verdict, did>>
    /\ UNCHANGED code

\* FO:69-74 seen faithful: the never-happens list, derived from the model with
\* a closed-world item per variable (FO:70), shown to the user at the first
\* write (SK:60) and refuted by an agent that never saw the model (FO:71). A
\* strict model's list holds something the code does (assumption A5, the
\* closed-world items); the user catches it when they know the code, an
\* independent checker catches it (A2), a checker with the modellers' blind
\* spot may or may not. A loose model's mistake is in what it allows, which
\* the list does not show.
Facts ==
    /\ pc = "facts"
    /\ \E agentSees \in (IF Checker = "independent" THEN {TRUE} ELSE BOOLEAN) :
         IF fid[1] = "strict" /\ (UserKnows \/ agentSees)
           THEN FixAll
           ELSE /\ did' = did \cup {"facts"}
                /\ pc' = "gates" /\ UNCHANGED <<fid, verdict>>
    /\ UNCHANGED code

\* SO code against code, DF:59-63: compare what a user observes at small bounds.
\* A model that is off differs from one that is not, and a strict one from a
\* loose one (assumption A1). Two models off in the same way look the same.
Compare ==
    /\ pc = "compare"
    /\ IF fid[1] # fid[2]
         THEN FixAll
         ELSE /\ did' = did \cup {"compare"}
              /\ pc' = Publish /\ UNCHANGED <<fid, verdict>>
    /\ UNCHANGED code

\* SK:68-69 / FO:64-65 seen failing and seen succeeding test the rules and goals
\* inside the model, not that the model matches the code (DF:92): a faithful
\* model passes; one that is off may pass or not (A4). A gate that fails sends
\* the run back to fix the model from the source in the same run (SK:75,
\* FO:65), not to an end.
Gates ==
    /\ pc = "gates"
    /\ \/ /\ pc' = IF Two /\ "compare" \notin did THEN "compare" ELSE Publish
          /\ UNCHANGED <<fid, verdict, did>>
       \/ /\ fid[1] # "faithful"
          /\ FixAll
    /\ UNCHANGED code

\* SK:77 every path of a broken rule is replayed — on the app for code, by a
\* fresh agent against the quoted passages for a document. A path the replay
\* refutes is a model error: fixed, everything rerun (FO:67). A confirmed path
\* is recorded and the area counts as established. It runs only on a broken
\* rule (DF:93).
ReplayStep ==
    /\ pc = "replay"
    /\ IF code = "ok"
         THEN FixAll                        \* no real path: the replay refutes it (A3)
         ELSE /\ did' = did \cup {"replay"} \* a real break: the replay confirms one (A3)
              /\ pc' = "established"
              /\ UNCHANGED <<fid, verdict>>
    /\ UNCHANGED code

Done == pc = "established" /\ UNCHANGED vars

Next == Extract \/ Check \/ Trace \/ Facts \/ Compare \/ Gates \/ ReplayStep \/ Done

Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------
\* R1 (safety): an established hypothesis that says the rule holds is right.
NoFalseHeld == (pc = "established" /\ verdict = "held") => code = "ok"

\* R2 (safety): an established hypothesis that says the rule breaks is right.
NoFalseBreak == (pc = "established" /\ verdict = "violated") => code = "bug"

\* R3 (safety): once the replay is done (or none is owed), a hypothesis that
\* says the rule breaks is right.
Replayed == "replay" \in did \/ ~Replay
NoFalseBreakAfterReplay == (pc = "established" /\ verdict = "violated" /\ Replayed) => code = "bug"

\* G1 (goal): a real break is found and the hypothesis is established.
FoundReal == pc = "established" /\ verdict = "violated" /\ code = "bug"
NotFoundReal == ~FoundReal

\* G2 (goal): code that is fine is established as holding.
ClearedReal == pc = "established" /\ verdict = "held" /\ code = "ok"
NotClearedReal == ~ClearedReal

-----------------------------------------------------------------------------
\* Seen succeeding: the same spec with one named transition removed.
NextNoGates == Extract \/ Check \/ Trace \/ Facts \/ Compare \/ ReplayStep \/ Done
SpecNoGates == Init /\ [][NextNoGates]_vars
=============================================================================
