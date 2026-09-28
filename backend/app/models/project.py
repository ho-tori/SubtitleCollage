from pydantic import BaseModel, Field

from app.models.roi import RoiConfig
from app.models.screenshot import ScreenshotItem


class Project(BaseModel):
    id: str
    name: str
    roi: RoiConfig | None = None
    screenshots: list[ScreenshotItem] = Field(default_factory=list)
    export_format: str = "png"
    gap: int = 12
    background: str = "#000000"

