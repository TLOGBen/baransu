"""簽核服務（修正版）。每個 HTTP 請求呼叫一個函式；多個請求可能同時進行。

規則：金額 < 1000 只要主管核准；≥ 1000 要主管再財務。核准完成後由付款工作付款。
申請人在簽核中可以撤回；被退回後可以改金額再送出。
"""
from dataclasses import dataclass, field

THRESHOLD = 1000


class Conflict(Exception):
    """另一個請求已經先改過這張申請。"""


@dataclass
class Request:
    status: str = "draft"            # draft | pending | approved | rejected | withdrawn
    amount: int = 0
    approvals: list = field(default_factory=list)   # [(role, amount)]
    paid: bool = False
    paid_amount: int = 0
    version: int = 0


DB: dict[int, Request] = {}


def load(rid: int) -> Request:
    r = DB[rid]
    return Request(r.status, r.amount, list(r.approvals), r.paid, r.paid_amount, r.version)


def save(rid: int, r: Request) -> None:
    """比較後交換：只有版本沒變時才寫入，寫入時版本加一。"""
    if DB[rid].version != r.version:
        raise Conflict(rid)
    r.version += 1
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
        r.status = "pending"
        r.approvals = []                # 重送時清空舊的核准
        save(rid, r)


def approve(rid: int, role: str) -> None:
    r = load(rid)
    if r.status == "pending" and next_role(r) == role:
        r.approvals.append((role, r.amount))
        if next_role(r) is None:
            r.status = "approved"
        save(rid, r)                    # 版本不同就丟出 Conflict，什麼都不寫


def reject(rid: int, role: str) -> None:
    r = load(rid)
    if r.status == "pending" and next_role(r) == role:
        r.status = "rejected"
        save(rid, r)


def withdraw(rid: int) -> None:
    r = load(rid)
    if r.status == "pending":
        r.status = "withdrawn"
        save(rid, r)


def pay(rid: int) -> None:
    r = load(rid)
    if r.status == "approved" and not r.paid:
        r.paid = True
        r.paid_amount = r.amount
        save(rid, r)
