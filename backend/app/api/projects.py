from pydantic import BaseModel
from fastapi import APIRouter

from app.services.project_service import project_service

router = APIRouter(prefix="/api/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str = "Subtitle Collage"


@router.post("")
def create_project(payload: CreateProjectRequest) -> dict[str, str]:
    project = project_service.create(payload.name)
    return {"project_id": project.id}


@router.get("/{project_id}")
def get_project(project_id: str):
    return project_service.get(project_id)

