from Model.Projects.Project.Project import Project
from Database.repositories.project_repository import get_project_by_id, list_projects


def get_project(project_id: str) -> Project | None:
    data = get_project_by_id(project_id)
    if not data:
        return None
    return Project.from_dict(data)


def get_all_projects() -> list[Project]:
    rows = list_projects()
    return [Project.from_dict(r) for r in rows]
