from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client

def delete_file(file_id: str):
    """
    Remove um arquivo da base de conhecimento da OpenAI pelo ID.
    """
    client = get_openai_client()
    
    try:
        response = client.files.delete(file_id)
        return response.deleted
    except Exception as e:
        print(f"Erro ao deletar arquivo {file_id}: {e}")
        return False