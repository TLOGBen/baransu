---- MODULE CardRules ----
(* The judge: the rules confirmed by the user (2026-11-03) over what the screen shows.
   Written before the model of the code; it holds no code logic. *)
EXTENDS Naturals, FiniteSets

CONSTANTS Calls

VARIABLES
  mode,     \* per call: "none" (not in the transcript), "solo" (a standalone row), "group" (a row of a folded group)
  running,  \* per call: the call is still running
  held,     \* per call: lint refused it (the preview held it)
  kept,     \* per call: lint keeps a card for it now (keepCard; a trim or /clear removes it)
  open,     \* the folded group as drawn: TRUE its rows draw, FALSE one line
  cardDrawn,\* per call: the cards the last drawing of the row showed (0, 1 or 2)
  errDrawn, \* per call: the last drawing of the row showed the error text
  user      \* the person's last choice for the group: "none", "open", "close"

judgeVars == <<mode, running, held, kept, open, cardDrawn, errDrawn, user>>

Seen(c) == mode[c] = "solo" \/ (mode[c] = "group" /\ open)

\* A: a call with a card whose row is on the screen and done shows the card.
A == \A c \in Calls : (Seen(c) /\ ~running[c] /\ kept[c]) => cardDrawn[c] >= 1

\* B: a held call's card stands in place of its error text.
B == \A c \in Calls : (Seen(c) /\ ~running[c] /\ held[c] /\ kept[c]) => ~errDrawn[c]

\* D: one card per call.
D == \A c \in Calls : cardDrawn[c] <= 1

\* Q1-b: a folded group holding a call with a card does not stay one line.
Q1 == (\E c \in Calls : mode[c] = "group" /\ ~running[c] /\ kept[c]) => open

\* Reading (open): a group the person closed stays closed. Reported, not required.
UserClose == user = "close" => ~open
====
