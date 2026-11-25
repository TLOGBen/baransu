---- MODULE GitAccount ----
\* git-facts' wrong-account decision (plugins/baransu/hooks/engine/moments.ts :: wrongAccount, commonDomain,
\* hostOf), every combination of the signals it reads, against what the person meant to use.
\* Accounts are reduced to their mail domain: the decision compares only domains.
EXTENDS Naturals

D == {"T", "G", "C"}          \* team / personal (gmail) / client domains
NoneD == "none"

VARIABLES hist, host, self, author, intended
vars == <<hist, host, self, author, intended>>

\* commonDomain: distinct author addresses per domain on the base (0..2 each); a domain holding more than half.
Total == hist["T"] + hist["G"] + hist["C"]
Majority == IF \E d \in D : hist[d] * 2 > Total THEN CHOOSE d \in D : hist[d] * 2 > Total ELSE NoneD

\* wrongAccount's fits: 1 fits, 0 does not, 2 the repo gives no signal.
Fits(d) == IF host = d THEN 1 ELSE IF Majority # NoneD THEN (IF d = Majority THEN 1 ELSE 0) ELSE 2
RepoWhy == Fits(author) = 0
SelfWhy == self # NoneD /\ self # author /\ Fits(self) # 0
Warn == RepoWhy \/ SelfWhy

Init ==
  /\ hist \in [D -> 0..2]
  /\ host \in D \cup {NoneD}
  /\ self \in D \cup {NoneD}      \* the clone's reflog identity; may itself be the wrong account
  /\ author \in D
  /\ intended \in D               \* the account the person should use here
Next == UNCHANGED vars
Spec == Init /\ [][Next]_vars

\* ---- rules (README, confirmed 2026-11-19) ----
\* Accepted misses: the wrong account looks like the repo's own (it fits, or the repo gives no signal), and the
\* clone has no other account on record to compare with. No signal tells it apart from the right one.
KnownBlind == Fits(author) # 0 /\ (self = NoneD \/ self = author \/ Fits(self) = 0)
\* Accepted nuisance (cases 2, 3): the right account's domain fits neither the repo's majority nor its host.
\* Found by TLC (P1): the clone was worked under another account that fits the repo, and the person now uses the
\* right one: R2 cannot tell a correction from a slip, so it warns.
KnownSwitch == self # NoneD /\ self # author /\ Fits(self) # 0
KnownNuisance == Fits(author) = 0 \/ KnownSwitch

R2_Catch == (author # intended) => (Warn \/ KnownBlind)
R1_Quiet == (author = intended) => (~Warn \/ KnownNuisance)
====
