

/-! git-facts' wrong-account decision (moments.ts :: wrongAccount, commonDomain), for histories of any length. -/

/-- commonDomain: two different domains can never both hold more than half of the distinct addresses,
so "the" majority is well defined whatever the history's size. -/
theorem majority_unique (a b t : Nat) (h : a + b ≤ t) : ¬ (2 * a > t ∧ 2 * b > t) := by
  omega

/-- The repo's signal for a domain: `some true` fits, `some false` does not, `none` no signal. -/
def fits (host majority : Option String) (d : String) : Option Bool :=
  if host = some d then some true
  else match majority with
    | some m => some (decide (d = m))
    | none => none

def warn (host majority self : Option String) (author : String) : Bool :=
  (fits host majority author = some false) ||
  (match self with
    | some s => decide (s ≠ author) && decide (fits host majority s ≠ some false)
    | none => false)

/-- R1: the author's domain fits the repo and is the one the clone was worked under (or there is none on
record): no warning, for every host, majority and history. -/
theorem r1_quiet (host majority : Option String) (author : String) (self : Option String)
    (hfit : fits host majority author = some true)
    (hself : self = none ∨ self = some author) :
    warn host majority self author = false := by
  rcases hself with h | h <;> subst h <;> simp [warn, hfit]

/-- R2: a switch away from the account on record, whose domain the repo does not reject, always warns. -/
theorem r2_catch (host majority : Option String) (author s : String)
    (hdiff : s ≠ author) (hok : fits host majority s ≠ some false) :
    warn host majority (some s) author = true := by
  simp [warn, hdiff, hok]

/-- R4: an author domain the repo rejects always warns, whatever the clone's record says. -/
theorem r4_foreign (host majority self : Option String) (author : String)
    (h : fits host majority author = some false) :
    warn host majority self author = true := by
  simp [warn, h]

#print axioms majority_unique
#print axioms r1_quiet
#print axioms r2_catch
#print axioms r4_foreign
