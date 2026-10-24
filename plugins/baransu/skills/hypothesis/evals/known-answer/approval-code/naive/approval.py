"""簽核服務（天真版）。每個 HTTP 請求呼叫一個函式；多個請求可能同時進行。

規則：金額 < 1000 只要主管核准；≥ 1000 要主管再財務。核准完成後由付款工作付款。
申請人在簽核中可以撤回；被退回後可以改金額再送出。
"""
from dataclasses import dataclass, field

THRESHOLD = 1000


@dataclass
class Request:
    status: str = "draft"            # draft | pending | approved | rejected | withdrawn
    amount: int = 0
    approvals: list = field(default_factory=list)   # [(role, amount)]
    paid: bool = False
    paid_amount: int = 0


DB: dict[int, Request] = {}


def load(rid: int) -> Request:
    r = DB[rid]
    return Request(r.status, r.amount, list(r.approvals), r.paid, r.paid_amount)


def save(rid: int, r: Request) -> None:
    DB[rid] = r


def required(amount: int) -> list[str]:
    return ["manager"] if amount < THRESHOLD else ["manager", "finance"]


def next_role(r: Request) -> str | None:
    done = {role for role, _ in r.approvals}
    for role in required(r.amount):
        if role not in done:
            return role
    return None


def edit(rid: int, amount: int) -> None:
    r = load(rid)
    if r.status in ("draft", "rejected"):
        r.amount = amount
        save(rid, r)


def submit(rid: int) -> None:
    r = load(rid)
    if r.status in ("draft", "rejected"):
        r.status = "pending"            # 舊的核准紀錄沒有清掉
        save(rid, r)


def approve(rid: int, role: str) -> None:
    r = load(rid)                       # 讀
    if r.status == "pending" and next_role(r) == role:   # 檢查
        r.approvals.append((role, r.amount))
        if next_role(r) is None:
            r.status = "approved"
        save(rid, r)                    # 寫：與讀之間沒有鎖


def reject(rid: int, role: str) -> None:
    r = load(rid)
    if r.status == "pending" and next_role(r) == role:
        r.status = "rejected"
        save(rid, r)


def withdraw(rid: int) -> None:
    r = load(rid)                       # 讀
    if r.status == "pending":           # 檢查
        r.status = "withdrawn"
        save(rid, r)                    # 寫：與讀之間沒有鎖


def pay(rid: int) -> None:
    r = load(rid)
    if r.status == "approved" and not r.paid:
        r.paid = True
        r.paid_amount = r.amount
        save(rid, r)
