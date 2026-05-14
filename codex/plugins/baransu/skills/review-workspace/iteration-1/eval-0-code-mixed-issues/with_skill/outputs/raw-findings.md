# Raw Reviewer Findings

Findings as emitted by each isolated perspective reviewer, before Stage 6
consolidation / de-duplication / tier assignment. Kept verbatim for audit.

---

## architecture-reviewer

### arch-01-userbuilder-over-abstraction
- severity: major
- citation: fixtures/user_service.py:13-29
- claim_violated: "以 UserBuilder Factory Pattern 包 dict 組裝" (decision claim)
- observation: UserBuilder 是 Fluent Builder，但 docstring 自述 "Only one caller
  in this codebase" (line 14)、且 build_user (line 51-53) 是其唯一 caller。
  單一 consumer 就是「過度抽象」規則定義的典型情況 —— 介面/類別的新增沒有
  兩個以上真實 consumer，預留是假的。此處
  `{"role": default, "name": name, "email": email}` 三行 dict literal 即可完成。
- suggested_fix: 把 build_user 內聯為
  `{"role": "member", "name": name, "email": email}` 直接回傳，刪除
  UserBuilder 類別。new_user 亦無需 build_user 中介，可直接組 dict。
- balance_note:
  - 不做：保留 17 行 UserBuilder + 一層 build_user 間接 → 增加閱讀成本、
    誤導未來 reader 以為有多個 user-shape
  - 做：刪除約 20 行、讀碼更直接；失去的是「未來若真有多種 user 型態時
    可延伸」的幻想預留
  - 中間方案：保留 build_user 作為 helper function (3 行)，只刪 UserBuilder
    類別本身 —— 保留 "create user dict" 的命名點，去掉無 consumer 的 Fluent API
  建議採中間方案。

### arch-02-no-persistence-abstraction-but-fine
- severity: advisory
- citation: fixtures/user_service.py:37, 58
- claim_violated: none
- observation: authenticate 和 new_user 直接 open(DB_PATH) 讀寫 JSON，
  沒有 repository/storage abstraction 層。本視角**不建議**新增抽象：只有
  兩個 call site、都是同一個檔案、同一個模組 —— 新增 Repository 就是本 agent
  規則 3 明令禁止的「過度抽象」。
- suggested_fix: none — advisory only. 呼應 user 的「過度工程該放掉」擔憂，
  明示「此處不抽象」也是一項正確決定。
- balance_note: N/A — not a new-work proposal.

---

## quality-reviewer

### qual-01-null-crash-on-unknown-user
- severity: critical
- citation: fixtures/user_service.py:40-43
- claim_violated: "authenticate: returns the user dict on success, None on failure"
  (line 35 docstring)
- observation: users.get(username) 在 username 不存在時回 None，緊接著 line 43
  user["password_hash"] 對 None 做 subscript，拋 TypeError。程式碼內的
  註解 (line 41-42) 自承這是 bug。實際執行結果：失敗時不是回 None，而是
  crash —— 直接違反 docstring 宣稱。
- suggested_fix: 在 line 41 後加：
  `if user is None: return None`
- balance_note:
  - 不做：docstring 成謊言、任何未註冊 username 直接 stacktrace
  - 做：兩行新 code、一個 branch；無 UX 或效能代價
  - 中間方案：無必要（fix 已是最小）
  必須修。

### qual-02-new_user-overwrites-entire-db
- severity: critical
- citation: fixtures/user_service.py:56-60
- claim_violated: "new_user: 建立並持久化一個 user" (docstring 隱含意圖)
- observation: open(DB_PATH, "w") + json.dump(user, f) 將整個 users.json
  用單一 user dict 覆寫 —— 所有既有使用者被抹除，且新寫入的結構是 flat dict
  而非原本 {username: {...}} 的 mapping，下次 authenticate 的 users.get(username)
  必定 miss。這是 authenticate/new_user 雙方的契約完全不相容。
  另：此函式原本 signature 也缺 username 欄位 —— build_user 只寫 name/email/role，
  無 username key，authenticate 卻以 username 當 lookup key。contract 斷裂。
- suggested_fix: read-modify-write：
  ```
  try:
      with open(DB_PATH) as f:
          users = json.load(f)
  except FileNotFoundError:
      users = {}
  users[name] = user   # 或 username 欄位統一
  with open(DB_PATH, "w") as f:
      json.dump(users, f)
  ```
- balance_note:
  - 不做：new_user 每呼叫一次等於重置整個 user DB；authenticate 對任何 new_user
    寫入的 user 都查不到。核心功能完全壞掉
  - 做：read-modify-write 約 5 行，需處理空 DB 的 FileNotFoundError
  - 中間方案：無 —— 這不是新工作，是已宣稱功能不成立的修復
  必須修。

### qual-03-new_user-no-return-type-annotation
- severity: minor
- citation: fixtures/user_service.py:56
- claim_violated: none
- observation: def new_user(name: str, email: str): 缺 -> dict 回傳型別標註，
  與同檔案其他函式不一致（authenticate -> Optional[dict]、build_user -> dict）。
- suggested_fix: 補 -> dict。
- balance_note: cosmetic，一致性微改；無成本。

### qual-04-unused-imports-dead-import
- severity: minor
- citation: fixtures/user_service.py:6-7
- claim_violated: none
- observation: import datetime (line 6) 和 import logging (line 7) 兩行
  comment 自承 unused，且 Grep 該檔案 datetime、logging 無其他 reference。
- suggested_fix: 刪除這兩行 import。
- balance_note: N/A — Tier 1 範疇（dead import），不需天平。

### qual-05-no-file-error-handling
- severity: major
- citation: fixtures/user_service.py:37, 58
- claim_violated: "authenticate: 成功回傳 user dict，失敗回傳 None"
- observation: open(DB_PATH) 在 DB_PATH 不存在時拋 FileNotFoundError；
  json.load 在 corrupt JSON 時拋 JSONDecodeError。兩者皆為「認證失敗」
  的合理情境但目前會 crash，而非 docstring 承諾的「回 None」。
- suggested_fix: user 裁斷：(a) 修 docstring 明示 IOError 會 raise，
  或 (b) 用 try/except 包起來回 None。
- balance_note:
  - 不做：docstring 與實作對 failure mode 不一致
  - 做：或改 docstring (1 行) 或加 try/except (4-5 行)
  - 中間方案：兩者擇一即可
  T3 —— 需 user 判斷語意。

---

## security-reviewer

### sec-01-hardcoded-api-key
- severity: critical
- citation: fixtures/user_service.py:9
- claim_violated: none explicit — 規則 2「硬編碼秘密」典型案例
- observation: API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c"
  —— 前綴 sk-live- 為 live-mode API key 慣例（Stripe/OpenAI 等），後續 32
  位 hex 與真實金鑰模式相符。本檔在 fixtures/ 目錄 —— 可能為測試用假資料 ——
  但 sk-live- 前綴是明確 production 暗示，不像 placeholder (sk-test-*、
  xxx-REDACTED)。Grep 本檔內 API_KEY 無任何 reference — 屬「宣告但未使用」
  的硬編碼秘密；只要進 commit history 就等於洩漏。
- suggested_fix:
  - 若為真 key → 從 repo 歷史移除（git filter-repo / BFG）+ rotate key
  - 改為 API_KEY = os.environ["USER_SERVICE_API_KEY"]
  - 若只是 fixture → 改成明顯 placeholder："sk-test-PLACEHOLDER"
- balance_note:
  - 不做：若為真 key → 已洩漏；若為假 key → 誤導下游 reader / 靜態掃描誤報
  - 做：一行改動 + (若真) key rotation 工作
  - 中間方案：若確為 fixture → 改名 PLACEHOLDER 即可（最便宜）
  必須修；user 需確認是否為真 key。

### sec-02-md5-for-password
- severity: critical
- citation: fixtures/user_service.py:44
- claim_violated: none explicit — 違反規則 5，對應 CWE-327 + OWASP A02:2021
- observation: hashlib.md5(password.encode()).hexdigest() 用 MD5 雜湊密碼：
  (a) MD5 已 cryptographically broken（CWE-327 collision）
  (b) 未加 salt → rainbow table 攻擊 trivial
  (c) 無 work factor → GPU 爆破極快
  具體可利用路徑：若 users.json 被讀到（檔案權限 / 備份 / log 洩漏），
  攻擊者可 offline 爆破密碼。
- suggested_fix: 改用 bcrypt / argon2-cffi / hashlib.scrypt。存儲格式需同步
  升級（salt + hash 一起存），既有 users.json 需 migration 或「next-login
  rehash」策略。
- balance_note:
  - 不做：任何 DB 洩漏 → 密碼全破
  - 做：加 dependency + 改 hash 產生/比對兩處 + migration
  - 中間方案：無 —— MD5 無任何脈絡下適用於密碼
  必須修；修復涉及存儲格式變更，需 user 批准實作路徑。

### sec-03-password-compare-non-constant-time
- severity: major
- citation: fixtures/user_service.py:46
- claim_violated: none explicit — 違反規則 5 + CWE-208
- observation: if stored_hash == attempt_hash: 用 Python == 比對，
  非 constant-time；對 attacker-controlled timing probe 弱。
  實務上 Python 遠端 timing 利用困難 → defence-in-depth 而非直接 exploit。
- suggested_fix: import hmac; 改為 hmac.compare_digest(stored_hash, attempt_hash)。
- balance_note:
  - 不做：理論 timing 風險
  - 做：import + 1 行替換
  - 中間方案：無
  一行修復、無代價 → 應修。排序在 sec-02 之後。

### sec-04-path-not-user-controlled-advisory
- severity: advisory
- citation: fixtures/user_service.py:10, 37, 58
- claim_violated: none
- observation: DB_PATH 是 module constant，不由 user 輸入構成，無
  path-traversal exploitation path。FUD 類「萬一被設成 user input…」
  本 agent 禁忌；不升級。
- suggested_fix: none — advisory only.
- balance_note: N/A.

### sec-05-no-authz-on-new_user
- severity: advisory
- citation: fixtures/user_service.py:56
- claim_violated: none — target 未宣稱任何 authz
- observation: new_user 沒有 authz check。但本檔 target 描述不含 web 層 /
  endpoint 呼叫脈絡 —— threat model 未明示；要求加 authz 會落入本 agent
  禁忌「威脅建模投射」。回報為 advisory。
- suggested_fix: none — advisory only.
- balance_note: N/A.
