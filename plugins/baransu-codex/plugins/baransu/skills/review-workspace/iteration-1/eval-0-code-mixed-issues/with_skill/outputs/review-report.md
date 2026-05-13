# /baransu:review — 審核結果

**Verdict：FAIL**

> 理由簡述：存在兩個 critical 等級的安全缺陷（硬編碼 API key、MD5 密碼雜湊）
> 與兩個 critical 等級的邏輯/契約缺陷（null-crash 違反 docstring、new_user
> 覆寫整個 DB 並與 authenticate 契約不相容）。即使模擬環境略過了 AskUserQuestion，
> 這些 finding 屬「宣稱與實作不符 + 公認 CWE/OWASP 對應」雙重觸發，依 Stage 7
> rubric「critical-severity T3 finding with no accepted fix path」→ FAIL。

---

## Target

- **路徑**：`plugins/baransu/skills/review-workspace/iteration-1/fixtures/user_service.py`
- **Tier**：T2 standard（single file 60 LOC，但涵蓋 auth + secrets + crypto + persistence 四個安全面向，依規則 round up）
- **規模**：60 LOC、1 類別（UserBuilder）+ 4 函式（authenticate / build_user / new_user / UserBuilder.build）、單一模組、無跨層變更
- **檔案性質**：位於 `fixtures/` 資料夾，無對應測試 / 無 `__init__.py` / 無 pytest 設定

---

## 目標宣稱 (Claim Checklist)

1. **宣稱做了**
   - `authenticate(username, password)` 查找使用者並驗證密碼
   - `new_user(name, email)` 建立並持久化一個 user
   - `UserBuilder` 以 fluent API 組成 user dict
   - `build_user(name, email)` 封裝 UserBuilder 的呼叫
2. **宣稱決定**
   - 以 JSON 檔 (`/var/data/users.json`) 為資料存儲
   - 以 MD5 hash 雜湊密碼
   - 以 module-level constant 存放 `API_KEY`
   - 採用 UserBuilder Factory/Fluent Pattern 封裝 user dict 組裝
3. **宣稱達成** — `authenticate` docstring 明示：「returns the user dict on success, None on failure」
4. **宣稱 NOT building** — 無明示 out-of-scope
5. **宣稱 Unknowns** — 無明示
6. **使用者脈絡**（僅用作 review 焦點，非 claim）：擔憂格式 / 安全 / 邏輯 / 過度工程混雜；希望能區分「必修 / 過度設計放掉 / 純 cosmetic」；模組尚無 e2e 測試

---

## 派遣的審核者

- **架構審核（architecture-reviewer）**：啟用 — 觸發規則「target 有新增結構（UserBuilder 類別），使用者擔憂項之一為過度工程」對應 arch rubric「過度抽象 / 未自證的複雜度」
- **品質審核（quality-reviewer）**：啟用 — 觸發規則「target 含可執行程式碼」
- **安全審核（security-reviewer）**：啟用 — 觸發規則「auth / secrets / crypto / persistence / file-path 全部命中」
- **對抗測試（adversarial）**：略過 — T2 tier 且無跨層 / 跨服務變更
- **派遣方式**：正常安裝環境中會以 parallel Task call + isolated context 分派；本次為模擬執行，於 `dispatch-log.md` 有完整記錄

---

## 發現（四級 triage）

### Tier 1 — 已自動修復（format / import / typo / dead import）

> 模擬規則：**不直接修改 target file**；變更以 `auto-fixes.diff` 提交為提案。

| # | 檔案 | 行數 | 動作 | 說明 |
|---|---|---|---|---|
| T1-a | `fixtures/user_service.py` | 6 | 刪除 `import datetime  # unused` | 檔案自承 unused，Grep 確認無其他 reference |
| T1-b | `fixtures/user_service.py` | 7 | 刪除 `import logging  # unused` | 同上 |

Scope 鎖定於 dead-import 移除，無語意變更。完整 diff：`outputs/auto-fixes.diff`。

---

### Tier 2 — 待確認（非語意但超出 T1）

**無**。本次無「僅 rename / collapse constant / 刪 dead code」此類 non-semantic 批次；所有可 Edit 類都在 T1，所有語意類都在 T3。

---

### Tier 3 — 需判斷（模擬環境：AskUserQuestion 已 bypass，以預設選項處理）

> 本次以四題批次方式打包七項 finding。每題後附
> `[SIMULATED: AskUserQuestion bypassed — chose option X because Y]`
> 說明模擬環境下所選的預設答案與理由。真實執行時這些會真的送到
> `AskUserQuestion`、由 user 決定。

#### Q1 — 安全三項（必修）

**包含**：sec-01 hardcoded API key、sec-02 MD5 for password、sec-03 non-constant-time compare

| id | citation | severity | 觀察 | 最小修 |
|---|---|---|---|---|
| sec-01 | `user_service.py:9` | critical | `API_KEY = "sk-live-9f8a7b…"` — `sk-live-` 前綴為 production live-key 慣例；Grep 顯示本檔內 `API_KEY` 完全未被引用（宣告即遺棄），仍進 commit history 即已洩漏 | 改讀 `os.environ["USER_SERVICE_API_KEY"]`；或若實為 fixture，改名 `sk-test-PLACEHOLDER` |
| sec-02 | `user_service.py:44` | critical | MD5 雜湊密碼（CWE-327、OWASP A02:2021）+ 無 salt + 無 work factor；若 `users.json` 以任何方式洩漏（備份 / 檔案權限 / log），密碼可 offline 爆破 | 改用 `bcrypt` / `argon2-cffi` / `hashlib.scrypt`，含 salt 存放；既有資料需 migration 或 next-login rehash 策略 |
| sec-03 | `user_service.py:46` | major | `stored_hash == attempt_hash` 非 constant-time（CWE-208）；Python 遠端 timing 利用困難，屬 defence-in-depth | `import hmac; hmac.compare_digest(stored_hash, attempt_hash)` |

**天平**：sec-01 / sec-02 屬「CWE + OWASP 雙重對應」硬標準，不修的代價遠大於修的成本，無中間方案可繞過。sec-03 一行修復無代價，搭車修掉。

`[SIMULATED: AskUserQuestion bypassed — recommended option = 「三項全修」，
because sec-01 與 sec-02 都是 CWE/OWASP 公認 critical，不存在 legitimate 原設計
意圖；sec-03 為 hmac.compare_digest 一行替換無代價。使用者的擔憂類別「必須修」
完全覆蓋此批次。]`

#### Q2 — 邏輯兩項（必修）

**包含**：qual-01 null-crash、qual-02 new_user 覆寫 DB + 契約斷裂

| id | citation | severity | 觀察 | 最小修 |
|---|---|---|---|---|
| qual-01 | `user_service.py:40-43` | critical | `users.get(username)` 在查無此人時回 None，下一行 `user["password_hash"]` 直接對 None 做 subscript → TypeError。docstring 宣稱「失敗回 None」—— 實作違反自己的 contract。註解自承是 bug | 在 line 41 後補兩行：`if user is None: return None` |
| qual-02 | `user_service.py:56-60` | critical | `new_user` 用 `open(DB_PATH, "w")` + `json.dump(user, f)` 將 **整個** users DB 覆寫為**單一** user dict。`authenticate` 卻期待 `{username: {...}}` mapping → 任何 `new_user` 寫入的資料，`authenticate` 永遠查不到。另：user dict 中根本沒存 `username` 欄位（只有 name/email/role），但 authenticate 以 username 當 key 查找 | 改為 read-modify-write；`users[username] = user`；處理 FileNotFoundError（空 DB 初始化） |

**天平**：qual-01 兩行 fix，無任何代價。qual-02 是核心功能不成立 —— 不是新工作，是修到讓宣稱的功能真的存在。無中間方案。

`[SIMULATED: AskUserQuestion bypassed — recommended option = 「兩項全修」，
because 兩者都是 docstring 宣稱與實作直接矛盾（qual-reviewer 規則 1 核心產出）。
使用者的擔憂類別「必須修」完全覆蓋。]`

#### Q3 — 架構一項（可選簡化）

**包含**：arch-01 UserBuilder 過度抽象

| id | citation | severity | 觀察 | 建議 |
|---|---|---|---|---|
| arch-01 | `user_service.py:13-29` | major | UserBuilder 是 17 行的 Fluent Builder；檔案自述「Only one caller」、實際 Grep 驗證唯一 caller 即 `build_user`（`user_service.py:53`）。單一 consumer 對應 architecture-reviewer 規則 3 的「過度抽象」典型 —— 介面/類別的新增沒有 ≥2 真實 consumer，預留是假的 | **中間方案（推薦）**：刪除 UserBuilder 類別，保留 `build_user` 作為三行 helper — `return {"role": "member", "name": name, "email": email}`。保留語意命名點，移除無 consumer 的 Fluent API |

**天平**：
- 不做：留 17 行無 consumer 的抽象 → 誤導 reader、增加維護面
- 做：刪 ~20 行、閱讀更直接 → 失去「未來若真有多種 user 型態時可延伸」的幻想預留（本 agent 規則：「未來是假的」）
- 中間方案：保留 `build_user` helper，只刪 UserBuilder —— 成本最小、保留抽象名、去掉過度結構

`[SIMULATED: AskUserQuestion bypassed — recommended option = 「採中間方案」，
because 完全刪除會失去 build_user 的語意名；完全保留會違反 arch-reviewer 規則 3
與使用者「過度設計該放掉」的擔憂。中間方案是 balance-passing minimum。]`

#### Q4 — 語意裁斷搭 cosmetic

**包含**：qual-05 file-error handling 的 failure-mode 語意、qual-03 型別標註 cosmetic

| id | citation | severity | 觀察 | 選項 |
|---|---|---|---|---|
| qual-05 | `user_service.py:37, 58` | major | `open(DB_PATH)` 在檔案不存在時拋 `FileNotFoundError`；`json.load` 在 corrupt JSON 時拋 `JSONDecodeError`。兩者皆為「認證失敗」的合理情境，但目前 crash 而非 docstring 承諾的「回 None」| (a) 改 docstring 宣告 IOError 會 raise；(b) 用 try/except 包起來回 None。兩者擇一 |
| qual-03 | `user_service.py:56` | minor | `def new_user(name: str, email: str):` 缺 `-> dict` 標註，與 `authenticate -> Optional[dict]` / `build_user -> dict` 不一致 | 補 `-> dict` |

**天平**：qual-05 是**語意選擇題**（fail-fast vs fail-soft 風格），不是 bug；docstring 與實作對齊即可，方向由 user 決定。qual-03 是純一致性 cosmetic，四字元修改。

`[SIMULATED: AskUserQuestion bypassed — recommended option for qual-05 =
「方案 (a) 改 docstring」因為最小代價、保留 fail-fast 語意 + 與 qual-02
的 read-modify-write 新增的 FileNotFoundError 處理可以協同。qual-03 = 修。
使用者的「哪些只是 cosmetic」類別 = qual-03。]`

---

### Tier 4 — 僅供參考

| id | severity | 內容 |
|---|---|---|
| arch-02 | advisory | 沒有 Repository 抽象是**對的** —— 兩個 call site、同模組、同檔案，新增 storage 抽象會是過度工程。明確回應 user 的「過度工程該放掉」擔憂：此處不抽象也是一項合理決定 |
| sec-04 | advisory | `DB_PATH` 為 module constant，不由 user 輸入構成，無 path-traversal 可利用面；「如果未來被設成外部輸入…」類 FUD 不升級。若確實有外部可配置需求再重審 |
| sec-05 | advisory | `new_user` 無 authz check；但本模組的 threat model 未明示（CLI？內部 service？web endpoint？），security-reviewer 禁忌「威脅建模投射」，留為提醒：caller 層是否已有授權門需 user 確認 |

---

## E2E Gate

**n/a**。`fixtures/` 目錄沒有 `pyproject.toml` / `pytest.ini` / test file / Makefile；baransu 專案根目錄 CLAUDE.md 明示「No build / test / lint commands」。依 Stage 7 rule「test infra absent → verdict 忽略 e2e，註記 n/a」。

> 使用者在 prompt 中提到「這個模組還沒有 e2e 測試」，審核結果不因缺 e2e 而 INCOMPLETE —— 但**強烈建議**：一旦此檔脫離 fixture 身分、進入真的 production module，應即建立 pytest 套件覆蓋 authenticate（已知 / 未知 username、空 DB、corrupt JSON、密碼比對成功 / 失敗）與 new_user（空 DB 初始化、既有 users.json append、key 衝突）。此則為 advisory，不影響本次 verdict。

---

## 結論

此檔在 60 行內同時踩中**兩個 critical 安全缺陷**（硬編碼疑似 live API key、MD5 密碼雜湊無 salt）與**兩個 critical 邏輯缺陷**（null-crash 違反自述 docstring、new_user 覆寫整個 DB 且與 authenticate 契約完全斷裂，等於核心功能不成立）。這些都對應公認 CWE / OWASP 或直接與 target 自己寫下的 docstring 矛盾，完全不在「legitimate 原設計意圖」的保護範圍。**無任何修復路徑被接受的情況下，verdict = FAIL**。

回應使用者的三分類訴求：

- **必須修**（4 項 critical + 1 major + 1 major）：sec-01 hardcoded key、sec-02 MD5、sec-03 constant-time compare、qual-01 null-crash、qual-02 new_user 契約斷裂、qual-05 error handling 對齊 docstring
- **過度設計應放掉**（1 項）：arch-01 UserBuilder 單一 caller — 推薦中間方案，保留 `build_user` helper、刪除 UserBuilder 類別
- **純 cosmetic**（3 項）：T1-a / T1-b 兩個 dead import（已於 diff 提出自動移除），qual-03 `new_user` 缺 `-> dict` 型別標註
- **反向確認**（3 項）：arch-02 / sec-04 / sec-05 三條本次不觸發新工作，留 FYI

修復建議的執行順序：先 Q2 邏輯兩項（讓核心功能真的能跑）→ Q1 安全三項（讓存放結果安全）→ Q3 UserBuilder 中間方案（讓讀碼不被干擾）→ Q4 + T1 收斂 cosmetic。

---

## 模擬執行註記

- 本次為 baransu:review 的 eval 模擬，無 live user；所有 AskUserQuestion 均以 `[SIMULATED: ...]` 標記其所選預設。
- Target 檔案**未被實際修改**；Tier 1 auto-fix 以 `outputs/auto-fixes.diff` 提案。
- 三位 reviewer 為 isolated-lens 模擬（無真 Task-dispatch subagent tool 可用），以逐 agent 的 .md 當作唯一視角 re-read target 的方式分別產 finding，保持 perspective 邊界。詳見 `outputs/dispatch-log.md` 與 `outputs/raw-findings.md`。
