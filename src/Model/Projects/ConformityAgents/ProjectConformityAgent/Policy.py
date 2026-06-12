_DEFAULT_PROMPT = (
    "Você é um agente de conformidade de Projetos de qualidade de software. "
    "Sua função é validar se os campos de um Projeto estão dentro dos padrões esperados. "
    "Responda SEMPRE em JSON no formato: {\"valid\": true/false, \"feedback\": \"mensagem\"}. "
    "Seja objetivo e use linguagem formal e acessível. "
    "Não invente regras além das solicitadas. "
    "Em caso de conteúdo inapropriado ou ilegal, retorne valid=false com feedback explicativo."
)


class ProjectConformityPolicy:
    DEFAULT_PROMPT = _DEFAULT_PROMPT

    def get_system_prompt(self) -> str:
        try:
            from AppSettings import get_setting
            custom = get_setting("policy_project").strip()
            if custom:
                return custom
        except Exception:
            pass
        return _DEFAULT_PROMPT
