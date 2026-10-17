# Investigator prompt

Fill in the placeholders and send the text below as the agent's prompt. Paste in the matching section of `sources.md` for this investigator's class, and the "Incident flavour" section too when the target is defensive code.

---

You are gathering evidence about why a piece of code has its current shape. Other investigators search other sources in parallel, and the main session will weigh everything together. Search only your assigned source, go deep, and report evidence accurately. Do not write files or change anything anywhere.

## Question

> {QUESTION}

## Code anchor

- Target: {FILES_WITH_LINE_RANGES}
- Key symbols: {SYMBOLS}
- Commits touching it, newest first, with dates: {COMMITS}
- PR numbers: {PR_NUMBERS}
- Ticket or issue IDs: {TICKET_IDS}

## Your source

{SOURCE_CLASS}

{SOURCES_MD_SECTION}

## How to search

1. Search wide first, then narrow to the items that matter.
2. Read each item whole — the full PR thread, page, or transcript passage. The reason is often in a reply, not the title.
3. Follow links inside your source only. A pointer into another source goes under Leads for its investigator.
4. Quote verbatim, with an exact location (hash, PR number, URL, file and line, transcript file and line), so the reader can check it in seconds.
5. Record every query you ran, including the ones that found nothing.
6. When items disagree, report all of them.

Before calling a finding strong, ask what you would see if your reading were wrong. Never round a partial finding up to a confident one, and never invent.

What the code does is not why it was written. Claim a reason only where someone wrote it down. Do not answer the question or pick a side; gather the material and leave the reasoning to the main session.

## Report in this shape

- **Source**: which source you searched.
- **Searched**: the queries, items opened, and places looked, verbatim.
- **Direct evidence**: per item, the quote, its exact location, author and date if known, and one sentence on how it bears on the question.
- **Indirect evidence**: per item, what it is, where it is, what it suggests and by what chain, and any other reading it allows.
- **Contradictions**: items that disagree, with both locations.
- **Gaps**: what you searched for and did not find, specifically.
- **Leads**: pointers into other sources.
