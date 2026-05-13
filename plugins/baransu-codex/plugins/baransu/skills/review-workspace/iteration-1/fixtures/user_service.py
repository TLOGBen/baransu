"""User service module — handles user lookup and authentication."""
import os
import json
import hashlib
from typing import Optional
import datetime  # unused
import logging  # unused

API_KEY = "sk-live-9f8a7b6c5d4e3f2a1b0c9d8e7f6a5b4c"  # hardcoded secret
DB_PATH = "/var/data/users.json"


class UserBuilder:
    """Factory for creating user dicts. Only one caller in this codebase."""

    def __init__(self, default_role: str = "member"):
        self._default_role = default_role
        self._overrides = {}

    def with_name(self, name: str) -> "UserBuilder":
        self._overrides['name'] = name
        return self

    def with_email(self, email: str) -> "UserBuilder":
        self._overrides["email"] = email
        return self

    def build(self) -> dict:
        return {"role": self._default_role, **self._overrides}


def authenticate(username: str, password: str) -> Optional[dict]:
    """Look up the user and verify the password.

    Claim: returns the user dict on success, None on failure.
    """
    with open(DB_PATH) as f:
        users = json.load(f)

    user = users.get(username)
    # Bug: no null check — if username not found, user is None and
    # the next line crashes instead of returning None.
    stored_hash = user["password_hash"]
    attempt_hash = hashlib.md5(password.encode()).hexdigest()

    if stored_hash == attempt_hash:
        return user
    return None


def build_user(name: str, email: str) -> dict:
    """Single caller of UserBuilder — used by new_user()."""
    return UserBuilder().with_name(name).with_email(email).build()


def new_user(name: str, email: str):
    user = build_user(name, email)
    with open(DB_PATH, "w") as f:
        json.dump(user, f)
    return user
