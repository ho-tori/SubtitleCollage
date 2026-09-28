from pathlib import Path

from PIL import Image

from app.core.config import MAX_EXPORT_PIXELS
from app.core.errors import AppError
from app.models.roi import RoiConfig


def calculate_crop_box(image: Image.Image, roi: RoiConfig) -> tuple[int, int, int, int]:
    image_width, image_height = image.size
    left = int(image_width * roi.x)
    top = int(image_height * roi.y)
    right = int(image_width * (roi.x + roi.width))
    bottom = int(image_height * (roi.y + roi.height))
    if left < 0 or top < 0 or right > image_width or bottom > image_height or left >= right or top >= bottom:
        raise AppError("INVALID_ROI", "字幕区域无效")
    return left, top, right, bottom


def crop_subtitle_strip(source_path: Path, target_path: Path, roi: RoiConfig) -> None:
    with Image.open(source_path) as image:
        subtitle_strip = image.crop(calculate_crop_box(image, roi)).convert("RGB")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        subtitle_strip.save(target_path, format="PNG")


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    if image.width == width:
        return image
    ratio = width / image.width
    new_height = max(1, int(image.height * ratio))
    return image.resize((width, new_height), Image.Resampling.LANCZOS)


def parse_hex_color(value: str) -> tuple[int, int, int]:
    clean = value.strip().lstrip("#")
    if len(clean) != 6:
        raise AppError("EXPORT_FAILED", "背景色必须是 6 位 HEX 颜色")
    try:
        return tuple(int(clean[index : index + 2], 16) for index in (0, 2, 4))
    except ValueError as exc:
        raise AppError("EXPORT_FAILED", "背景色格式无效") from exc


def compose_collage(
    cover_path: Path,
    strip_paths: list[Path],
    output_path: Path,
    gap: int = 12,
    background: tuple[int, int, int] = (0, 0, 0),
    quality: int = 95,
) -> None:
    with Image.open(cover_path) as cover_source:
        cover = cover_source.convert("RGB")
    canvas_width = cover.width
    strips: list[Image.Image] = []
    for strip_path in strip_paths:
        with Image.open(strip_path) as strip_source:
            strips.append(resize_to_width(strip_source.convert("RGB"), canvas_width))
    total_height = cover.height + sum(gap + strip.height for strip in strips)
    canvas = Image.new("RGB", (canvas_width, total_height), background)
    current_y = 0
    canvas.paste(cover, (0, current_y))
    current_y += cover.height
    for strip in strips:
        current_y += gap
        canvas.paste(strip, (0, current_y))
        current_y += strip.height
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        canvas.save(output_path, quality=quality)
    else:
        canvas.save(output_path, format="PNG")


def compose_collage_from_sources(
    cover_path: Path,
    source_paths: list[Path],
    roi: RoiConfig,
    output_path: Path,
    gap: int = 12,
    background: tuple[int, int, int] = (0, 0, 0),
    quality: int = 95,
) -> None:
    with Image.open(cover_path) as cover_source:
        cover = cover_source.convert("RGB")

    canvas_width = cover.width
    strip_heights: list[int] = []
    for source_path in source_paths:
        with Image.open(source_path) as source:
            left, top, right, bottom = calculate_crop_box(source, roi)
            strip_width = right - left
            strip_height = bottom - top
            scaled_height = strip_height if strip_width == canvas_width else max(1, int(strip_height * (canvas_width / strip_width)))
            strip_heights.append(scaled_height)

    total_height = cover.height + sum(gap + height for height in strip_heights)
    if canvas_width * total_height > MAX_EXPORT_PIXELS:
        cover.close()
        raise AppError("EXPORT_TOO_LARGE", "导出图片尺寸过大，请减少图片数量或字幕高度")
    canvas = Image.new("RGB", (canvas_width, total_height), background)
    current_y = 0
    canvas.paste(cover, (0, current_y))
    current_y += cover.height
    cover.close()

    for source_path in source_paths:
        with Image.open(source_path) as source:
            strip = source.crop(calculate_crop_box(source, roi)).convert("RGB")
            strip = resize_to_width(strip, canvas_width)
        current_y += gap
        canvas.paste(strip, (0, current_y))
        current_y += strip.height
        strip.close()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.suffix.lower() in {".jpg", ".jpeg"}:
        canvas.save(output_path, quality=quality)
    else:
        canvas.save(output_path, format="PNG")
