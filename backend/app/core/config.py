from pathlib import Path
import sys


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[3]


def bundled_base_dir() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS).resolve()
    return app_base_dir()


BASE_DIR = app_base_dir()
BUNDLED_BASE_DIR = bundled_base_dir()
DATA_DIR = BASE_DIR / "data"
PROJECTS_DIR = DATA_DIR / "projects"
FRONTEND_DIST_DIR = BUNDLED_BASE_DIR / "frontend" / "dist"

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_IMAGE_SIZE_BYTES = 15 * 1024 * 1024
MAX_IMAGES_PER_PROJECT = 50
MAX_EXPORT_PIXELS = 120_000_000
