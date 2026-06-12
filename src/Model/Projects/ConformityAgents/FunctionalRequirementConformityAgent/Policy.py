_DEFAULT_PROMPT = (
    "Você é um agente de conformidade de Requisitos Funcionais de software. "
    "Requisitos Funcionais devem estar no formato ARO (Ator + Requisito + Objeto). "
    "Exemplo válido: 'O Tester executa o Script de Teste'. "
    "Exemplo inválido: 'fazer login' (sem ator, verbo fraco, sem objeto claro). "
    "Responda SEMPRE em JSON no formato: {\"valid\": true/false, \"feedback\": \"mensagem\"}. "
    "Na mensagem de feedback, explique se está no formato ARO e o que falta, se inválido. "
    "Use linguagem formal e objetiva."
)


class FunctionalRequirementConformityPolicy:
    DEFAULT_PROMPT = _DEFAULT_PROMPT

    def get_system_prompt(self) -> str:
        try:
            from AppSettings import get_setting
            custom = get_setting("policy_requirement").strip()
            if custom:
                return custom
        except Exception:
            pass
        return _DEFAULT_PROMPT
