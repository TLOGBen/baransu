# area — the one directory a hypothesis lives in, and the one way it is read

(unimplemented) Intent: this file is for `/hypothesis` and for whoever maintains `scripts/hypothesis.py`. Readers never load it; what they need is printed by the script. If a reader skill ever has to open this file to do its job, the interface has leaked — fix the script's output, not the reader.

## Layout

```
.claude/hypothesis/
  <area>/                 # kebab-case, named for the behaviour, not the file (approval, not service-py)
    README.md             # the contract (front matter) + the explanation (body); the only file the script parses
    page.html             # the diagram series, opened for the user
    <Model>.tla, *.cfg    # or the verifier's harness files; every part cites its source
    evidence/             # seen-failing and seen-succeeding outputs, broken-variant diffs, latest run
  .<area>.draft/          # a write in progress; dot-dirs are invisible to the script
```

(unimplemented) No index file: the script globs `*/README.md`, so there is no list to drift from the directories. `/ship` never archives `hypothesis/` (kept product, committed with the branch).

## The contract (README front matter)

(unimplemented) A YAML subset the script parses with the standard library: scalars, and lists of one-line scalars — no nesting, no multi-line values. The fields, in order:

| Field | Value | Read by |
|---|---|---|
| `area` | the directory name | script |
| `input` | `code` \| `symptom` \| `document` \| `comparison` | humans only — the script never branches on it |
| `verdict` | see §Verdict | script |
| `sync` | the commit HEAD pointed at when the check last passed its gates | script (message), `--maintain` (diff base) |
| `covers` | one line per source file: `<path> <git blob hash> [<label>]` | script (staleness) |
| `rules` | one line per rule: `<id> <safety\|goal> <status>｜<plain sentence>` | script prints them |
| `findings` | one line per finding: `<id> <kind> → <rule id>｜<one-sentence harm>` | script prints them |
| `checks` | one line per rule: `<rule id> <tool adapter> <args…>` — the adapter fixes the executable; the args are only its arguments, so a README cannot name a program to run | script `check` |
| `tool` | `<name> <version>` | script prints it |
| `bounds` | one line | script prints it |

## Verdict

(unimplemented) Stored values, written only by `/hypothesis`:

| `verdict` | 顯示 | meaning |
|---|---|---|
| `holds` | 成立 | every rule holds within the bounds |
| `open` | 待釐清 | no rule is broken, but at least one rule's truth waits on an ambiguity |
| `broken` | 不成立 | at least one finding of kind bug, contradiction, gap, or refinement |
| `cannot` | 無法寫成 | no model; README §Not formalized carries the reason record |

(unimplemented) Computed by the script, never stored, and always shown instead of the stored verdict: `過期` (a `covers` line no longer matches, a file is missing, or the README cannot be parsed) and `舊位置` (a legacy `.claude/prove-it/formal/<area>/`; when the same name exists in both places the new one is used and the legacy one is only listed, never rerun). Rule status values: `holds`, `broken`, `open`.

## Sync point

(unimplemented) One mechanism for every input kind: the blob hash of each covered file at the moment the gates passed (`git hash-object -- <path>`, which also works for an untracked or uncommitted file and for a document outside the repo's history). `sync` is kept for the diff base and for humans; staleness never reads it. A hypothesis checked against a dirty working tree is therefore still exact. The document's own version label rides in the `covers` line's third token. A `covers` line may name a directory ending in `/`; its hash is the hash of the sorted `<path> <blob>` lines of the files under it, so a new file in that directory — a new writer of the guarded state — makes the area stale. Hashing uses git's default filters, so line-ending settings do not make a checkout on another platform look stale.

## Writing

(unimplemented) Build the whole area in `.<area>.draft/`; swap it in only when every gate passed: rename the live area to `.<area>.old/`, rename the draft into place, remove `.<area>.old/`. A stop at any point leaves either the old area or the new one live, never a mix; a leftover dot-dir is reported by the next run and resumed or removed on the user's word. Between the two renames the live name is briefly absent, so the script shows a `.<area>.old/` or `.<area>.draft/` with no live `<area>/` as 過期, never as "no hypothesis here".

## Reader interface

(unimplemented) The script's two subcommands, their output lines, and their exit codes — the full reader contract, mirrored in `hypothesis.py --help`:

- `status [path…]` — areas covering the paths (all areas when none): one line `<area>\t<顯示>\t<說明>\t<README path>`, then its rules indented, each with its status only when the area is in sync, then its findings. Exit 0 when every area is 成立 or 無法寫成 (a `cannot` area claims nothing, so it blocks nothing — its line still shows), 1 any 不成立 or 待釐清, 2 any 過期 or 舊位置, 3 the script could not run. The highest applicable code wins.
- `check [path…|area…]` — as `status`, after rerunning each in-sync area's `checks`; no argument means areas covering `git diff --name-only HEAD` plus untracked files. A stale area is not rerun. A rerun that disagrees with the stored verdict on an unchanged source prints `與紀錄不符` and exits 3.
