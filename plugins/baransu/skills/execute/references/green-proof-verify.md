# Pre-SWITCH guard — verify green_proof

Invoked from SKILL.md §4b Phase 3, before the review-tier SWITCH. 「下方 SWITCH」
in this file refers to that SWITCH in SKILL.md §4b Phase 3. Content moved
verbatim from SKILL.md; semantics unchanged.

**Pre-SWITCH guard — verify green_proof**: 在進入下方 SWITCH、`mark task ✅` 之前，主 skill
必須先 verify review-agent 回報的 `green_proof` 欄位符合 `agents/review-agent.md` §3 的 5-tier
必填矩陣。verify 規則：

```
verify_green_proof(review_result):
  # Step 1 — existence check applies to ALL tiers (including direct fix).
  # 4 keys 必須在 schema 中存在（值的語義由 tier 決定，但 key 本身不可省）。
  REQUIRE green_proof.test_command          key present
  REQUIRE green_proof.exit_code             key present (value 為整數)
  REQUIRE green_proof.output_tail           key present
  REQUIRE green_proof.tests_correspondence  key present
  IF any REQUIRE fails:
    return FAIL, reason="green_proof key missing"

  # Step 2 — tier-specific value check.
  IF review_result.tier == "direct fix":
    # direct-fix tier 允許 4 個 value 為 "n/a"/0/""/"n/a"；不再驗 value 內容
    return PASS
  ELSE:
    # advisory / packaged confirm (quality|correctness) / needs judgment 必填實 test
    REQUIRE green_proof.test_command          non-empty AND != "n/a"
    REQUIRE green_proof.tests_correspondence  non-empty AND != "n/a"
    REQUIRE green_proof.exit_code == 0        # else Green failed, not a passed review
    REQUIRE green_proof.output_tail           non-empty
    IF any REQUIRE fails:
      return FAIL, reason="green_proof incomplete or exit_code != 0"
    return PASS
```

verify 結果處理：
- `PASS` → 進入下方 SWITCH，照原邏輯 routing。
- `FAIL` → review 視為失敗：**直接跳過 Goal-Alignment Filter**（因 verify-fail 注入的
  finding 是 process-level、既不對應 task 驗收標準也不對應 task 目標，若送入 filter 會被
  誤判為 off-goal observation 而 downgrade 至 advisory，導致 task 在無實 test 證據下被
  mark ✅；此漏洞由本段顯式處理）。直接走以下路徑：
    1. `failure_count += 1`（verify-fail 計入 task-level failure_count，與 §4b Phase 2
       的 compile-error 排除規則不同——compile error 走 `compile_error_count`、不計入；
       verify-fail 是 review-stage 的 process 失敗、計入 failure_count）。
    2. 附加 finding `{citation: "green_proof", observation: "<verify reason>", fix:
       "重派 review-agent 並要求附完整 green_proof"}` 到 review_result.findings。
    3. 重派 impl-agent + review-agent（接 §4b Phase 2 retry 邏輯：第 1 次重試直接
       重派；第 2 次失敗觸發 smart-friend 補上 correction_strategy）。
    4. 不進下方 SWITCH，本輪 Phase 3 結束。
