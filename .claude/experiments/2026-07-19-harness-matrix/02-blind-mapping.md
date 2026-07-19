# 盲評代號映射（評審不可見；報告解盲用）

| 盲評代號 | arm | branch |
|----------|-----|--------|
| ARM-1 | p2-os | exp/p2-os |
| ARM-2 | p1-f | exp/p1-f |
| ARM-3 | p3-fos | exp/p3-fos |
| ARM-4 | p1-o（bonus，Opus 單體） | exp/p1-os |
| ARM-5 | p2-fos | exp/p2-fos |
| ARM-6 | p3-f | exp/p3-f |
| ARM-7 | p1-os（真組合，腳本代派工） | exp/p1-os2 |
| ARM-8 | p2-f | exp/p2-f |
| ARM-9 | p1-fos | exp/p1-fos |
| ARM-10 | p3-os | exp/p3-os |

副本內容 = `git archive <branch>` 減去 `.exp/`、`.claude/`、`EXPERIMENT-BRIEF.md`、`.gitignore` 外加
hardlink 的 target/ 快取。評審收到：副本目錄 + 一份共用 brief 副本（驗收標準）+ CLAUDE.md（副本內建）。
評審不知道模型軸與流程軸的存在，只按四維評分。
