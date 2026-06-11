from openai import OpenAI


def get_openai_client():
    client = OpenAI(api_key="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")
    return client