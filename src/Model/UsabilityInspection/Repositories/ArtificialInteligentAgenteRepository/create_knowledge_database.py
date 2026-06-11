from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client

def create_knowledge_database(knowledge_database_name: str):

    client = get_openai_client()
    vector_store = client.vector_stores.create(
        name=knowledge_database_name
    )
    return vector_store.id

