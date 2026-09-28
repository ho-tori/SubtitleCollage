from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api import exports, files, images, projects, strips
from app.core.config import FRONTEND_DIST_DIR, PROJECTS_DIR
from app.core.errors import AppError, app_error_handler

PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Subtitle Collage", version="0.1.0")
app.add_exception_handler(AppError, app_error_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects.router)
app.include_router(images.router)
app.include_router(strips.router)
app.include_router(exports.router)
app.include_router(files.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


if FRONTEND_DIST_DIR.exists():
    assets_dir = FRONTEND_DIST_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    def serve_index():
        return FileResponse(FRONTEND_DIST_DIR / "index.html")

    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        if full_path.startswith("api/") or full_path == "assets":
            return FileResponse(FRONTEND_DIST_DIR / "index.html")
        candidate = (FRONTEND_DIST_DIR / full_path).resolve()
        if FRONTEND_DIST_DIR.resolve() in candidate.parents and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST_DIR / "index.html")
