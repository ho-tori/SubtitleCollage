from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import ALLOWED_EXTENSIONS, ALLOWED_MIME_TYPES, MAX_IMAGE_SIZE_BYTES, MAX_IMAGES_PER_PROJECT
from app.core.errors import AppError
from app.models.project import Project
from app.models.screenshot import ScreenshotItem
from app.services.project_service import project_service


class ImageService:
    async def add_images(self, project: Project, files: list[UploadFile]) -> list[ScreenshotItem]:
        if len(project.screenshots) + len(files) > MAX_IMAGES_PER_PROJECT:
            raise AppError("IMAGE_TOO_LARGE", f"每个项目最多支持 {MAX_IMAGES_PER_PROJECT} 张图片")

        added: list[ScreenshotItem] = []
        for upload in files:
            item = await self._save_upload(project, upload)
            project.screenshots.append(item)
            added.append(item)

        if project.screenshots and not any(item.is_cover for item in project.screenshots):
            project.screenshots[0].is_cover = True

        project_service.save(project)
        return added

    async def _save_upload(self, project: Project, upload: UploadFile) -> ScreenshotItem:
        source_name = upload.filename or "image"
        suffix = Path(source_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise AppError("INVALID_IMAGE_FORMAT", "仅支持 PNG、JPG、JPEG 和 WEBP 图片")
        if upload.content_type and upload.content_type not in ALLOWED_MIME_TYPES:
            raise AppError("INVALID_IMAGE_FORMAT", "图片 MIME 类型不受支持")

        image_id = str(uuid4())
        internal_name = f"{image_id}{suffix}"
        project_dir = project_service.project_dir(project.id)
        original_path = project_dir / "original" / internal_name
        await self._write_upload(upload, original_path)

        try:
            with Image.open(original_path) as image:
                image.verify()
            with Image.open(original_path) as image:
                if image.width < 16 or image.height < 16:
                    raise AppError("INVALID_IMAGE_FORMAT", "图片尺寸过小")
        except (UnidentifiedImageError, OSError) as exc:
            original_path.unlink(missing_ok=True)
            raise AppError("INVALID_IMAGE_FORMAT", "图片文件无法打开") from exc

        return ScreenshotItem(
            id=image_id,
            filename=source_name,
            order=len(project.screenshots) + 1,
            original_path=f"original/{internal_name}",
            is_cover=not project.screenshots,
        )

    async def _write_upload(self, upload: UploadFile, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        total = 0
        try:
            with target_path.open("wb") as target:
                while chunk := await upload.read(1024 * 1024):
                    total += len(chunk)
                    if total > MAX_IMAGE_SIZE_BYTES:
                        raise AppError("IMAGE_TOO_LARGE", "单张图片最大体积为 15 MB")
                    target.write(chunk)
        except Exception:
            target_path.unlink(missing_ok=True)
            raise


def delete_image_files(project: Project, item: ScreenshotItem) -> None:
    project_dir = project_service.project_dir(project.id)
    for relative in (item.original_path, item.preview_path, item.cropped_path):
        if not relative:
            continue
        path = (project_dir / relative).resolve()
        if project_dir.resolve() in path.parents:
            path.unlink(missing_ok=True)


image_service = ImageService()
