import uuid
from Model.Projects.ConformityAgents.AcceptanceCriteriaConformityAgent.AcceptanceCriteriaConformityAgent import AcceptanceCriteriaConformityAgent
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Database.repositories.functional_requirement_repository import functional_requirement_exists
from Database.repositories.acceptance_criteria_repository import create_acceptance_criteria as db_create


class AcceptanceCriteriaConformityError(Exception):
    def __init__(self, result: ConformityResult):
        self.result = result
        super().__init__(f"Critério de Aceite inválido: {result.feedback}")


class FunctionalRequirementNotFoundError(Exception):
    pass


def create_acceptance_criteria(requirement_id: str, content: str, author: str = '') -> dict:
    """
    Cria um Critério de Aceite para um Requisito Funcional. (4)
    - 4.1: Consulta política do agente
    - 4.2: Verifica se está no formato Gherkin
    """
    if not functional_requirement_exists(requirement_id):
        raise FunctionalRequirementNotFoundError(f"Requisito Funcional '{requirement_id}' não encontrado.")

    # 4.2 - Verifica formato Gherkin
    agent = AcceptanceCriteriaConformityAgent()
    result = agent.validate(content)

    if not result.valid:
        raise AcceptanceCriteriaConformityError(result)

    ac_id = str(uuid.uuid4())
    return db_create(id=ac_id, requirement_id=requirement_id, content=content, author=author)
