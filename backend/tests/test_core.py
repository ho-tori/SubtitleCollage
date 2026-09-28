from pathlib import Path

from PIL import Image

from app.models.roi import RoiConfig
from app.services.collage_service import calculate_crop_box, compose_collage, crop_subtitle_strip


def test_calculate_crop_box() -> None:
    image = Image.new("RGB", (1920, 1080))
    roi = RoiConfig(x=0.0, y=0.72, width=1.0, height=0.25)
    assert calculate_crop_box(image, roi) == (0, 777, 1920, 1047)


def test_crop_and_compose(tmp_path: Path) -> None:
    cover = tmp_path / "cover.png"
    strip = tmp_path / "strip.png"
    output = tmp_path / "collage.png"
    Image.new("RGB", (100, 100), (20, 20, 20)).save(cover)
    crop_subtitle_strip(cover, strip, RoiConfig(x=0, y=0.5, width=1, height=0.25))
    compose_collage(cover, [strip], output, gap=10)
    with Image.open(strip) as strip_image:
        assert strip_image.size == (100, 25)
    with Image.open(output) as output_image:
        assert output_image.size == (100, 135)
