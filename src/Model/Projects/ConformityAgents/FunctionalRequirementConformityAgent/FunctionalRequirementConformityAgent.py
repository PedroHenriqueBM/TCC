import json
from Model.Projects.ConformityAgents.FunctionalRequirementConformityAgent.Policy import FunctionalRequirementConformityPolicy
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client


class FunctionalRequirementConformityAgent:
    """
    Verifica se o Requisito Funcional está no formato ARO (Ator + Requisito + Objeto). (3.2)
    Exemplo ARO: "O Tester executa o Script de Teste"
    """

    def __init__(self):
        self.__policy = FunctionalRequirementConformityPolicy()
        self.__client = get_openai_client()

    def validate_name(self, name: str) -> ConformityResult:
        """Verifica se o nome do Requisito Funcional está no formato ARO. (3.2)"""
        prompt = (
            f"Valide se o seguinte Requisito Funcional está no formato ARO "
            f"(Ator + Requisito/Verbo + Objeto).\n"
            f"O formato ARO exige:\n"
            f"  - Ator: quem realiza a ação (ex: 'O usuário', 'O sistema', 'O Tester')\n"
            f"  - Requisito/Verbo: a ação realizada (ex: 'executa', 'visualiza', 'cadastra')\n"
            f"  - Objeto: o alvo da ação (ex: 'o relatório', 'os dados', 'o perfil')\n\n"
            f"Requisito Funcional: \"{name}\"\n\n"
            f"Indique se está no formato ARO, identificando cada componente, "
            f"ou explique o que está faltando."
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
