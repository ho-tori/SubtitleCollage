import argparse
from pathlib import Path

from app.models.roi import RoiConfig
from app.services.collage_service import compose_collage, crop_subtitle_strip


def parse_roi(value: str) -> RoiConfig:
    parts = [float(part) for part in value.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError("ROI must be x,y,width,height")
    return RoiConfig(x=parts[0], y=parts[1], width=parts[2], height=parts[3])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--cover", required=True, type=Path)
    parser.add_argument("--roi", required=True, type=parse_roi)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--gap", default=12, type=int)
    args = parser.parse_args()

    image_paths = sorted(
        path
        for path in args.input.iterdir()
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
    )
    cropped_dir = args.output.parent / "cropped"
    strip_paths: list[Path] = []
    for index, source in enumerate(image_paths, start=1):
        target = cropped_dir / f"{index:03d}.png"
        crop_subtitle_strip(source, target, args.roi)
        strip_paths.append(target)

    compose_collage(args.cover, strip_paths, args.output, gap=args.gap)
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()

