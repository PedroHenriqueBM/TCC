from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client

def save_file_on_know_on_knowledge_database(
        knowledge_id: str,
        file_id: str,
        doc_key: str,
        client_metadata: str,
        version: int,
        category: str
    ):

    client = get_openai_client()

    client.vector_stores.files.create(
        vector_store_id=knowledge_id,
        file_id=file_id,
        attributes={
            "doc_key": doc_key,
            "cliente": client_metadata,
            "versao": version,
            "categoria": category
        }
    )

