from pydantic import BaseModel


class ScreenshotItem(BaseModel):
    id: str
    filename: str
    order: int
    original_path: str
    preview_path: str | None = None
    cropped_path: str | None = None
    selected: bool = True
    is_cover: bool = False
