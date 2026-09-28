from fastapi import APIRouter
from fastapi.responses import FileResponse

from app.core.errors import AppError
from app.services.project_service import project_service

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("/{project_id}/{folder}/{filename}")
def get_file(project_id: str, folder: str, filename: str):
    if folder not in {"original", "cropped", "preview", "export"}:
        raise AppError("IMAGE_NOT_FOUND", "文件不存在", 404)
    project_dir = project_service.project_dir(project_id).resolve()
    path = (project_dir / folder / filename).resolve()
    if project_dir not in path.parents or not path.exists():
        raise AppError("IMAGE_NOT_FOUND", "文件不存在", 404)
    return FileResponse(path, headers={"Cache-Control": "public, max-age=31536000, immutable"})
