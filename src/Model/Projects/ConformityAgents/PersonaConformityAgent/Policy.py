_DEFAULT_PROMPT = (
    "Você é um agente de conformidade de Personas de software. "
    "Personas são representações de perfis de usuários que interagem com sistemas. "
    "Sua função é validar se cada campo de uma Persona está dentro dos padrões esperados. "
    "Responda SEMPRE em JSON no formato: {\"valid\": true/false, \"feedback\": \"mensagem\"}. "
    "Use linguagem formal, objetiva e sem discriminação. "
    "Em caso de conteúdo inapropriado ou ilegal, retorne valid=false com feedback explicativo."
)


class PersonaConformityPolicy:
    DEFAULT_PROMPT = _DEFAULT_PROMPT

    def get_system_prompt(self) -> str:
        try:
            from AppSettings import get_setting
            custom = get_setting("policy_persona").strip()
            if custom:
                return custom
        except Exception:
            pass
        return _DEFAULT_PROMPT
