---- MODULE CodexRules ----
(* The judge: rules C1-C6 (user 2026-11-18) as properties over what the hook
   processes output to Codex and what really happened (ghost variables).
   Written before the model of the adapter; it holds no adapter logic.
   R1-R21 are inherited by refinement (README Q1), not restated here. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Items, Events

VARIABLES
  delivered,   \* output: how many times each owed item was handed to the model
  extra,       \* truth: how many processes handed an item over and were killed before writing the state back
  lostG,       \* truth: a process wrote the state back over a newer state it never read (lost update)
  generated,   \* truth: the items that became owed
  holdOut,     \* output: the model responses in which the repeated act was held (and the model got the reason)
  releaseOut,  \* output: the model responses in which the repeated act was released
  ranG,        \* truth: the model responses in which Codex actually ran the repeated act (released, or let
               \*   through because its hook gave up, crashed or timed out before answering)
  failDeny,    \* output: a process that failed or gave up on the lock answered deny
  gaveUpDead,  \* truth: a process gave up waiting while the lock's holder was already dead
  promptOk,    \* truth: the user's next message's hook ran its output step
  promptSeen,  \* output: the items handed over by the time that output step ran
  allDone,     \* truth: every process finished or died
  stranded     \* truth at the end: an item was taken out of the state and never handed over

judgeVars == <<delivered, extra, lostG, generated, holdOut, releaseOut, ranG, failDeny, gaveUpDead,
               promptOk, promptSeen, allDone, stranded>>

\* C1: no write overwrites a state the writer did not read.
C1 == ~lostG

\* C2: an item reaches the model once; one more time only per process killed between handing it over and writing.
C2 == \A i \in Items : delivered[i] <= 1 + extra[i]

\* C3: when the hook of the user's next message ran its output, every owed item had reached the model;
\* and when everything has finished, no item was taken and never handed over.
C3 == /\ (promptOk => \A i \in generated : delivered[i] >= 1)
      /\ (allDone => ~stranded)

\* C4 (R11 on Codex): the repeated act runs only in a response after one where it was held and the model got the
\* reason -- judged on what Codex ran, not only on what the engine released (second derivation, 2026-11-18).
C4 == \A r \in releaseOut \cup ranG : \E r2 \in holdOut : r2 < r

\* C5: a hook that failed or gave up on the lock never blocks the act.
C5 == ~failDeny

\* C6: no hook gives up (lets lint go silent) because of a lock whose holder is already dead.
C6 == ~gaveUpDead
====
