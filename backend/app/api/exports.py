from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.errors import AppError
from app.services.collage_service import compose_collage_from_sources, parse_hex_color
from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects/{project_id}", tags=["exports"])


class ExportRequest(BaseModel):
    format: str = Field(default="png", pattern="^(png|jpg|jpeg)$")
    gap: int = Field(default=12, ge=0, le=200)
    background: str = "#000000"


@router.post("/export")
def export_collage(project_id: str, payload: ExportRequest):
    project = project_service.get(project_id)
    cover = next((item for item in project.screenshots if item.is_cover), None)
    if cover is None:
        raise AppError("NO_COVER_IMAGE", "尚未选择顶部封面")
    if project.roi is None:
        raise AppError("ROI_NOT_CONFIGURED", "尚未设置字幕区域")
    project_dir = project_service.project_dir(project.id)
    strips = [
        item
        for item in sorted(project.screenshots, key=lambda value: value.order)
        if item.selected and not item.is_cover
    ]
    if not strips:
        raise AppError("NO_SELECTED_STRIPS", "没有参与导出的字幕条")
    suffix = "jpg" if payload.format == "jpeg" else payload.format
    output_path = project_dir / "export" / f"collage.{suffix}"
    compose_collage_from_sources(
        cover_path=project_dir / cover.original_path,
        source_paths=[project_dir / item.original_path for item in strips],
        roi=project.roi,
        output_path=output_path,
        gap=payload.gap,
        background=parse_hex_color(payload.background),
    )
    project.export_format = suffix
    project.gap = payload.gap
    project.background = payload.background
    project_service.save(project)
    return {"download_url": f"/api/files/{project_id}/export/{output_path.name}"}
