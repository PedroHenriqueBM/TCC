from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client

def find_file_by_name(filename: str, purpose: str | None = None):

    client = get_openai_client()

    files = client.files.list(
        purpose=purpose if purpose else None,
        order="desc",
        limit=10000
    )

    for f in files.data:
        if f.filename == filename:
            return f.id

    return None