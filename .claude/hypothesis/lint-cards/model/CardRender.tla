---- MODULE CardRender ----
(* The transcript's rows and lint's cards, one action per step the platform or lint takes.
   Sources: plugins/baransu/hooks/adapters/claude-code/view/hooks.ts (ui.render hooks), view/card.ts (drawCard),
   engine/engine.ts (keepCard and its trim, cardFor, cleared, callAfterTake: the card is kept before the
   tool.call hook returns, lines 371 and 513-518); the platform from claude-code.d.ts (ToolUse / ToolResult /
   ToolGroup) and what HUNT-2026-002 measured (a folded group's rows draw through ToolUse, no ToolResult).
   Variant:
     "old"      the source now: the card only on ToolResult (a standalone row);
     "new"      the change: the card on ToolUse, a held call's error text emptied, a carded group unfolds;
     "nogroup"  "new" without the ToolGroup hook;
     "noempty"  "new" without emptying a standalone held call's ToolResult;
     "double"   "new" that also draws the card on ToolResult.
   KeepFirst: the card is kept before the platform draws the finished row (the source); FALSE lets the
   draw come first and the keep a step later. *)
EXTENDS CardRules, Integers

CONSTANTS Variant, KeepFirst, Cap, MaxSteps

Outcomes == {"held", "card", "plain"}

VARIABLES
  n,          \* steps so far (scope)
  outcome,    \* per call: how it will end
  owed,       \* per call: its card is still to be kept (KeepFirst = FALSE only)
  seq,        \* per call: start order (the trim drops the oldest)
  nextSeq,
  openBase    \* the platform's own choice for the folded group: desktop draws its rows, the terminal one line

vars == <<judgeVars, n, outcome, owed, seq, nextSeq, openBase>>

Step == n < MaxSteps /\ n' = n + 1

\* The group as drawn: the ToolGroup hook unfolds one holding a finished call with a card.
OpenOf(m, r, k, base) ==
  IF Variant \in {"new", "noempty", "double"} /\ \E d \in Calls : m[d] = "group" /\ ~r[d] /\ k[d]
    THEN TRUE ELSE base

\* What one drawing of a row shows: <<cards, error text>>.
DrawOf(m, op, r, k, h) ==
  IF r \/ m = "none" \/ (m = "group" /\ ~op) THEN <<0, FALSE>>
  ELSE IF Variant = "old"
    THEN (IF m = "solo" THEN <<IF k THEN 1 ELSE 0, h /\ ~k>> ELSE <<0, h>>)
  ELSE IF Variant = "noempty" /\ m = "solo" THEN <<IF k THEN 1 ELSE 0, h>>
  ELSE IF Variant = "double" /\ m = "solo" THEN <<IF k THEN 2 ELSE 0, h /\ ~k>>
  ELSE <<IF k THEN 1 ELSE 0, h /\ ~k>>

\* Redraw the rows in S from the next state's values; the others keep their last drawing.
Redraw(S, m, op, r, k, h) ==
  /\ cardDrawn' = [c \in Calls |-> IF c \in S THEN DrawOf(m[c], op, r[c], k[c], h[c])[1] ELSE cardDrawn[c]]
  /\ errDrawn' = [c \in Calls |-> IF c \in S THEN DrawOf(m[c], op, r[c], k[c], h[c])[2] ELSE errDrawn[c]]

\* keepCard: keep c's card; past Cap cards the oldest goes (engine.ts keepCard).
KeepOne(k, c) ==
  LET k1 == [k EXCEPT ![c] = TRUE]
      held1 == {d \in Calls : k1[d]}
      oldest == CHOOSE d \in held1 : \A e \in held1 : seq[d] <= seq[e]
  IN IF Cardinality(held1) > Cap THEN [k1 EXCEPT ![oldest] = FALSE] ELSE k1

Init ==
  /\ mode = [c \in Calls |-> "none"] /\ running = [c \in Calls |-> FALSE] /\ held = [c \in Calls |-> FALSE]
  /\ kept = [c \in Calls |-> FALSE] /\ cardDrawn = [c \in Calls |-> 0] /\ errDrawn = [c \in Calls |-> FALSE]
  /\ user = "none" /\ n = 0 /\ outcome = [c \in Calls |-> "plain"] /\ owed = [c \in Calls |-> FALSE]
  /\ seq = [c \in Calls |-> 0] /\ nextSeq = 1
  /\ openBase \in BOOLEAN /\ open = openBase

\* tool.call starts c: its row appears running; a call already on the screen folds with it into a group,
\* and the group's rows are drawn again.
Start(c, o) ==
  /\ Step /\ mode[c] = "none"
  /\ LET others == {d \in Calls : mode[d] # "none"}
         m1 == IF others = {} THEN [mode EXCEPT ![c] = "solo"]
               ELSE [d \in Calls |-> IF d = c \/ d \in others THEN "group" ELSE mode[d]]
         r1 == [running EXCEPT ![c] = TRUE]
         h1 == [held EXCEPT ![c] = (o = "held")]
         op == OpenOf(m1, r1, kept, openBase)
     IN /\ mode' = m1 /\ running' = r1 /\ held' = h1 /\ open' = op
        /\ Redraw({d \in Calls : m1[d] # "none"}, m1, op, r1, kept, h1)
  /\ outcome' = [outcome EXCEPT ![c] = o] /\ seq' = [seq EXCEPT ![c] = nextSeq] /\ nextSeq' = nextSeq + 1
  /\ UNCHANGED <<kept, user, owed, openBase>>

\* The call ends: lint keeps its card (a held call's or a finding's) and the hook returns; the platform draws
\* the finished row. With KeepFirst = FALSE the keep is owed to a later step.
Finish(c) ==
  /\ Step /\ running[c]
  /\ LET r1 == [running EXCEPT ![c] = FALSE]
         carded == outcome[c] # "plain"
         k1 == IF carded /\ KeepFirst THEN KeepOne(kept, c) ELSE kept
         op == OpenOf(mode, r1, k1, openBase)
     IN /\ running' = r1 /\ kept' = k1 /\ open' = op
        /\ owed' = [owed EXCEPT ![c] = carded /\ ~KeepFirst]
        /\ Redraw({d \in Calls : mode[d] = "group" \/ d = c}, mode, op, r1, k1, held)
  /\ UNCHANGED <<mode, held, user, outcome, seq, nextSeq, openBase>>

\* The owed keep lands; nothing is drawn by it (cardFor is read only while a row draws).
KeepLate(c) ==
  /\ Step /\ owed[c] /\ mode[c] # "none"
  /\ kept' = KeepOne(kept, c) /\ owed' = [owed EXCEPT ![c] = FALSE]
  /\ UNCHANGED <<mode, running, held, open, cardDrawn, errDrawn, user, outcome, seq, nextSeq, openBase>>

\* The person opens or closes the folded group; its rows are drawn again.
Toggle(want) ==
  /\ Step /\ \E d \in Calls : mode[d] = "group"
  /\ LET op == OpenOf(mode, running, kept, want) IN
     /\ openBase' = want /\ open' = op /\ user' = IF want THEN "open" ELSE "close"
     /\ Redraw({d \in Calls : mode[d] = "group"}, mode, op, running, kept, held)
  /\ UNCHANGED <<mode, running, held, kept, outcome, owed, seq, nextSeq>>

\* A scroll draws one row again.
Scroll(c) ==
  /\ Step /\ mode[c] # "none"
  /\ Redraw({c}, mode, open, running, kept, held)
  /\ UNCHANGED <<mode, running, held, kept, open, user, outcome, owed, seq, nextSeq, openBase>>

\* A reload of the plugin: the cards live in $.state and stay; nothing is drawn by it.
Reload ==
  /\ Step
  /\ UNCHANGED <<judgeVars, outcome, owed, seq, nextSeq, openBase>>

\* /clear: the transcript starts over and lint's state with it (engine.ts cleared).
Clear ==
  /\ Step /\ \A c \in Calls : ~running[c]
  /\ mode' = [c \in Calls |-> "none"] /\ kept' = [c \in Calls |-> FALSE] /\ held' = [c \in Calls |-> FALSE]
  /\ cardDrawn' = [c \in Calls |-> 0] /\ errDrawn' = [c \in Calls |-> FALSE] /\ owed' = [c \in Calls |-> FALSE]
  /\ user' = "none" /\ open' = openBase
  /\ UNCHANGED <<running, outcome, seq, nextSeq, openBase>>

Next ==
  \/ \E c \in Calls, o \in Outcomes : Start(c, o)
  \/ \E c \in Calls : Finish(c) \/ KeepLate(c) \/ Scroll(c)
  \/ \E w \in BOOLEAN : Toggle(w)
  \/ Reload
  \/ Clear

Spec == Init /\ [][Next]_vars
====
