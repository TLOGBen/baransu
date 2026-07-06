# Mini spec — 帳單狀態機（domain dry-run fixture）

> Fixture for the /review domain-grounding semantic dry run. One-page business
> spec; the sole authoritative source for the transition table in this fixture.

## 1. States

| 狀態 | 說明 | 終態 |
|---|---|---|
| 待付款 | 帳單建立後的初始狀態 | no |
| 已付款 | 付款完成 | yes |
| 已取消 | 帳單於付款前被取消 | yes |
| 逾期 | 到期日已過且未付款 | no |
| 呆帳 | 逾期滿 180 天經核准轉列 | yes |

新建帳單一律進入「待付款」；終態無任何出向轉移。

## 2. Transitions

### 2.1 待付款 → 已付款（事件：付款成功）
無額外前置條件。

### 2.2 待付款 → 逾期（事件：逾期日到）
前置條件：到期日已過且未收到付款。

### 2.3 待付款 → 已取消（事件：取消帳單）
前置條件：尚未收到任何付款。

### 2.4 逾期 → 已付款（事件：付款成功）
逾期補繳；無額外前置條件。

### 2.5 逾期 → 呆帳（事件：轉呆帳）
前置條件：逾期天數 ≥ 180，且經主管核准。

## 3. Global invariant

**呆帳必經逾期**：任何帳單要成為「呆帳」，必須先處於「逾期」且滿足 2.5 的
前置條件。不存在由「待付款」直接轉「呆帳」的合法路徑。
