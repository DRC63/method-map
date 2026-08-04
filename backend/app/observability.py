"""Optional error tracking (Sentry).

Fully inert unless SENTRY_DSN is set: local dev, tests and any deployment
without the secret run completely untouched, and sentry-sdk is imported only
when a DSN is actually present (so it is not even required at runtime until
activated). Turn it on by setting SENTRY_DSN as a deployment secret; optionally
SENTRY_ENVIRONMENT and SENTRY_TRACES_SAMPLE_RATE.

sentry-sdk auto-instruments FastAPI when init runs at import time (before any
request is served), so no app wrapping is needed - just call init_sentry() early
in main.py.
"""
import os


def init_sentry(service: str) -> bool:
    """Initialise Sentry when SENTRY_DSN is configured; return True if enabled.

    `service` tags every event, so one Sentry project can host all P3MAI apps and
    still be filterable per app. The import is deferred to keep sentry-sdk an
    activate-only dependency - nothing is imported when the DSN is unset.
    """
    dsn = os.getenv("SENTRY_DSN", "").strip()
    if not dsn:
        return False

    import sentry_sdk

    sentry_sdk.init(
        dsn=dsn,
        # Environment + release aid triage; default to production when unspecified.
        environment=os.getenv("SENTRY_ENVIRONMENT", "production"),
        # Errors are the priority, not tracing - sample performance at 0 by default
        # to avoid quota/cost surprises; raise via env if tracing is wanted.
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        # Privacy first: do not attach request bodies, headers or user identifiers.
        send_default_pii=False,
    )
    sentry_sdk.set_tag("service", service)
    return True
