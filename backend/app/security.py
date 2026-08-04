"""Lightweight single-password gate for authoring/edit mode.

Read access is fully open (public reference tool). Any write endpoint depends on
`require_admin`, which checks an `X-Admin-Password` header against ADMIN_PASSWORD.
This is deliberately simple - enough to stop casual edits on an open deployment,
not a full account system. Swap for real auth if the app ever holds anything
sensitive.

Fail-closed by design: if ADMIN_PASSWORD is unset or blank, authoring is
DISABLED (every write is rejected) rather than falling back to a guessable
default. A deployment that forgets to set the secret is therefore read-only,
never wide open. (An earlier version defaulted to "change-me", which left any
service without an explicit secret editable by anyone - the reason this now
fails closed.)
"""
import os

from fastapi import Header, HTTPException


def _admin_password() -> str | None:
    """The configured authoring password, or None if authoring is disabled.
    Blank/whitespace is treated as unset so an empty dashboard value fails closed
    rather than accepting an empty password."""
    value = os.getenv("ADMIN_PASSWORD", "").strip()
    return value or None


def check_password(candidate: str | None) -> bool:
    """True only when a password is configured AND the candidate matches it.
    With no password configured this always returns False - writes are disabled,
    not defaulted - so an unconfigured deployment cannot be authored."""
    configured = _admin_password()
    return bool(configured) and candidate == configured


def require_admin(x_admin_password: str | None = Header(default=None)) -> None:
    if not check_password(x_admin_password):
        raise HTTPException(status_code=401, detail="Invalid or missing admin password")
