import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .database import Base, SessionLocal, engine
from .models import Framework
from .observability import init_sentry
from .routers import entities, frameworks, meta, relationships
from .seed import seed as seed_db

load_dotenv()

# Error tracking - no-op unless SENTRY_DSN is set (see observability.py).
init_sentry("method-map")

Base.metadata.create_all(bind=engine)

# Seed the bundled frameworks on first boot against an empty database - e.g. a
# fresh deploy, or after a host with ephemeral disk (Render free tier) wipes it
# on restart. Idempotent: skips any framework that already exists. Skipped under
# pytest, which uses its own isolated per-test database.
if "PYTEST_CURRENT_TEST" not in os.environ:
    with SessionLocal() as _db:
        if _db.query(Framework).count() == 0:
            seed_db(_db)

app = FastAPI(title="P3MAI Method Map API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router)
app.include_router(frameworks.router)
app.include_router(entities.router)
app.include_router(relationships.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


# In production this backend also serves the built React frontend (npm run build
# in frontend/) so the whole app lives behind one origin. Locally frontend/dist
# won't exist (Vite dev server serves it instead), so this block is skipped.
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
