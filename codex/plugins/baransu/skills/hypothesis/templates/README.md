<!-- Template: .codex/hypothesis/<area>/README.md — the human page. Every fact a reader skill needs is also in hypothesis.json; this page is for a person reading cold. Section headings below are fixed (Traditional Chinese, user-facing). -->

# 假說：{title}

> 狀態以這行指令為準，不以本頁為準：`python3 <hypothesis skill>/scripts/hypothesis-status.py --area {area}`

## 一句話

<!-- fill: What part of the system this is about and what must never happen, in one sentence. -->

## 規則

<!-- fill: Table: id, kind (安全／活性／目標), plain sentence, citation, verdict at publish. Rendered from `hypothesis.json` `rules` and `goals`. -->

## 找到的問題

<!-- fill: One block per path P<n>, plain layer first (the summary and the harm in everyday words, none of 活性、安全性、精化、不變式、同步點、TLC、模型、狀態空間), then 細節: link to `paths/P<n>.md`, and the diagram number where it is drawn. For documents: grouped under 矛盾 / 缺漏 / 模糊（要問誰）. -->

## 圖

<!-- fill: Link to `diagrams.html` and one line per diagram saying which part it adds. -->

## 範圍

<!-- fill: Bounds, assumptions, what is left out; the sentence 「窮舉的結論只在這個範圍內成立」. -->

## 怎麼檢查的

<!-- fill: Tool and version and why this tool; the one command; states explored and time; seen failing (which variant, which rule caught it); seen succeeding (which goal, which transition removed). -->

## 對應表

<!-- fill: Model part → `file:line` (or quote + location). Same content as `model_map`. -->

## 沒有形式化的部分

<!-- fill: One row per reason record, all four fields. When there are none, the affirmative line 「全部形式化，沒有例外。」 — silence is not allowed. -->

## 同步點

<!-- fill: Commit (code) or version + hash (document), generation, and the date of publish; 「涵蓋的檔案改過，本頁結論就失效，以指令輸出為準」. -->
