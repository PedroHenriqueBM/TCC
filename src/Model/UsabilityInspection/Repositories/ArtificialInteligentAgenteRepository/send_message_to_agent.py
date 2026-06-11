from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.get_client import get_openai_client

def send_message_to_agent(
        user_message: str, 
        system_message: str,
        dataset_id: str,
        recording_id: str
    ) -> str:

    client = get_openai_client()
  
    response = client.responses.create(
        model="gpt-5.4",
        input=[
            {
                "role": "system",
                "content": system_message
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_message
                    },
                    {
                        "type": "input_file",
                        "file_id": dataset_id
                    },
                    {
                        "type": "input_file",
                        "file_id": recording_id
                    }
                ]
            }
        ]
    )

    return response.output_text
