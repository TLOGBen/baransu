--------------------------------- MODULE MC2 --------------------------------
(* Scope 2: three independent tasks, two seats - can questions use up every *)
(* seat while a ready task waits with nobody told?                          *)
EXTENDS Swarm, TLC

StateView == <<board, attempt, awaiting, owner, report, jobsAt, wstate, asked,
               waitFor, answered, resumed, blocks, envFixed, jobUsed>>
WorkerSym == Permutations(Workers)

DepsDef  == [t \in {"t1", "t2", "t3"} |-> {}]
PathsDef == [t \in {"t1", "t2", "t3"} |->
               CASE t = "t1" -> {"a"} [] t = "t2" -> {"b"} [] t = "t3" -> {"c"}]
=============================================================================
