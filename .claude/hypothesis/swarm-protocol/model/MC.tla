--------------------------------- MODULE MC ---------------------------------
(* Scope: three tasks, two workers. t1 and t2 share path a (they must not *)
(* run together); t3 depends on t1 and is added by the user mid-run.      *)
EXTENDS Swarm, TLC

\* who and compacted only label a step; they never enable or disable one.
StateView == <<board, attempt, awaiting, owner, report, jobsAt, wstate, asked,
               waitFor, answered, resumed, blocks, envFixed, jobUsed>>
WorkerSym == Permutations(Workers)

DepsDef  == [t \in {"t1", "t2", "t3"} |-> IF t = "t3" THEN {"t1"} ELSE {}]
PathsDef == [t \in {"t1", "t2", "t3"} |->
               CASE t = "t1" -> {"a"} [] t = "t2" -> {"a", "b"} [] t = "t3" -> {"b"}]
=============================================================================
