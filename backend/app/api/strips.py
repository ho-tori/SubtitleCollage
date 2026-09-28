from fastapi import APIRouter

from app.core.errors import AppError
from app.models.roi import RoiConfig
from app.services.collage_service import crop_subtitle_strip
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}", tags=["strips"])


@router.put("/roi")
def update_roi(project_id: str, roi: RoiConfig):
    project = project_service.get(project_id)
    project.roi = roi
    project_service.save(project)
    return {"message": "ROI updated"}


@router.post("/strips")
def generate_strips(project_id: str):
    project = project_service.get(project_id)
    if project.roi is None:
        raise AppError("ROI_NOT_CONFIGURED", "尚未设置字幕区域")
    project_dir = project_service.project_dir(project.id)
    for item in project.screenshots:
        if item.is_cover:
            item.cropped_path = None
            continue
        source = project_dir / item.original_path
        cropped_name = f"{item.id}.png"
        cropped = project_dir / "cropped" / cropped_name
        crop_subtitle_strip(source, cropped, project.roi)
        item.cropped_path = f"cropped/{cropped_name}"
    project_service.save(project)
    return {"items": [serialize_item(project_id, item) for item in project.screenshots]}


def serialize_item(project_id: str, item):
    payload = item.model_dump()
    payload["original_url"] = f"/api/files/{project_id}/{item.original_path}"
    if item.cropped_path:
        payload["cropped_url"] = f"/api/files/{project_id}/{item.cropped_path}"
    if item.preview_path:
        payload["preview_url"] = f"/api/files/{project_id}/{item.preview_path}"
    return payload
