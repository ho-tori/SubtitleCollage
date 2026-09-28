import json
from pathlib import Path
from threading import Lock, RLock
from uuid import uuid4

from pydantic import ValidationError

from app.core.config import PROJECTS_DIR
from app.core.errors import AppError
from app.models.project import Project


class ProjectService:
    def __init__(self) -> None:
        self._locks: dict[str, RLock] = {}
        self._locks_guard = Lock()

    def create(self, name: str) -> Project:
        project = Project(id=str(uuid4()), name=name.strip() or "Untitled Project")
        self.project_dir(project.id).mkdir(parents=True, exist_ok=True)
        for folder in ("original", "cropped", "preview", "export"):
            (self.project_dir(project.id) / folder).mkdir(exist_ok=True)
        self.save(project)
        return project

    def get(self, project_id: str) -> Project:
        path = self.project_file(project_id)
        if not path.exists():
            raise AppError("PROJECT_NOT_FOUND", "项目不存在", 404)
        with self._project_lock(project_id):
            raw = path.read_text(encoding="utf-8")
            try:
                return Project.model_validate_json(raw)
            except (ValidationError, ValueError) as exc:
                recovered = self._recover_project_json(path, raw)
                if recovered is not None:
                    return recovered
                raise AppError("PROJECT_FILE_INVALID", "项目文件损坏，请新建项目或恢复 project.json", 500) from exc

    def save(self, project: Project) -> None:
        with self._project_lock(project.id):
            self.project_dir(project.id).mkdir(parents=True, exist_ok=True)
            payload = json.dumps(project.model_dump(mode="json"), ensure_ascii=False, indent=2)
            target = self.project_file(project.id)
            temp = target.with_suffix(".json.tmp")
            try:
                temp.write_text(payload, encoding="utf-8")
                temp.replace(target)
            except OSError:
                target.write_text(payload, encoding="utf-8")

    def project_dir(self, project_id: str) -> Path:
        return PROJECTS_DIR / project_id

    def project_file(self, project_id: str) -> Path:
        return self.project_dir(project_id) / "project.json"

    def _project_lock(self, project_id: str) -> RLock:
        with self._locks_guard:
            if project_id not in self._locks:
                self._locks[project_id] = RLock()
            return self._locks[project_id]

    def _recover_project_json(self, path: Path, raw: str) -> Project | None:
        decoder = json.JSONDecoder()
        try:
            payload, _ = decoder.raw_decode(raw)
            project = Project.model_validate(payload)
        except Exception:
            return None

        backup = path.with_suffix(".json.bak")
        try:
            if not backup.exists():
                backup.write_text(raw, encoding="utf-8")
        except OSError:
            pass
        self.save(project)
        return project


project_service = ProjectService()
