from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client

def upload_file(name:str, file_path:str, type: str):
    client = get_openai_client()
    file_uploaded = client.files.create(
        file=(name, open(file_path,"rb"),type),
        purpose="assistants"
    )
    return file_uploaded.id