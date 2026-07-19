# 實驗執行記錄（主迴圈維護）

分支點：bfa0f46。9 worktrees under `.claude/worktrees/exp-{p1,p2,p3}-{f,os,fos}`。
每 arm 循序執行（一次一個 workflow），主迴圈在 arm 執行期間保持閒置，
使 workflow 內 `budget.spent()` 差值 ≈ 該 arm 的 token 成本。

| arm | 啟動 (unix) | 結束 (unix) | wall 秒 | tokens (workflow delta) | agents | 備註 |
|-----|------------|------------|---------|------------------------|--------|------|
| p1-f | 1784428341 | — | 952 (workflow duration) | 70,644 output / 154,995 subagent 總計 | 1 | 自報 21/21+A7 bonus，48→69 tests，工具呼叫 65 次 |
| p1-o (bonus) | 1784429385 | — | 1472 | 94,162 output / 196,982 subagent 總計 | 1 | 原定 p1-os；workflow 巢狀環境無 Agent 工具，Opus 無法委派 Sonnet，單刷完成 → 重新歸類為「Opus 單體」bonus 格。自報 21/21+A7，48→68 tests，工具 83 次。branch exp/p1-os |

| p1-os | 1784430957 | — | 1558 | 99,777 output / 433,701 subagent 總計 | 5 (opus plan + 3×sonnet + opus integrate) | 腳本代派工成功。自報 21/21+A7，48→66 tests，工具 126 次。branch exp/p1-os2 |
| p1-fos | 1784432571 | — | 1627 | 100,814 output / 468,969 subagent 總計 | 5 (fable plan + 2×sonnet + opus review + fable integrate) | 自報 21/21+A7，48→74 tests（最多），opus reviewer 做了真突變測試零缺陷，工具 137 次 |

| p2-f | 1784434262 | — | 1514 | 104,714 output / 329,085 subagent 總計 | 2 (fable spec + fable impl) | 自報 21/21+A7，48→77 tests（新高），spec 發現 brief 的警告基線誤植（實為 3 非 2），工具 84 次 |

| p2-os | 1784435809 | — | 1776 | 110,414 output / 325,338 subagent 總計 | 2 (opus spec + sonnet impl) | 自報 21/21+A7，76 tests；單一大 commit（含 spec+.exp，紀律較差）；基線測試數自報錯誤（~60 實為 48），工具 113 次 |

| p2-fos | 1784437617 | — | 1937 | 124,525 output / 480,592 subagent 總計 | 3 (fable spec + sonnet impl + opus review) | 自報 21/21+A7，48→91 tests（最多），opus 審查零缺陷零 fix；spec 146K/impl 207K/review 126K tokens |

| p3-f | 1784439656 | — | 3114 | 184,760 output / 652,847 subagent 總計 | 8 (fable：spec+3×impl+3×review+final) | 三 task 全一次過（advisory）、needs_fixer=false、84 tests；review 抓到 C4 lazy-parse 未釘死等 advisory 級發現；工具 228 次 |

| p3-os | 1784442834 | — | 2976 | 180,699 output / 612,472 subagent 總計 | 8 (opus spec + 3×sonnet impl + 3×opus review + opus final) | 三 task 一次過、needs_fixer=false、79 tests；⚠️ review-b 抓到 idx+1 顯示衝突（非稠密 idx 陷阱）但判 advisory 放行——潛在存活缺陷；工具 215 次 |

| p3-fos | 1784445864 | — | 4515 | 281,777 output / 808,667 subagent 總計 | 10 (fable spec + sonnet impl×4 + opus review×4 + fable final)| task b 經歷全實驗唯一一次打槍重派（第一輪 packaged confirm → 第二輪修掉 idx+1 顯示缺陷）；84 tests、needs_fixer=false；工具 302 次 |

**關鍵對照**：p3-os 與 p3-fos 同為 sonnet 實作 + opus 審查，同一 idx+1 缺陷 — p3-os 判 advisory 放行、
p3-fos 打槍重派修掉。差異源頭疑為 spec/ctx 作者（opus vs fable）把驗收條件釘死的程度。

## 金錢成本（output-token 下限估算；牌價：fable $50 / opus $25 / sonnet 促銷 $10 per MTok）

| arm | agents | 總 tokens | 成本 USD |
|-----|--------|-----------|----------|
| p1-f | 1 | 154,995 | $7.75 |
| p1-o (bonus) | 1 | 196,982 | $4.92 |
| p1-os | 5 | 433,701 | $6.81 |
| p1-fos | 5 | 468,969 | $12.07 |
| p2-f | 2 | 329,085 | $16.45 |
| p2-os | 2 | 325,338 | $5.35 |
| p2-fos | 3 | 480,592 | $12.58 |
| p3-f | 8 | 652,847 | $32.64 |
| p3-os | 8 | 612,472 | $11.84 |
| p3-fos | 10 | 808,667 | $20.92 |
| **合計** | 45 | 4.46M | **$131.34** |

方法備註：僅計 subagent output tokens（per-agent model×tokens 由 workflow 狀態檔提取）；
input 端以 cache-read 為主故略去，屬下限估算但跨 arm 方法一致、可相對比較。
Sonnet 5 促銷價至 2026-08-31（正式 $15 時 sonnet 實作 arm 成本 ×1.5）。

## 驗證輪（改革條款 R1–R9 / 一頁合約假說；基線同 bfa0f46）

| arm | 啟動 (unix) | wall 秒 | tokens | agents | 備註 |
|-----|------------|---------|--------|--------|------|
| p2-os′ | 1784455004 | 1878 | 181,904 output / 310,584 總計 | 2 (opus 改革規格 + sonnet impl) | 規格實現 R1–R5：訊息格式零數字欄位、鏡像測試不算釘死、Verbatim Constants；impl 70 tests 含雙 UI 真路徑釘死，自抓一個 FoldedHit 預選回歸。自報全數達標 |

驗證輪成本（同法：per-agent output tokens × 牌價下限估算）：
| arm | 成本 USD | 明細 | 對照 |
|-----|----------|------|------|
| p2-os′ | **$5.01** | opus 126k + sonnet 183k | vs 原 p2-os $5.35（幾乎同價，條文品質換代免費）；vs 冠軍 p3-f $32.64 的 15% |
| p3-os′ | **$19.29** | 10 agents（spec 149k opus；task c 打槍重派 ×1；final 111k opus） | vs 原 p3-os $11.84（+63%，買到：1 次真打槍、全樹常數 diff、真路徑釘死）；vs p3-f $32.64 的 59% |

p3-os′ 過程紀錄：69.6 分、1.056M tokens、task c 第一輪被 R6 任務書以 packaged confirm 拒收後重派修正
（原 p3-os 同型缺陷被 advisory 放行——R7 的牙齒實測長出）；final 四段全過、needs_fixer=false、82 tests。

**異常記錄**：workflow 內生成的 agent（含 agentType general-purpose）不能再生 subagent。
P1 組合 arm 改用「腳本代派工」機制：lead 產出結構化派工單（自訂拆分、1-3 工人）→
腳本照單生成 worker → lead 整合審查。p1-os 於新 worktree exp-p1-os2（branch exp/p1-os2）重跑。
| p-min | 1784461242 | 2120 | 136,006 output / 413,527 總計 | 3 (opus 合約 35 行 + sonnet impl + opus seal) | **$7.27**（opus 89k+119k、sonnet 204k）。seal 突變抽查抓到 CLI println 未釘表面→直接修正＋補 2 釘死測試（65f0b20），81 tests；regex 含节/節 byte-diff 乾淨 |

驗證輪盲評映射（評審不可見）：ARM-11=p3-os′(exp2/p3os)、ARM-12=p-min(exp2/pmin)、ARM-13=p2-os′(exp2/p2os)

## 驗證輪盲評判決（解盲，09-validation-verdicts.json 存全文）

| arm | 釘死/20 | 未釘(行為對) | unmet | 引入 med/high | arch | 測試有效(突變) | 成本 |
|-----|---------|--------------|-------|----------------|------|----------------|------|
| **p3-os′** | **20 全釘** | 0 | 0 | **0** | **9.5** | **9.5（6/6 全殺）** | $19.29 |
| p-min | 18 | 2（B6/C4 接線深度） | 0 | 0 | 9 | 9 | $7.27 |
| p2-os′ | 18 | 1（C4） | 1（A7 bonus 主動除外） | 0 | 9 | 7（5/8；優先序 fixture 不夠辨別） | $5.01 |

事前預測結算（07 號文件）：
1. 「p3-os′ ≥ 20、0 bug」→ **完全命中**。原墊底（17 釘、1 high+1 med）翻身至冠軍同級，
   test_eff 9.5 還高於 p3-f 的 9，成本 59%。改革成功判準達成。
2. 「p2-os′ 19–21、0 bug、未釘表面可能存活」→ 大致命中（0 bug；未釘存活如預測；
   A7 為規格主動除外扣 1）。
3. 「p-min 20±1、0 bug、成本 ≤40%」→ 行為面命中（20/20 met、0 bug、22% 成本），
   釘死深度 18（殘餘缺口=handler→helper 呼叫點耦合，與 seal 自報一致）。
4. 反向風險（一頁塞不下）→ 未發生於此任務規模。

**跨三 arm 的類別滅絕證據**：idx+1 章數缺陷 0 出現（第一輪 5/10）；常數轉抄缺陷 0 出現
（三 arm regex byte-diff 全乾淨，含节/節）。R1/R2/R3 對這兩個錯誤類別是結構性消滅。
共同殘留：pre-existing reader.rs idx-vs-position 缺陷三位評審全數再度標記（backlog 首位不變）。
