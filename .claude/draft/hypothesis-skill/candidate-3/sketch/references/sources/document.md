# source adapter — document

(unimplemented) Intent: one prose document — requirement interview, meeting notes, RFP, SA, SD, any spec. Checks the flow the document describes, never whether a system runs that way.

## Recognize

(unimplemented) A `.md`, `.txt`, `.pdf`, `.docx`, `.pptx`, `.html` file or a URL whose content is prose.

## Read

(unimplemented) Through `/read --save`; copy the resulting Markdown to `sources/<slug>.md` in staging. The snapshot is what every citation points at.

## Cite

(unimplemented) The passage verbatim in 「」 plus the location: file, section, page or line. Resolves when the quoted text appears verbatim in the snapshot — a mechanical check, run at gate 1.

## Extract

(unimplemented) Actors are roles the document names; states are statuses it names; a step is one sentence or table row that moves a status or permits an action. Nothing the document leaves open is filled in — it becomes a question with the two readings and who can answer.

### Profiles

(unimplemented) A table, not adapters: what to look for first by document type — RFP: obligations and acceptance; SA: rules and roles; SD: flows and screens; interview or meeting notes: decisions, with the speaker. A new document type is a new row. A new kind whose citation or sync differs (a BPMN file, an OpenAPI spec) is a new adapter.

## Sync point

(unimplemented) `{ role, kind: document, path, version, sha256, snapshot, snapshot_sha256, converter }`. `version` as the document states it, or `unversioned`.

## Stale

(unimplemented) `sha256` of the original file differs from the recorded one. A different `snapshot_sha256` with the same original (converter changed) is not stale; it is noted.

## Mutate

(unimplemented) Per safety rule, delete or negate the one cited passage that makes it hold; realized in the model as a variant.

## Replay

(unimplemented) For each trace step, find the passage that permits it. All found → finding. A step that needs something the document does not say → an ambiguity question, not a contradiction.

## Findings vocabulary

(unimplemented) `矛盾 N` (two rules that cannot both hold, with the path that hits both), `缺漏 N` (a state with no way out, or a case the document does not cover), `模糊 N` (a question, to whom). Each quotes the passages.

## Diff since sync

(unimplemented) Read the new version, diff its Markdown against the snapshot, map each changed passage to the claim-sheet items that cite it.
