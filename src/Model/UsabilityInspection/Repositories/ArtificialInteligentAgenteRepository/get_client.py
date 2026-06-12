import os
from openai import OpenAI


def get_openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()

    if not api_key:
        try:
            from AppSettings import get_setting
            api_key = get_setting("openai_api_key")
        except ImportError:
            pass

    if not api_key:
        raise EnvironmentError(
            "Chave da API OpenAI não configurada. "
            "Acesse Configurações na interface para adicionar sua chave."
        )
    return OpenAI(api_key=api_key)
