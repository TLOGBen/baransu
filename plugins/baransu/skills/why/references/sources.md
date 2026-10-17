# Evidence classes

Four classes. Each holds a different kind of "why"; knowing which kind to expect tells you what an empty result means. Map every tool the session actually has onto one class by its main evidence; never assume a tool exists because another session had it. A connected tool that fits none of the four (an error tracker, a metrics store) joins the class whose question it answers best and is named in 查了哪些來源.

## 1. Repo record — always present

Best at the reason given at the time of the change, while it was being reviewed.

- Commit messages and diffs: `git log --follow`, `git log -S` / `-G` (the commit that added or removed a string or pattern), `git show`, `git blame -L`.
- PR bodies, review comments and linked issues: `gh pr view`, `gh issue view`, `gh search issues '<term> repo:<owner>/<name>'`. When the remote is not GitHub, say so and use what that host's CLI offers.
- In-tree records: CHANGELOG entries, `docs/` notes, the project's agent instruction files (CLAUDE.md, AGENTS.md — their own `git log -p` often records why a rule was added), code comments, TODO / FIXME / HACK notes near the target. A rule may have been reworded or translated since it was first written, so `git log -S` on today's wording finds only the latest version; read the removed lines in that commit's diff to reach the earlier one.
- Tests: a test's name and assertions often state the edge case that forced the change.
- Co-change: files modified in the same commit show what the change was for.

## 2. Agent decision record — always present on a machine that works with agents

Best at deliberation that never reached a commit message: the options weighed, the user's stated reason, a constraint mentioned once in chat. On a machine where the user delegates the work to Claude Code or Codex, this is often where the real reason lives. Search the items below in this order; the first two are written records of a decision and outrank everything after them.

- Decision records: ADRs under `docs/adr/` (or under each context's own `docs/adr/` in a repo with several contexts). An ADR that covers the target is a Direct answer; read its status too, since a superseded ADR states an old reason.
- The project glossary: `CONTEXT.md`, or `CONTEXT-MAP.md` pointing to one per context. It fixes what a domain term means and which boundary a concept belongs to, which often is the reason a name, a module split or a rule exists.
- Plans and working files under the repo's `.claude/`: `think/` (deliberation plans, each with Key decisions and Not building), `archived/` (earlier sessions' working dirs), `review/`, `hunt/`, and the research a decision drew on in `learn/` and `read/material/`. These directories are often cleaned or untracked later, so also look in git history: `git log --all --name-only -- '.claude/**'` lists the ones ever committed, and `git show <commit>:<path>` reads them back.
- Memory files: the user's agent memory (Claude Code: `~/.claude/projects/*/memory/`), which records feedback and project decisions with a **Why:** line.
- Local logs a plugin or tool writes about its own use (for example `~/.claude/<plugin>/` telemetry): they show how a removed or changed feature was actually used before the decision.
- Session transcripts. Claude Code keeps them as `~/.claude/projects/<encoded-cwd>/*.jsonl`, filed under the directory the session started in, so a repo's conversations are often under the home directory's folder; Codex keeps them under `~/.codex/sessions/<YYYY>/<MM>/<DD>/*.jsonl`; sessions run in the cloud are not on this machine at all. Search them like this:
  1. Start from a session link in the commit (the `Claude-Session:` trailer or a session URL). Grep its session id across the local transcript folders once: a hit is the conversation; no hit means it ran elsewhere (usually the cloud), so name the link in 不知道什麼 and stop looking for it.
  2. Check how far back the local transcripts go: the earliest `timestamp` inside the files across every project folder (the repo may have moved, leaving its older conversations under its old path's folder). A commit older than that has no local conversation, and a stretch of days with no messages is a gap; say so instead of searching.
  3. Otherwise bound by the timestamps inside the files, not the file modification time, which only marks a long session's last activity. Keep the lines whose `timestamp` falls within a few days of the commit dates.
  4. Read only what the user typed: user messages whose content is plain text, minus injected text that also arrives in that shape (system reminders, agent and session hand-backs, loaded skill bodies, scheduled or loop prompts). Search them with a distinctive phrase from the commit message or plan rather than the symbol name, which mostly matches later sessions pasting the same log. When the session has a transcript-search tool, the same applies to its queries, and hits from the current session and the sessions it started are excluded.
  5. Quote the user's own words when they state a reason.

Transcripts outside the window may hold the answer; say so in 不知道什麼 when the window found nothing.

## 3. Connected doc sources — only when the session has one and something points there

Best at long-form rationale written before the code (a spec, a meeting note) or correspondence about a requirement.

Look at the tools the session actually has, including deferred ones not yet loaded — a notes or wiki connector (Notion, Confluence), a file store (Google Drive), a mail connector (Gmail), an issue tracker other than the repo host. Search each with the feature name, the key symbol, the PR or ticket number, and the author around the commit dates; read whole pages and threads, not titles. If authentication fails, report the class as unreachable; never fill it in.

## 4. Upstream material — only when the reason may lie outside the repo

Best at an outside constraint: a library's behaviour or deprecation, an API limit, a spec, a platform rule.

Signals: the target works around a dependency, pins a version, clamps a value an outside API sets, or cites a URL or an issue in another project. Settle it with one lookup — the one page that answers it (`/read <url>`, the dependency's changelog or issue, a docs lookup tool when the session has one), or, when the claim is about a tool's behaviour, a quick reproduction in a temporary directory outside the repo, removed afterwards. One lookup or one reproduction script per question; this is a check, not a research digest.

## Incident flavour (any class)

When the target is defensive code, add these to each class's search: a revert followed by a re-apply, commit or plan wording such as "outage", "crash", "hotfix", "workaround", a hunt report under `.claude/hunt/`, and transcripts where the user reported the failure.
