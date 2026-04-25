# Task Map

| Task Tool ID | Group | Task ID | Impl-Checklist | Notes |
|-------------|-------|---------|----------------|-------|
| task_at_01 | agents-tdaid | TASK-agents-tdaid-01 | impl-checklist-agents-tdaid.md | |
| task_at_02 | agents-tdaid | TASK-agents-tdaid-02 | impl-checklist-agents-tdaid.md | |
| task_at_03 | agents-tdaid | TASK-agents-tdaid-03 | impl-checklist-agents-tdaid.md | |
| task_at_04 | agents-tdaid | TASK-agents-tdaid-04 | impl-checklist-agents-tdaid.md | |
| task_ac_01 | agents-completion | TASK-agents-completion-01 | impl-checklist-agents-completion.md | |
| task_ac_02 | agents-completion | TASK-agents-completion-02 | impl-checklist-agents-completion.md | |
| task_ac_03 | agents-completion | TASK-agents-completion-03 | impl-checklist-agents-completion.md | |
| task_ac_04 | agents-completion | TASK-agents-completion-04 | impl-checklist-agents-completion.md | |
| task_se_01 | skill-execute | TASK-skill-execute-01 | impl-checklist-skill-execute.md | |
| task_se_02 | skill-execute | TASK-skill-execute-02 | impl-checklist-skill-execute.md | |
| task_se_03 | skill-execute | TASK-skill-execute-03 | impl-checklist-skill-execute.md | |
| task_pm_01 | plugin-meta | TASK-plugin-meta-01 | impl-checklist-plugin-meta.md | |
| task_pm_02 | plugin-meta | TASK-plugin-meta-02 | impl-checklist-plugin-meta.md | |

## Pre-scan Notes

agents-tdaid と agents-completion 各自建立獨立的 `agents/*.md` 文件，無檔案交集。可安全並行執行。
skill-execute 前置群組：agents-tdaid, agents-completion（Level 2，待兩個並行群組完成後執行）。
plugin-meta 前置群組：skill-execute（Level 3，最後執行）。
