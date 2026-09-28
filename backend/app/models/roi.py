from pydantic import BaseModel, Field, model_validator


class RoiConfig(BaseModel):
    x: float = Field(ge=0.0, le=1.0)
    y: float = Field(ge=0.0, le=1.0)
    width: float = Field(gt=0.0, le=1.0)
    height: float = Field(gt=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_bounds(self) -> "RoiConfig":
        if self.x + self.width > 1.0:
            raise ValueError("x + width must be <= 1")
        if self.y + self.height > 1.0:
            raise ValueError("y + height must be <= 1")
        return self

