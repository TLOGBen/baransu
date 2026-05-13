# Code Review — `fixtures/user_service.py`

審查檔案：`/home/vakarve/projects/baransu/plugins/baransu/skills/review-workspace/iteration-1/fixtures/user_service.py`
審查模式：嚴格獨立審查（clean-eyes pass）
審查者視角：預設 Claude，無特殊框架

---

## 總結判斷（TL;DR）

這份 61 行的模組裡混合了 **三個層次的問題**：

1. **安全／正確性 bug（必須修，阻擋上線）** — 硬編碼 API key、MD5 密碼雜湊、未處理的 `None` 導致 KeyError、`new_user()` 寫入時覆蓋整個資料庫。
2. **過度工程（應移除）** — `UserBuilder` 類別只為兩個欄位的 dict 服務、只有一個呼叫點，完全不划算。
3. **Cosmetic（順手清掉即可）** — 未使用的 import、引號風格不一致、缺 type hint、缺錯誤處理路徑的文件。

**發佈前必修**：P0-1、P0-2、P0-3、P0-4。
**強烈建議**：P1-1（刪掉 Builder）、P1-2（檔案 IO 正確性）。
**順手清掉**：P2 全部。

---

## P0 — Blockers（必須修，不修不能合）

### P0-1. 硬編碼生產環境 API Key（line 9）

```python
API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c"  # hardcoded secret
```

**嚴重性**：Critical（安全事件）
**問題**：
- 此字串看起來像 live API key，一旦進 git history 就算是已洩漏，必須立刻 **輪換（rotate）**，而不只是把程式碼移除。
- 光把字串換成環境變數是不夠的 — 還要走 `git log -p` / GitHub 掃描確認沒有其他副本；如果已經 push 過遠端或進過任何 CI log，假設金鑰已外洩。
- 模組內根本沒有用到 `API_KEY`，這表示它可能是「以後要用」的殘留 — 更危險，因為沒有任何 runtime 訊號會讓人發現。

**修法**：
```python
import os
API_KEY = os.environ["SERVICE_API_KEY"]  # 啟動即 fail-fast；缺值比默默用錯 key 安全
```
搭配 `.env` + `.gitignore`，並且把原本那把 key 在供應商後台作廢。

---

### P0-2. MD5 用於密碼雜湊（line 44）

```python
attempt_hash = hashlib.md5(password.encode()).hexdigest()
```

**嚴重性**：Critical（安全／合規）
**問題**：
- MD5 **不是密碼雜湊演算法**。它是快速雜湊，對 GPU 暴力破解完全沒防線；無 salt，彩虹表能直接撞開常見密碼。
- `==` 比較容易走 timing side-channel。

**修法**：改用 `bcrypt`、`argon2-cffi`（推薦）或標準庫 `hashlib.scrypt` + salt。示意：
```python
import bcrypt
# 建立用戶時：bcrypt.hashpw(pw.encode(), bcrypt.gensalt())
# 驗證時：bcrypt.checkpw(pw.encode(), stored_hash)
```
如果資料庫裡已經存了 MD5 hash，需要一套遷移策略（下次登入時重 hash）。這是另一個 ticket，但必須排進去。

---

### P0-3. `user is None` 未處理，造成 `TypeError` 而非回傳 `None`（line 40–43）

```python
user = users.get(username)
# Bug: no null check ...
stored_hash = user["password_hash"]
```

**嚴重性**：High（行為與 docstring 矛盾）
**問題**：docstring 明文保證「returns None on failure」，但查不到 user 時程式會 crash，而不是回傳 None。這不只是 bug，還是**合約違約** — 呼叫端寫的 `if authenticate(...) is None:` 檢查會完全被繞過，錯誤路徑未定義。

**修法**：
```python
user = users.get(username)
if user is None:
    return None
stored_hash = user.get("password_hash")
if stored_hash is None:
    return None
```
順便也處理 `password_hash` 欄位缺失的狀況。另外考慮 `hmac.compare_digest(stored_hash, attempt_hash)` 做 constant-time 比較。

---

### P0-4. `new_user()` 把整個 users DB 用單一 user 覆寫（line 56–60）

```python
def new_user(name: str, email: str):
    user = build_user(name, email)
    with open(DB_PATH, "w") as f:
        json.dump(user, f)   # ← 覆寫！整個 DB 變成只有這一個 user
    return user
```

**嚴重性**：Critical（資料遺失）
**問題**：`authenticate()` 期望 `DB_PATH` 是 `{username: {...}}` 的 dict，但 `new_user()` 把檔案整個蓋成單一 user dict。**第一次呼叫 `new_user()` 就會把整個使用者資料庫清空**。這是生產級 data-loss bug，比其他幾條都嚴重。

另外還有：
- 沒有 key（用 `name`？`email`？）— 連要怎麼在 DB 裡找回這個 user 都不清楚。
- 沒有密碼 / password_hash — 建立出來的 user 日後無法通過 `authenticate()`。
- 沒 file locking — 兩個 process 併發呼叫會 race。
- JSON flat file 本身作為 user store 也不建議，但那是設計層級，此 ticket 先不展開。

**修法（至少）**：
```python
def new_user(name: str, email: str, password: str):
    try:
        with open(DB_PATH) as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    if name in users:
        raise ValueError(f"user {name!r} already exists")
    users[name] = {
        "name": name,
        "email": email,
        "password_hash": bcrypt_hash(password),  # 見 P0-2
        "role": "member",
    }
    with open(DB_PATH, "w") as f:
        json.dump(users, f)
    return users[name]
```
長期應改用真正的 DB + 事務。

---

## P1 — 應該修（過度工程 / 正確性邊緣）

### P1-1. `UserBuilder` 是過度工程，應刪除（line 13–29）

**判斷**：**這是過度設計，應該整類刪掉**。

原因（明確的，不是口味問題）：
- 只有一個呼叫點（`build_user()`），而 `build_user()` 自己也只有一個呼叫點（`new_user()`）。
- 建的物件是 **一個兩欄位的 dict**。Builder pattern 的價值在「多個可選參數＋逐步建構＋不可變結果」；這裡一個都不成立。
- 真正需要的，`{"role": "member", "name": name, "email": email}` 一行就夠。

Builder pattern 在 Python 多半是 anti-pattern — 語言本身就有 keyword args 和 `dataclass` 處理「多可選欄位」。保留它只會讓下一個讀這份程式碼的人花力氣判斷「這東西是不是有我沒看到的用途」。

**修法**：整個 `UserBuilder` 類 + `build_user()` 刪掉，`new_user()` 直接 inline。如果之後欄位真的變多，用 `@dataclass(frozen=True)`。

---

### P1-2. 檔案 I/O 缺失：不存在、壞 JSON、權限、併發（line 37–38, 58–59）

**問題**：`authenticate()` 裡 `open(DB_PATH)` 沒有 `FileNotFoundError` / `json.JSONDecodeError` 處理；`new_user()` 也沒有；兩者對 DB 檔的存取沒 lock。

**修法**：至少包起來 try/except 並 log；寫檔用 temp file + `os.replace` 做 atomic replace，避免寫到一半 crash 導致 DB 損毀。

---

### P1-3. `authenticate()` 每次都重讀整份 DB

在 fixture / 玩具規模不是問題，但若 `DB_PATH` 真的是多使用者 JSON，登入每次都整份讀進記憶體不會 scale。搭配 P0-4 的改造一起做。

---

## P2 — Cosmetic / 小清理

這些獨立來看都不是「必須」，一次清掉省時省事。

| 行 | 問題 | 修法 |
|---|---|---|
| 6 | `import datetime` 未使用 | 刪除 |
| 7 | `import logging` 未使用 | 刪除（若 P1-2 要加 log，則保留並實際用） |
| 21 vs 25 | 字典鍵 `'name'` 單引號、`"email"` 雙引號不一致 | 統一（專案若用 black，會自動雙引號） |
| 56 | `new_user()` 缺 return type hint | 加 `-> dict`（或遷移到 dataclass） |
| 32 | `authenticate()` 的 docstring 沒寫出例外行為 | 補「raises FileNotFoundError if DB missing」或由 P1-2 修掉這件事 |
| 整體 | 無 `__all__`、無 module docstring 描述 public API | 低優先 |

---

## 測試

目前沒有 e2e，使用者已自述。**在修 P0 的同時應補以下 unit tests**（TDD 優先，先寫測試讓 P0-3、P0-4 變紅）：

1. `authenticate("不存在的人", "x")` 回傳 `None`（不丟例外）— 釘住 P0-3。
2. `authenticate(known_user, 正確密碼)` 回傳 user dict。
3. `authenticate(known_user, 錯誤密碼)` 回傳 `None`。
4. 連呼叫兩次 `new_user()`，第一個 user 必須還在 — 釘住 P0-4。
5. `new_user` 重複 name 丟 `ValueError`。
6. DB 檔不存在時，`authenticate()` 的行為是可預期的（明確丟例外，或回 None，二擇一並寫進 docstring）。

框架用 `pytest`，fixture 用 `tmp_path` 做隔離的 DB 檔案，不要碰 `/var/data/users.json`。

---

## 審查者的三個元觀察

1. **這份檔案的主要風險是安全與資料遺失，不是過度設計。** P1-1 的 Builder 看起來很顯眼、很好罵，但它「只是醜」；真正會燒掉產品的是 P0-1（洩漏 key）、P0-2（MD5）、P0-4（蓋 DB）。審查優先順序不要被視覺複雜度誤導。

2. **docstring 與實作不一致是危險信號。** `authenticate()` 的 docstring 保證 `None on failure`，實作卻會 crash — 這代表原作者寫 docstring 時是「對的」，但之後改實作忘了同步。整份 codebase 建議跑一次 docstring contract 對齊。

3. **模組命名叫 `user_service` 但混合了 store（讀 / 寫檔案）、auth（密碼驗證）、builder（建構）三種責任。** 現在規模太小談分層還太早，但修 P0-4 時可以很便宜地順勢把「使用者儲存」抽到 `UserRepository` 介面後面，未來換 DB 不痛。

---

## 建議修復順序

1. **立刻**：輪換 API_KEY（P0-1），這是跑在人之外的動作。
2. **同一個 PR**：P0-3（null check）+ P0-4（DB 覆寫）+ 對應的 pytest。PR 小、改動集中、影響關鍵路徑。
3. **下一個 PR**：P0-2（bcrypt 遷移）+ 舊 MD5 hash 的遷移策略。
4. **再下一個 PR / 同一個**：刪 Builder（P1-1），補 I/O 錯誤處理（P1-2），清 cosmetic（P2）。
5. **Optional**：引入 `UserRepository` 抽象。

以上。
