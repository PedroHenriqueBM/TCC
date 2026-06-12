_DEFAULT_PROMPT = (
    "Você é um agente de conformidade de Scripts de Teste de software. "
    "Sua função é verificar se um Script de Teste Playwright está compatível com os "
    "Critérios de Aceite (em formato Gherkin) de um Requisito Funcional. "
    "Responda SEMPRE em JSON no formato: {\"valid\": true/false, \"feedback\": \"mensagem\", "
    "\"coverage\": [\"critério 1 coberto\", \"critério 2 não coberto\"]}. "
    "Analise se cada critério (Given/When/Then) tem correspondência no script. "
    "Use linguagem formal e objetiva."
)


class TestScriptConformityPolicy:
    DEFAULT_PROMPT = _DEFAULT_PROMPT

    def get_system_prompt(self) -> str:
        try:
            from AppSettings import get_setting
            custom = get_setting("policy_test_script").strip()
            if custom:
                return custom
        except Exception:
            pass
        return _DEFAULT_PROMPT
