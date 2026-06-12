import json
from Model.SystemTest.ConformityAgent.Policy import TestScriptConformityPolicy
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client


class TestScriptConformityResult(ConformityResult):

    def __init__(self, valid: bool, feedback: str, coverage: list[str] = None):
        super().__init__(valid, feedback)
        self.coverage = coverage or []


class TestScriptConformityAgent:
    """
    Verifica se o Script de Teste está compatível com os Critérios de Aceite. (6.2)
    """

    def __init__(self):
        self.__policy = TestScriptConformityPolicy()
        self.__client = get_openai_client()

    def validate(self, script_content: str, acceptance_criteria: str) -> TestScriptConformityResult:
        """6.2 - Verifica se Script de Teste está Compatível com Critério de Aceite."""
        prompt = (
            f"Verifique se o seguinte Script de Teste Playwright cobre adequadamente "
            f"os Critérios de Aceite fornecidos.\n\n"
            f"Critérios de Aceite (Gherkin):\n{acceptance_criteria}\n\n"
            f"Script de Teste:\n```python\n{script_content}\n```\n\n"
            f"Para cada critério, indique se está coberto pelo script. "
            f"Avalie se as ações do script correspondem aos passos Given/When/Then."
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
        return TestScriptConformityResult(
            valid=bool(data.get("valid", False)),
            feedback=data.get("feedback", ""),
            coverage=data.get("coverage", [])
        )
