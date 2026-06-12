_DEFAULT_PROMPT = (
    "Você é um agente de conformidade de Critérios de Aceite de software. "
    "Critérios de Aceite devem estar no formato Gherkin (Given/When/Then). "
    "Exemplo válido:\n"
    "  Given que o usuário está na página de pesquisa\n"
    "  When o usuário digita um termo e pressiona Enter\n"
    "  Then o sistema exibe os resultados da pesquisa\n\n"
    "Responda SEMPRE em JSON no formato: {\"valid\": true/false, \"feedback\": \"mensagem\"}. "
    "Verifique se contém os blocos Given, When e Then, e se descrevem um comportamento verificável. "
    "Use linguagem formal e objetiva."
)


class AcceptanceCriteriaConformityPolicy:
    DEFAULT_PROMPT = _DEFAULT_PROMPT

    def get_system_prompt(self) -> str:
        try:
            from AppSettings import get_setting
            custom = get_setting("policy_criteria").strip()
            if custom:
                return custom
        except Exception:
            pass
        return _DEFAULT_PROMPT
