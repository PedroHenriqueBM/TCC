import json
from Model.Projects.ConformityAgents.PersonaConformityAgent.Policy import PersonaConformityPolicy
from Model.Projects.ConformityAgents.ConformityResult import ConformityResult
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client


class PersonaConformityAgent:

    def __init__(self):
        self.__policy = PersonaConformityPolicy()
        self.__client = get_openai_client()

    def __ask(self, user_prompt: str) -> ConformityResult:
        response = self.__client.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": self.__policy.get_system_prompt()},
                {"role": "user", "content": user_prompt}
            ]
        )
        data = json.loads(response.choices[0].message.content)
        return ConformityResult(valid=bool(data.get("valid", False)), feedback=data.get("feedback", ""))

    def validate_name(self, name: str) -> ConformityResult:
        """Verifica se o nome da Persona é válido. (2.3)"""
        return self.__ask(
            f"Valide se o nome de uma Persona é válido.\n"
            f"Regras: deve ser não vazio, ter entre 2 e 100 caracteres, "
            f"representar um perfil de pessoa de forma respeitosa.\n"
            f"Nome: \"{name}\""
        )

    def validate_opportunities(self, opportunities: str) -> ConformityResult:
        """Verifica se as oportunidades da Persona são válidas. (2.2)"""
        return self.__ask(
            f"Valide se o campo 'oportunidades' de uma Persona está adequado.\n"
            f"Oportunidades descrevem como o sistema pode ajudar o perfil.\n"
            f"Regras: deve ser não vazio, claro, objetivo e relacionado ao contexto de software.\n"
            f"Oportunidades: \"{opportunities}\""
        )

    def validate_key_attributes(self, key_attributes: str) -> ConformityResult:
        """Verifica se os atributos-chave da Persona são válidos. (2.4)"""
        return self.__ask(
            f"Valide se o campo 'atributos-chave' de uma Persona está adequado.\n"
            f"Atributos-chave definem características do perfil (ex: idade, profissão, nível técnico).\n"
            f"Regras: deve ser não vazio, descritivo e relevante.\n"
            f"Atributos-chave: \"{key_attributes}\""
        )

    def validate_description(self, description: str) -> ConformityResult:
        """Verifica se a descrição da Persona é válida. (2.5)"""
        return self.__ask(
            f"Valide se a descrição de uma Persona está adequada.\n"
            f"Regras: deve descrever o perfil de forma clara, com pelo menos 10 caracteres.\n"
            f"Descrição: \"{description}\""
        )

    def validate_needs(self, needs: str) -> ConformityResult:
        """Verifica se as necessidades da Persona são válidas. (2.6)"""
        return self.__ask(
            f"Valide se o campo 'necessidades' de uma Persona está adequado.\n"
            f"Necessidades descrevem o que o perfil precisa que o sistema ofereça.\n"
            f"Regras: deve ser não vazio, claro e contextualizado.\n"
            f"Necessidades: \"{needs}\""
        )

    def validate_challenges(self, challenges: str) -> ConformityResult:
        """Verifica se os desafios da Persona são válidos. (2.7)"""
        return self.__ask(
            f"Valide se o campo 'desafios' de uma Persona está adequado.\n"
            f"Desafios descrevem dificuldades que o sistema testado enfrenta para atender o perfil.\n"
            f"Regras: deve ser não vazio, claro e realista.\n"
            f"Desafios: \"{challenges}\""
        )

    def validate_all(self, name: str, opportunities: str, key_attributes: str,
                     description: str, needs: str, challenges: str) -> list[ConformityResult]:
        """Valida todos os campos da Persona de uma vez. (2.1-2.7)"""
        return [
            self.validate_name(name),
            self.validate_opportunities(opportunities),
            self.validate_key_attributes(key_attributes),
            self.validate_description(description),
            self.validate_needs(needs),
            self.validate_challenges(challenges)
        ]
