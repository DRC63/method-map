"""Lightweight single-password gate for authoring/edit mode.

Read access is fully open (public reference tool). Any write endpoint depends on
`require_admin`, which checks an `X-Admin-Password` header against ADMIN_PASSWORD.
This is deliberately simple - enough to stop casual edits on an open deployment,
not a full account system. Swap for real auth if the app ever holds anything
sensitive.
"""
import os

from fastapi import Header, HTTPException

DEFAULT_ADMIN_PASSWORD = "change-me"


def _admin_password() -> str:
    return os.getenv("ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)


def check_password(candidate: str | None) -> bool:
    return bool(candidate) and candidate == _admin_password()


def require_admin(x_admin_password: str | None = Header(default=None)) -> None:
    if not check_password(x_admin_password):
        raise HTTPException(status_code=401, detail="Invalid or missing admin password")
