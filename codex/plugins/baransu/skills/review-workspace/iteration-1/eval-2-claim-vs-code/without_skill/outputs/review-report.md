# Thread-Safety 審查報告

**目標檔案**: `fixtures/counter.py`
**宣稱**: 「`Counter.increment()` 是 thread-safe，可在多執行緒呼叫而不需加鎖。」
**結論**: **此宣稱為假 (NOT thread-safe)。**

---

## 一、程式碼重點

```python
def increment(self) -> int:
    current = self._value        # 讀
    current = current + 1        # 改
    self._value = current        # 寫
    return self._value
```

`get()` 亦直接回傳 `self._value`，無任何同步機制。

---

## 二、為什麼不是 Thread-Safe

這是一個教科書等級的 **讀—改—寫 (read-modify-write) race condition**。

### 2.1 Race 的具體時序

假設 `self._value == 0`，兩個執行緒 T1、T2 同時呼叫 `increment()`：

| 時刻 | T1                          | T2                          | `self._value` |
| ---- | --------------------------- | --------------------------- | ------------- |
| t0   | `current = self._value` → 0 |                             | 0             |
| t1   |                             | `current = self._value` → 0 | 0             |
| t2   | `current = 0 + 1` → 1       |                             | 0             |
| t3   |                             | `current = 0 + 1` → 1       | 0             |
| t4   | `self._value = 1`           |                             | 1             |
| t5   |                             | `self._value = 1`           | 1             |

兩次 `increment()` 後結果應為 2，實際為 1。**典型的 lost update。**

### 2.2 「Python 有 GIL 就沒事」是常見誤解

同事可能誤以為 CPython 的 GIL 會讓 `increment()` atomic。事實上：

1. GIL 只保證單一 bytecode 指令不會被中斷；`increment()` 內的讀—改—寫跨越**多條** bytecode（`LOAD_ATTR`、`BINARY_ADD`、`STORE_ATTR`），任何一條之後都可能被排程器切走。
2. 即使寫成 `self._value += 1` 仍然不 atomic（Python 官方 FAQ 明確說明只有極少數操作，例如 `list.append`，剛好是 atomic）。
3. PEP 703 (no-GIL) 下更徹底失去這個「意外的」保護。
4. 這是 CPython FAQ 與 `threading` 文件長期以來的標準警告案例。

### 2.3 經驗證據（可選的驗證腳本）

若要實證，可執行：

```python
import threading
from counter import Counter

c = Counter()
def worker():
    for _ in range(100_000):
        c.increment()

threads = [threading.Thread(target=worker) for _ in range(8)]
for t in threads: t.start()
for t in threads: t.join()
assert c.get() == 800_000, f"lost updates: got {c.get()}"
```

在任何多核機器上這個 assert 幾乎必定失敗（通常會少幾萬到幾十萬）。

---

## 三、最小必要修法

**在 `__init__` 加一個 `threading.Lock`，用 `with` 包住 `increment()` 的讀—改—寫。** 不需要更多。

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

    def get(self) -> int:
        return self._value
```

### 3.1 為什麼這樣就夠（不 over-engineer）

- **一把 `Lock` 已足夠**：臨界區極短（一次加法 + 一次屬性寫），無巢狀鎖需求，不需要 `RLock`。
- **不需要 `queue.Queue` / actor / atomic 第三方套件**：這裡只有一個整數計數器，拿大砲打蚊子。
- **不需要改 `get()`**：Python 屬性讀取本身對 `int` 是單步 bytecode，且本例只要求「不丟失遞增」，沒有要求 `get()` 與某次 `increment()` 精確對齊。如果呼叫方需要「快照語意」，才考慮在 `get()` 也加 `with self._lock:`（視需求再加，不是現在必要）。
- **`return self._value` 放在 `with` 內**：確保回傳的是「本次遞增後」的值，否則仍有 race（他人先 increment 再被本執行緒讀到，回傳值就不再是「自己這次+1後的結果」）。這一點是此修法裡唯一容易寫錯的細節。
- **不需要 `functools.lru_cache` / `__slots__` / `atomic int` 擴充**：皆與 thread-safety 無關。

### 3.2 Diff 大小

新增 1 個 import、1 個欄位、把 3 行包進 `with`，合併為 `+=`。總共 4~5 行變動。

---

## 四、給同事的一句話

> 「`increment()` 有 read-modify-write race，GIL 保護的是單條 bytecode 不是整個方法；加一把 `threading.Lock` 包住那三行就好，不要改其他東西。」

## 最終判定

**NOT thread-safe。** 最小修法：在 `Counter` 加入 `threading.Lock`，用 `with self._lock:` 包住 `increment()` 內的讀—改—寫與 `return`。共約 4~5 行變動，無須其他改動。
