# /baransu:review — 審核結果

**Verdict：FAIL**

## Target

- 路徑：`plugins/baransu/skills/review-workspace/iteration-1/fixtures/counter.py`
- 型態：單一檔案 + 明確宣稱（code + claim target）
- 規模：21 行（含 docstring），實際程式碼 ~12 LOC，1 class、2 methods
- Tier：**T1 quick**（≤ 100 LOC、單檔、單宣稱）
- 宣稱來源：module docstring 第 3–4 行 + commit message + 使用者 invocation 原文

## 目標宣稱 (Claim Checklist)

本次 target 只承載一條顯式宣稱，是宣稱與實作是否相符的純粹審核：

1. **[CLAIM-1 — 主宣稱]** `Counter.increment()` 是 thread-safe 的 —
   根據 docstring：「safe to call from multiple threads without a lock」。
   這是本次 review 唯一需要驗證的主張，也是本次的幻覺檢查核心。
2. **[SCOPE — 隱含]** 本檔只負責一個共享計數器，API 為 `__init__(start)` /
   `increment() -> int` / `get() -> int`，語義應與一般計數器相同
   （每次 increment 遞增 1 並回傳新值）。
3. **[NOT-CLAIMED]** 檔案未宣稱：process-safe、async-safe、distributed-safe、
   reentrant、順序性保證、或任何 memory model 細節 —— 這些在本次 review 中視為
   out-of-scope，不產 finding。
4. **[UNKNOWNS]** 未明示的假設：執行環境（CPython with GIL？no-GIL build？
   PyPy？）、切換間隔（`sys.setswitchinterval` 是否被改？）、同時呼叫的 thread
   數量上限。`/review` 採保守假設：必須在所有主流 Python runtime（含 CPython
   3.13 free-threaded build）下成立才算 thread-safe。

## 派遣的審核者

- **架構審核**：**略過** — target 為單檔 12 LOC，不跨模組、不跨層、無新介面 /
  新抽象 / 新依賴方向；activation 表明確指示單檔小 target 不應啟用此視角。
  強行啟動只會產生雜訊 finding（"這個 class 可不可以改 dataclass"），與本次
  宣稱驗證的核心無關。
- **品質審核**：**啟用** — 屬 "correctness-vs-claim" 的經典場景。target 具可執行
  code + 明確宣稱，正中 quality-reviewer 的核心職責（幻覺檢查：checklist 每
  一條宣稱對照真實程式行為）。本次只動用此一個視角。
- **安全審核**：**略過** — 無 auth / authz / session、無 input handling、無 secret
  / crypto、無 network / serialization / filesystem / shell。thread-safety 是
  correctness 面向，不是安全面向；誤派會產出 FUD 類 finding（"race condition
  在安全脈絡可能…"），違反 security-reviewer 的 "具體可利用路徑" 原則。
- **對抗測試**：**略過** — 依 Stage 3 規則，T1 quick、非 cross-layer、非
  cross-service，adversarial 明示略過；宣稱本身已完全形式化（"thread-safe or
  not"），對抗角度不會再生出新視角。
- **AskUserQuestion 繞過說明**：Auto mode 啟用；本次 tier / activation / fix
  scope 皆有單一 defensible default（T1、單 reviewer、`threading.Lock`），
  不符合 AskUserQuestion 真正有價值的情境（多選項且代價不對稱）。依平台
  規則（platform-awareness）採預設並於此註記。

## 發現（四級 triage）

### Tier 1 — 已自動修復（format / import / typo / dead import）

無。程式碼 format 乾淨，無 dead import。

### Tier 2 — 待確認（非語意但超出 T1）

無。

### Tier 3 — 需判斷

**[FINDING-Q1]** 宣稱與實作不符（critical）

- id：`q1-claim-hallucinated`
- severity：**critical**
- citation：`fixtures/counter.py:12-17`
- claim_violated：CLAIM-1（"increment() is thread-safe"）
- observation：
  `increment()` 的實作為三行無同步保護的 read-modify-write：
  ```
  current = self._value          # LOAD
  current = current + 1          # ADD
  self._value = current          # STORE
  ```
  CPython GIL 僅保證**單一 bytecode**的原子性，不保證多 bytecode 序列的
  原子性。在 LOAD 與 STORE 之間，GIL 可被釋放（`sys.setswitchinterval` 控制，
  預設 5ms）。兩個 thread 可同時讀到相同 `current`，各自加 1 後回寫相同
  新值，造成「遺失更新」（lost update）—— 此即教科書上最經典的 data race。
  在 CPython 3.13+ 的 free-threaded build 上，連單 bytecode 原子性都不保證，
  情況更嚴重。docstring 所述「safe to call from multiple threads without a lock」
  **為假**。
- suggested_fix（最小必要修法 / surgical minimum）：
  ```python
  import threading

  class Counter:
      def __init__(self, start: int = 0):
          self._value = start
          self._lock = threading.Lock()

      def increment(self) -> int:
          with self._lock:
              self._value += 1
              return self._value
  ```
  改動 scope：+1 import、+1 實例屬性、+1 `with` block、`get()` 視需要亦可
  加鎖（只讀單一 int 在 CPython 下 LOAD_ATTR 單 bytecode 足夠，最小修法可
  不動 `get()`；若要 free-threaded build 也正確，再加 `with self._lock:` 於
  `get()`）。
- balance_note：
  - 不做的代價：宣稱為謊，任何相信 docstring 的 caller 都會在壓力下遇到
    intermittent 少數遺失更新；debug 極其困難（symptom = 偶爾少掉幾次
    計數，重現不穩定）。
  - 做的代價：單一 `threading.Lock` 為 stdlib、零額外依賴；鎖粒度極小
    （三行），效能影響可忽略；API 形狀不變。
  - 中間方案：`itertools.count()` 可提供 lock-free 遞增，但會改 API 語義
    （不可設 start 外的任意值、不能重設、`get()` 的語義不同）—— 列為 FYI，
    非最小修法。
  - 結論：`threading.Lock` 是唯一通過天平的手術刀級修法。

### Tier 4 — 僅供參考

**[FYI-1]** `itertools.count` 替代方案 —
若 API 日後確定只需要「單調遞增計數器」且不需要重設或任意 set，可改以
`itertools.count(start)` 提供 lock-free 的原子遞增；但這會改變 `__init__` /
`get()` 的語義，屬 API 變更不是最小修法，故此次不建議採用。僅供未來演進
參考。

**[FYI-2]** 對抗性重寫建議（全部 downgrade 至此）—
以下於本案例皆屬**過度工程**，天平不通過，故本報告不作為建議：
- `asyncio.Lock` —— 與 thread model 錯配，解決不同問題。
- `queue.Queue` —— 不同 primitive，需要改寫 call site。
- `multiprocessing.Value` —— 跨 process 問題，不在 claim scope。
- Redis / 外部原子計數器 —— 完全脫離 target 尺寸。
- `dataclass(frozen=True)` + 回傳新 instance —— 從可變計數器改不可變，API 變更。

**[FYI-3]** 關於 `get()` 的補充 —
在 CPython with GIL 下，`get()` 僅一個 LOAD_ATTR bytecode 單獨原子；無需加鎖。
若要支援 CPython 3.13+ free-threaded build，或要求嚴格 memory model，應
在 `get()` 也加 `with self._lock:`。此點宣稱未涉及，故列 FYI 不列 Tier 3。

## E2E Gate

**n/a**，理由：
1. baransu repo 明確宣告無 build / test / lint 工具鏈（`CLAUDE.md` 的
   "What's Intentionally Absent" 節：無 `pyproject.toml` / `pytest.ini` /
   `Makefile` / `package.json`）。Stage 7 e2e gate 規則：「If test infra absent:
   verdict logic ignores e2e; note 'e2e gate: n/a (no test infra)'」。
2. target 本身是 skill eval 用的 **fixture**（位於 `review-workspace/.../fixtures/`），
   其存在目的即為被 review 的教材樣本，並非生產碼路徑，不該被 e2e 測試覆蓋。
3. 驗證 thread-safety 的「green test run evidence」實務上無法用一次 e2e 證偽
   race condition（race 是機率性的；測試通過不代表 thread-safe）—— 此案例
   的驗證更適合以程式語意分析（即本報告所為）完成。

## 結論

宣稱 `Counter.increment() is thread-safe` 為**幻覺**：程式碼第 12–17 行是
三個 bytecode 的 read-modify-write 序列，在 CPython GIL 模型下只保證單一
bytecode 原子性，無法保證整段原子性；在 free-threaded build 下更直接暴露為
data race。這是教科書級的 lost-update race，不是風格差異、不是品味問題，
是與 docstring 明文衝突的 correctness bug。最小必要修法為 `threading.Lock` +
`with` block，改動不超過 4 行，無外部依賴、不改 API 形狀、效能影響可忽略。
任何更大的改造（`asyncio` / `queue` / `multiprocessing` / Redis）在本宣稱
範圍下均不通過天平檢查，已全數降級為 FYI。Verdict 判為 **FAIL**：critical
severity 的 T3 finding，宣稱被確認為假，修法路徑已提出，等待使用者採納。
