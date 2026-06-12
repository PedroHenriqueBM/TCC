import json
from Model.Projects.ConformityAgents.AcceptanceCriteriaConformityAgent.Policy import AcceptanceCriteriaConformityPolicy
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client


class AcceptanceCriteriaConformityAgent:
    """
    Verifica se o Critério de Aceite é válido e está no formato Gherkin. (4.2)
    """

    def __init__(self):
        self.__policy = AcceptanceCriteriaConformityPolicy()
        self.__client = get_openai_client()

    def validate(self, content: str) -> ConformityResult:
        """Verifica se o Critério de Aceite é válido e está no formato Gherkin. (4.2)"""
        prompt = (
            f"Valide se o seguinte Critério de Aceite está no formato Gherkin.\n"
            f"O formato Gherkin requer:\n"
            f"  - Given (Dado que): a pré-condição do cenário\n"
            f"  - When (Quando): a ação realizada pelo usuário\n"
            f"  - Then (Então): o resultado esperado verificável\n\n"
            f"Critério de Aceite:\n\"{content}\"\n\n"
            f"Verifique se os três blocos estão presentes e se descrevem um comportamento claro e testável."
        )
        response = self.__client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.__policy.get_system_prompt()},
                {"role": "user", "content": prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        return ConformityResult(valid=bool(data.get("valid", False)), feedback=data.get("feedback", ""))
