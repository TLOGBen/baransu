# traps — 這個形狀會怎麼壞

## 讀的那一側

1. **讀者繞過腳本，直接讀 README 或 `hypothesis.json` 的 `verdict_at_sync`。** 這是整個形狀要防的事，結構只防得住一半：腳本會藏結論，但檔案裡的字還在。對策：欄位名叫 `verdict_at_sync` 不叫 `verdict`；README 第一行寫「狀態以指令為準」；`reading.md` 寫明讀者不開這兩個檔；`/review` 的 principle 只引用腳本輸出。殘留風險：模型自己好奇打開檔案。可以加 `verify-skills.py` 一條：讀者 skill 的文字裡不得出現 `hypothesis.json`（只有 `hypothesis/` 自己可以）。
2. **腳本跑不起來被當成「沒有假說」。** `python3` 不在 PATH、Windows 只有 `python`、CRLF 換行的 shebang。讀者把 exit 非 0／10 都當 `broken`，但如果讀者寫成「沒輸出 → 沒涵蓋」就破功。`reading.md` 已寫死「腳本失敗 = broken」；在 Windows 的呼叫寫法（`python` vs `python3`）要在實作時決定，最好由腳本自己有一個 `.cmd`／判斷式包裝。
3. **`--diff <base>` 的 base 選錯。** review 用 `main`、紅綠用任務起點；選太新會漏掉改動（但雜湊判定不受 base 影響——base 只決定「哪些 area 被列出」）。漏列的 area 不會被說成通過，只是沒被問到。`--all` 是保險。
4. **過期太常發生，讀者開始習慣性忽略 `stale`。** 檔案層級的粗顆粒加上「改涵蓋檔就過期」，在熱門檔案上每次改動都要 `--maintain`。如果 `no-effect` 那一步不夠便宜（重跑 TLC 秒級，但 agent 讀 diff 要 token），使用者會嫌煩。量測點：試行時記錄每次 `--maintain` 的花費與 `no-effect` 的比例。
5. **新寫入者的 regex 漏抓。** 寫入用 ORM（`update({status})`）、反射、SQL 字串、別的語言；或 regex 太寬，每次都報 `new-writer`。漏抓 = 回到沒有 watch 的程度；太寬 = 第 4 條的疲勞。`--maintain` 處理 `new-writer` 時應順便修 regex。
6. **CRLF 正規化以外的「同內容不同位元組」**：BOM、編碼轉換、格式化工具重排。會造成假的 `stale`，方向是安全的，但會加劇第 4 條。
7. **文件在 repo 外或在別台機器。** 絕對路徑在另一台機器上永遠 `missing` → `stale`。對策：寫假說時建議把原檔放進 repo；放不進時 README 要寫明「只在這台機器能判定」。

## 寫的那一側

8. **`sync.files` 和實際引用不一致。** 引用了 `pay.ts:41` 卻沒把 `pay.ts` 放進 `sync.files`，那個檔案改了也不會過期。對策：`sync.files` 由 publish 步驟從 `model_map` 與 `rules[].cites` 機械地產生，不手填；腳本讀時也比對兩者，引用了卻不在 `sync.files` → `draft`（已寫進 `compute_state` 第 5 步）。
9. **CAS 的比較與換檔之間仍有窗口。** 兩個 session 在同一毫秒 publish，後者可能蓋掉前者。結果方向仍是 `draft`（artifact 雜湊對不上），但如果兩者寫出相同雜湊的不同結論——不可能，結論在同一個檔案裡。殘留：前者的 history 列會遺失一筆。
10. **撰寫者把雜湊算在「改壞的副本」上。** broken variant 若不是在暫存副本而是在工作目錄做，忘了還原就 publish，雜湊對上的是壞掉的程式。對策：變體只存成 patch 並在系統暫存目錄套用；publish 前檢查工作目錄的涵蓋檔沒有未說明的差異。
11. **模型沒變但程式語意變了，`--maintain` 誤判 `no-effect`。** 這是判斷題，只有一個主人，但主人也會錯。讀者端無法察覺。緩解只有「重跑前後各一次」與「看過它失敗」；`no-effect` 時不重新推導 variant 是成本上的取捨，在試行中觀察誤判率。
12. **舊位置搬家半途。** `git mv` 了、還沒 publish 就停 → 舊位置已空，新位置是沒有 `hypothesis.json` 的 `draft`。方向安全（不會通過）。我原本想改成「先複製、發佈後才刪舊的」，但計畫已定「同一個區塊在任何時刻只能存在一處」（生命週期模擬路徑 ④：新舊並存時有人去讀沒人管的那份），而且舊檢查本來就不能拿來宣告完成，搬家半途並沒有讓誰失去一個能用的「通過」。所以保留整個移動；殘留風險只有「要再跑一次 `--maintain`」。

## 跟其他 skill 的接面

13. **`/review` 永遠不寫，但 `stale` 時「需要 `/hypothesis --maintain`」若被 review 自己去做，就破了「只讀」。** 表上寫的是回報，不是執行；`review/SKILL.md:39` 結構上擋住。
14. **紅綠綠燈在 loop／無人模式下遇到 `stale`。** 讀者會自動叫 `--maintain`；`--maintain` 是 `assisted`，只在「承諾是刻意改的」停下來要證據。停點的預設值第二片才定；在那之前它回報「卡住」並列出問題，綠燈維持紅。風險是停點被誤設成「預設當作沒有影響」——那會讓過期變成假的通過，`loop-pauses.md` 必須把這個停點標成不能預設放行（跟 Authorization PAUSE 一樣）。
15. **Codex 鏡像的 `$CLAUDE_SKILL_DIR`。** 讀者指令依賴這個變數解析到 `../hypothesis/scripts/`；Codex 的對應機制要在鏡像時查證（`/codex-skill-transfer`）。腳本本身是純 stdlib，Codex 可以跑。
16. **`/ship` 把 `hypothesis/` 歸檔掉。** ship 的歸檔清單是白名單，新目錄預設不會被歸檔；但「never archived」那段文字要加上 `hypothesis/`，否則日後有人「補齊」白名單時會誤加。
17. **觸發後才發現沒有 Java／TLC。** 結果應是 `unformalized`／`no-tool` 加一筆原因紀錄，而不是半套 area 留在 `draft`。對策（已寫進 SKILL.md §1）：先檢查工具在不在，再開 area 目錄。
