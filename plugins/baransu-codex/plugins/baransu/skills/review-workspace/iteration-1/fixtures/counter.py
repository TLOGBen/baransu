"""Shared-state counter module.

The PR author claims in the commit message: "counter.increment() is
thread-safe — safe to call from multiple threads without a lock."
"""


class Counter:
    def __init__(self, start: int = 0):
        self._value = start

    def increment(self) -> int:
        # Read-modify-write with no synchronization.
        current = self._value
        current = current + 1
        self._value = current
        return self._value

    def get(self) -> int:
        return self._value
