# /grade Cron registration runbook

The harness's daily loop kicks off with `/baransu:grade` at midnight. This document covers both registration paths: session-scoped via Claude Code's `CronCreate` primitive, and persistent via OS-level cron / systemd. Pick one based on lifecycle requirement.

## Time slot

Use `00:03` instead of `00:00`. The "Avoid :00 and :30" guidance from CronCreate prevents thundering-herd at the API; OS-level cron has the same advice for shared workstations. Cron expression: `3 0 * * *` (minute=3, hour=0, every day).

## Path A — CronCreate (session-scoped, durable)

In the Claude Code REPL, register:

```
CronCreate(
  cron: "3 0 * * *",
  prompt: "/baransu:grade",
  durable: true,
  recurring: true
)
```

Caveats:
- Recurring durable jobs persist to `.claude/scheduled_tasks.json` BUT auto-expire after **7 days** of recurring fires (i.e. each recurring CronCreate entry expires in 7 days).
- Jobs only fire while the Claude REPL is idle (mid-query → fires after current query completes).
- Re-register every 7 days within an active Claude session, OR migrate to Path B for true persistence.

Verify:

```
CronList
```

Should show one entry with `cron: "3 0 * * *"` and `prompt: "/baransu:grade"`.

Unregister:

```
CronDelete(id: <returned-id>)
```

## Path B — OS-level cron (persistent)

For production / unattended hosts, use OS cron:

```bash
crontab -e
# Add line:
3 0 * * * cd /home/vakarve/project/clis/baransu && claude -p "/baransu:grade" >> .claude/harness/cron.log 2>&1
```

This requires `claude` CLI installed and able to run headless (`-p` flag for prompt mode).

To unregister, run `crontab -e` again and delete the line.

Alternative: systemd timer:

```
# /etc/systemd/system/baransu-grade.timer
[Timer]
OnCalendar=*-*-* 00:03:00
Persistent=true

[Install]
WantedBy=timers.target

# /etc/systemd/system/baransu-grade.service
[Service]
ExecStart=/path/to/claude -p "/baransu:grade"
WorkingDirectory=/home/vakarve/project/clis/baransu
```

Enable:
```bash
systemctl --user enable --now baransu-grade.timer
```

Disable:
```bash
systemctl --user disable --now baransu-grade.timer
```

## /grade vs /bridge

`/grade` runs unattended via cron. `/bridge` is **manual-only** and never registered with cron — it's a comparison tool the operator runs explicitly with target branch + corpus size. Do NOT register `/baransu:bridge` via CronCreate or OS cron; the per-run report and trust check assume operator presence.

`/grade` does NOT require the `--allow-untrusted` flag (that flag belongs to `/baransu:bridge` for replaying corpus against an untrusted target branch). The cron-fired `/baransu:grade` invocation is plain — no flag suffix needed.

## Operational schedule

- 00:03 daily — `/baransu:grade` chains to `/baransu:triage` and auto-fix sub-flow per the SKILL.md flow.
- Manual `/baransu:grade --tune-acknowledged` after rubric review (≥ 50 completed rows trigger).
- Manual `/baransu:bridge <target_branch> [--corpus-size N] [--allow-untrusted]` for skill version comparison.
