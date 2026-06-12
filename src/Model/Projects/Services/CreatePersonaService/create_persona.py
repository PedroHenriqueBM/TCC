import uuid
from Model.Projects.Persona.Persona import Persona
from Model.Projects.ConformityAgents.PersonaConformityAgent.PersonaConformityAgent import PersonaConformityAgent
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Database.repositories.project_repository import project_exists
from Database.repositories.persona_repository import create_persona as db_create_persona


class PersonaConformityError(Exception):
    def __init__(self, results: list[ConformityResult]):
        self.results = results
        messages = [r.feedback for r in results if not r.valid]
        super().__init__("Persona não atende aos critérios de conformidade: " + " | ".join(messages))


class ProjectNotFoundError(Exception):
    pass


def create_persona(project_id: str, name: str, opportunities: str, key_attributes: str,
                   description: str, needs: str, challenges: str) -> Persona:
    """
    Cria uma Persona em um Projeto após validação. (2)
    - 2.1: Consulta política do agente
    - 2.2-2.7: Verifica todos os campos
    """
    if not project_exists(project_id):
        raise ProjectNotFoundError(f"Projeto '{project_id}' não encontrado.")

    agent = PersonaConformityAgent()

    # 2.2-2.7: Valida todos os campos
    results = agent.validate_all(
        name=name,
        opportunities=opportunities,
        key_attributes=key_attributes,
        description=description,
        needs=needs,
        challenges=challenges
    )

    failures = [r for r in results if not r.valid]
    if failures:
        raise PersonaConformityError(results)

    persona_id = str(uuid.uuid4())
    db_create_persona(
        id=persona_id, project_id=project_id, name=name,
        opportunities=opportunities, key_attributes=key_attributes,
        description=description, needs=needs, challenges=challenges
    )

    return Persona(
        id=persona_id, project_id=project_id, name=name,
        opportunities=opportunities, key_attributes=key_attributes,
        description=description, needs=needs, challenges=challenges
    )
