from Model.UsabilityInspection.Functionality.Functionality import Funcionality
from Database.repositories.functional_requirement_repository import (
    get_functional_requirement_by_id,
    get_personas_of_requirement
)
from Database.repositories.acceptance_criteria_repository import list_acceptance_criteria_by_requirement
from Database.repositories.comment_repository import list_comments_by_entity


def get_functionality_by_id(functionality_id: str) -> Funcionality | None:
    data = get_functional_requirement_by_id(functionality_id)
    if not data:
        return None

    # 'name' no BD corresponde ao campo 'description' da Funcionality (texto ARO do requisito)
    functionality = Funcionality(
        id=data['id'],
        description=data['name'],
        url=data.get('url', '')
    )

    # Popula critérios de aceite vindos do banco
    criteria_rows = list_acceptance_criteria_by_requirement(functionality_id)
    for ac in criteria_rows:
        functionality.add_acceptance_criteria(
            id=ac['id'],
            description=ac['content'],
            author=ac.get('author', ''),
            timestamp=ac.get('created_at', '')
        )

    # Popula comentários de inspeção de usabilidade anteriores
    comment_rows = list_comments_by_entity('usability_inspection', functionality_id)
    for c in comment_rows:
        functionality.add_comment(
            id=c['id'],
            description=c['content'],
            author=c.get('author', ''),
            timestamp=c.get('created_at', '')
        )

    return functionality
