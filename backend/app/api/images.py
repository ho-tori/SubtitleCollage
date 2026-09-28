from fastapi import APIRouter, File, UploadFile
from pydantic import BaseModel

from app.core.errors import AppError
from app.services.image_service import delete_image_files, image_service
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}/images", tags=["images"])


class UpdateImageRequest(BaseModel):
    selected: bool | None = None
    is_cover: bool | None = None
    order: int | None = None


class ReorderRequest(BaseModel):
    image_ids: list[str]


@router.post("")
async def upload_images(project_id: str, files: list[UploadFile] = File(...)):
    project = project_service.get(project_id)
    items = await image_service.add_images(project, files)
    return {"items": [serialize_item(project_id, item) for item in items]}


@router.put("/order")
def reorder_images(project_id: str, payload: ReorderRequest):
    project = project_service.get(project_id)
    by_id = {item.id: item for item in project.screenshots}
    if set(payload.image_ids) != set(by_id):
        raise AppError("IMAGE_NOT_FOUND", "排序列表必须包含全部图片")
    project.screenshots = [by_id[image_id] for image_id in payload.image_ids]
    for index, item in enumerate(project.screenshots, start=1):
        item.order = index
    project_service.save(project)
    return {"items": [serialize_item(project_id, item) for item in project.screenshots]}


@router.put("/{image_id}")
def update_image(project_id: str, image_id: str, payload: UpdateImageRequest):
    project = project_service.get(project_id)
    item = next((candidate for candidate in project.screenshots if candidate.id == image_id), None)
    if item is None:
        raise AppError("IMAGE_NOT_FOUND", "图片不存在", 404)
    if payload.selected is not None:
        item.selected = payload.selected
    if payload.order is not None:
        item.order = payload.order
    if payload.is_cover is not None:
        if payload.is_cover:
            for candidate in project.screenshots:
                candidate.is_cover = candidate.id == image_id
        else:
            item.is_cover = False
    project.screenshots.sort(key=lambda value: value.order)
    project_service.save(project)
    return serialize_item(project_id, item)


@router.delete("/{image_id}")
def delete_image(project_id: str, image_id: str):
    project = project_service.get(project_id)
    removed = next((item for item in project.screenshots if item.id == image_id), None)
    if removed is None:
        raise AppError("IMAGE_NOT_FOUND", "图片不存在", 404)
    original_count = len(project.screenshots)
    project.screenshots = [item for item in project.screenshots if item.id != image_id]
    if len(project.screenshots) == original_count:
        raise AppError("IMAGE_NOT_FOUND", "图片不存在", 404)
    for index, item in enumerate(project.screenshots, start=1):
        item.order = index
    if project.screenshots and not any(item.is_cover for item in project.screenshots):
        project.screenshots[0].is_cover = True
    project_service.save(project)
    delete_image_files(project, removed)
    return {"message": "Image deleted"}


def serialize_item(project_id: str, item):
    payload = item.model_dump()
    if item.preview_path:
        payload["preview_url"] = f"/api/files/{project_id}/{item.preview_path}"
    if item.cropped_path:
        payload["cropped_url"] = f"/api/files/{project_id}/{item.cropped_path}"
    return payload
