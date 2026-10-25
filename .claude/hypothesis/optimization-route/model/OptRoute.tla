------------------------------ MODULE OptRoute ------------------------------
(***************************************************************************)
(* The route `_shared/optimization.md` §2 lays out for a request to make   *)
(* something better: model first, decide whether optimization is asked,   *)
(* name the kinds, split, solve, put back together and re-check, hand     *)
(* over.                                                                   *)
(*                                                                         *)
(* OPT = plugins/baransu/skills/_shared/optimization.md                    *)
(*                                                                         *)
(* One request with two parts; the environment decides whether it asks    *)
(* for better, how each part splits, whether an ordered part's later      *)
(* choices would change earlier ones, the gap the solve reaches (zero,    *)
(* positive, or unknown when no bound is known), and whether a changed    *)
(* version still gives the same answers within the tolerance fixed first. *)
(* Which kinds apply and whether they compete or chain (OPT:37-38) shows  *)
(* up only through the gap and the claim, so it has no variable of its    *)
(* own.                                                                    *)
(***************************************************************************)

CONSTANTS
    Reading,    \* OPT:44 "Optimal is said only with a zero gap": "strict" = the text as written;
                \*   "loose" = the wording before this hypothesis (broken variant): any written
                \*   proof (a ratio, a positive gap) let the result be called optimal
    Recheck,    \* TRUE: OPT:45 re-checks a changed version; FALSE: broken variant
    AskGate,    \* TRUE: OPT:36 stops when optimization is not asked; FALSE: broken variant
    AtBoundAny, \* FALSE: OPT:44 "already at the bound" only when the split keeps the optimum;
                \*   TRUE: the wording before this hypothesis (broken variant): any part's own bound
    Deliverable \* TRUE: the route can hand over; FALSE: seen-succeeding variant

Parts == {1, 2}
Splits == {"separable", "ordered", "coupled", "whole"}

VARIABLES
    pc,         \* where the route is
    asked,      \* does the request ask for better (environment, OPT:36)
    split,      \* [part -> how it splits] (OPT:39-43); "none" before the split step
    orderOK,    \* [part -> an ordered part's later choices would not change earlier ones] (OPT:41)
    gap,        \* the gap the solve reaches: "none" | "zero" | "pos" | "unknown" (OPT:25-26, 44)
    changed,    \* the solve produced a new version (FALSE: already at the bound, OPT:44)
    correct,    \* the new version gives the same answers within the fixed tolerance (OPT:36, 45)
    claim,      \* what is said of the result: "none" | "optimal" | "bound" | "local" | "unknown"
    delivered   \* the result was handed over

vars == <<pc, asked, split, orderOK, gap, changed, correct, claim, delivered>>

TypeOK ==
    /\ pc \in {"model", "ask", "kinds", "split", "solve", "recheck", "deliver", "done"}
    /\ asked \in BOOLEAN /\ changed \in BOOLEAN /\ correct \in BOOLEAN /\ delivered \in BOOLEAN
    /\ split \in [Parts -> Splits \cup {"none"}]
    /\ orderOK \in [Parts -> BOOLEAN]
    /\ gap \in {"none", "zero", "pos", "unknown"}
    /\ claim \in {"none", "optimal", "bound", "local", "unknown"}

Init ==
    /\ pc = "model"
    /\ asked \in BOOLEAN
    /\ split = [p \in Parts |-> "none"] /\ orderOK = [p \in Parts |-> TRUE]
    /\ gap = "none" /\ changed = FALSE /\ correct = TRUE
    /\ claim = "none" /\ delivered = FALSE

\* OPT:35 model it first, whatever was asked.
WriteModel ==
    /\ pc = "model"
    /\ pc' = "ask"
    /\ UNCHANGED <<asked, split, orderOK, gap, changed, correct, claim, delivered>>

\* OPT:36 only when better is asked does the route go on; otherwise the model
\* serves the request as it is and no optimized version comes out.
Ask ==
    /\ pc = "ask"
    /\ pc' = IF asked \/ ~AskGate THEN "kinds" ELSE "done"
    /\ UNCHANGED <<asked, split, orderOK, gap, changed, correct, claim, delivered>>

\* OPT:37-38 name the kinds and whether they compose, compete or chain.
Kinds ==
    /\ pc = "kinds"
    /\ pc' = "split"
    /\ UNCHANGED <<asked, split, orderOK, gap, changed, correct, claim, delivered>>

\* OPT:39-43 each part splits one of four ways (parts may differ); an ordered
\* part may or may not have later choices that would change earlier ones.
Split ==
    /\ pc = "split"
    /\ \E s \in [Parts -> Splits], ok \in [Parts -> BOOLEAN] :
         /\ split' = s
         /\ orderOK' = [p \in Parts |-> IF s[p] = "ordered" THEN ok[p] ELSE TRUE]
    /\ pc' = "solve"
    /\ UNCHANGED <<asked, gap, changed, correct, claim, delivered>>

\* What proves the result optimal: a zero gap (OPT:44, row 5 "optimal when the
\* gap is 0"), and for every ordered part, no later choice that changes an
\* earlier one (OPT:41).
ProofOK(g) == g = "zero" /\ \A p \in Parts : split[p] = "ordered" => orderOK[p]

\* OPT:44 every part at its own bound is the whole at its bound only when the
\* split keeps the optimum: no coupled part, no ordered part whose later
\* choices change earlier ones.
SplitKeepsOptimum == \A p \in Parts : split[p] # "coupled" /\ (split[p] = "ordered" => orderOK[p])

\* What the text lets be said: optimal only with the proof; a positive gap is
\* a bound; no known bound is said as such; a non-convex local optimum is said
\* to be local (OPT:26, 44).
Claims(g) ==
    IF Reading = "strict"
      THEN IF ProofOK(g) THEN {"optimal"}
           ELSE IF g = "pos" THEN {"bound"}
           ELSE IF g = "unknown" THEN {"local", "unknown"}
           ELSE {"bound"}                         \* zero gap but an ordered part fails
      ELSE {"optimal", "bound", "local", "unknown"}

\* OPT:44 the best possible first: already at the bound means say so and stop,
\* nothing changed; otherwise apply the instrument and write the proof.
Solve ==
    /\ pc = "solve"
    /\ \/ /\ AtBoundAny \/ SplitKeepsOptimum      \* already at the bound
          /\ changed' = FALSE
          /\ gap' = "zero" /\ correct' = TRUE /\ claim' = "optimal"
          /\ pc' = "deliver"
       \/ /\ changed' = TRUE
          /\ \E g \in {"zero", "pos", "unknown"}, c \in BOOLEAN :
               /\ gap' = g /\ correct' = c /\ claim' \in Claims(g)
          /\ pc' = "recheck"
    /\ UNCHANGED <<asked, split, orderOK, delivered>>

\* OPT:45 re-check a changed version against the tolerance fixed in step 2
\* (OPT:36), by each row's own method, assumed able to see a different answer
\* (A1): a different answer is not handed over, the route goes back to solve.
DoRecheck ==
    /\ pc = "recheck"
    /\ pc' = IF Recheck /\ ~correct THEN "solve" ELSE "deliver"
    /\ UNCHANGED <<asked, split, orderOK, gap, changed, correct, claim, delivered>>

\* OPT:45 only a version that passed is handed over, with what was proved.
Deliver ==
    /\ pc = "deliver" /\ Deliverable
    /\ delivered' = TRUE
    /\ pc' = "done"
    /\ UNCHANGED <<asked, split, orderOK, gap, changed, correct, claim>>

Done == pc = "done" /\ UNCHANGED vars

Next == WriteModel \/ Ask \/ Kinds \/ Split \/ Solve \/ DoRecheck \/ Deliver \/ Done
Spec == Init /\ [][Next]_vars

-----------------------------------------------------------------------------
\* R1 a result called optimal has the proof of it.
NoUnprovenOptimal == (delivered /\ claim = "optimal") => ProofOK(gap)
\* R2 what is handed over gives the same answers as before, within the fixed tolerance.
NoWrongAnswer == delivered => correct
\* R3 an optimized new version is handed over only when better was asked.
OnlyWhenAsked == (delivered /\ changed) => asked
\* G1 a result can be handed over and proven optimal.
NotOptimalDelivered == ~(delivered /\ changed /\ claim = "optimal")
\* G2 a result can be handed over with an honest bound.
NotBoundDelivered == ~(delivered /\ claim = "bound")
=============================================================================
