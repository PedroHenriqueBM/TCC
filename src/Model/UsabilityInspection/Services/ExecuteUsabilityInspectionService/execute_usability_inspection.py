from pathlib import Path

from Model.UsabilityInspection.IntelligentUsabilityInspectionAgent.Policy import Policy
from Model.UsabilityInspection.IntelligentUsabilityInspectionAgent.IntelligentUsabilityInspectionAgent import IntelligentUsabilityInspectionAgent
from Model.UsabilityInspection.IntelligentUsabilityInspectionAgent.UsabilityHeuristicDatabase.UsabilityHeuristicDatabase import UsabilityHeuristicDatabase

from Model.UsabilityInspection.Exceptions.Functionality.FunctionalityNotExists import FunctionalityNotExists
from Model.UsabilityInspection.Exceptions.UsabilityHeuristicDatabase.DatasetNotExistsOnPath import DatasetNotExistsOnPath

from Model.UsabilityInspection.Services.CheckIfFunctionalityExistsService.check_if_functionality_exists import check_if_functionality_exists
from Model.UsabilityInspection.Services.GetFunctionalityByIdService.get_functionality_by_id import get_functionality_by_id
from Model.UsabilityInspection.Services.GetPathToSaveVideoService.get_path_to_save_video import get_path_to_save_video
from Model.UsabilityInspection.Services.GetLatestFileOnPathService.get_latest_file_on_path_service import get_latest_file_on_path_service

from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.check_if_file_exists_on_knowledge_database import find_file_by_name
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.upload_file import upload_file
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.delete_file import delete_file
from Model.UsabilityInspection.Repositories.ArtificialInteligentAgenteRepository.send_message_to_agent import send_message_to_agent


def execute_usability_inspection(functionality_id: str):
    # 1. Verifica se a funcionalidade existe no sistema
    functionality_exists = check_if_functionality_exists(functionality_id)

    if not functionality_exists:
        raise FunctionalityNotExists(f"The functionality with {functionality_id} id not exists")

    # 2. Busca o caminho onde o vídeo/pdf foi salvo pelo serviço de gravação
    path_to_save_video = get_path_to_save_video(functionality_id)

    # 3. Busca o arquivo PDF mais recente gerado na pasta
    record_file = get_latest_file_on_path_service(path_to_save_video)

    if not record_file or not Path(record_file).is_file():
        raise FileNotFoundError(f"Recording file not found: {record_file}")

    # 4. Busca os detalhes da funcionalidade para o contexto da IA
    functionality = get_functionality_by_id(functionality_id)
  
    # 5. Configuração da política de governança e comportamento da IA
    usability_policy = Policy(
        governance="""Você é uma IA que que realiza inspeções de usabilidade em gravações de vídeo transformadas em pdf (que simulam a execução de
uma determinada funcionalidade por parte de uma persona) utilizando as heurísticas de Nielsen e base de referência salva que contém sistemas
que se destacam no cumprimento delas. Você receberá um pdf oriundo de uma gravação e realizará a inspeção, devolvendo a resposta contendo as 
heurísticas e elementos que as ferem. Devolva no formato:

(numero) heuristica:
    - comentários
    - comentários
""",
        transparency_and_explainability="""Você deve, em cada comentário, além de dizer o elemento que fere a heurística, explicar em como chegou 
a cada conclusão.""",
        justice_and_mitigation_of_bias="""Nas suas respostas, você deve utilizar uma linguagem formal, acessível (sem paralavras complexas) e direta que
evite a discriminação de pessoas e a disseminação de preconceitos.""",
        safety_and_robustness="""Para a entrada dos dados, em caso de conteúdo indevido, ilegal (para texto e gravação) ou anômalo, devolver uma
mensagem dizendo que que a realização da inspeção está impossibilitada devido ao não cumprimento das normas de justiça.
""",
        privacy_and_data_protection="""Você deve assegurar a confidencialidade as informações inseridas, evitando vazamentos para outras conversas e
contextos"""
    )

    # 6. Inicialização da base de dados de heurísticas e do agente inteligente
    usability_heuristic_database = UsabilityHeuristicDatabase()

    intelligent_usability_inspection_agent = IntelligentUsabilityInspectionAgent(
        functionality=functionality,
        policy=usability_policy,
        usability_heuristic_database=usability_heuristic_database
    )

    # 7. Gerenciamento do Dataset de Heurísticas (Knowledge Base)
    dataset_filename = intelligent_usability_inspection_agent.usability_heuristic_database.get_name_of_dataset()
    dataset_id = find_file_by_name(dataset_filename, purpose="assistants")

    if not dataset_id:
        dataset_path = intelligent_usability_inspection_agent.usability_heuristic_database.get_path_of_dataset()

        if not Path(dataset_path).is_file():
            raise DatasetNotExistsOnPath("Dataset is missing on path setted")

        dataset_id = upload_file(
            name=dataset_filename,
            file_path=dataset_path,
            type="application/json"
        )

    # 8. Gerenciamento do Arquivo de Gravação (Sempre atualiza para a versão mais recente)
    filename_recording = f"execuction_recording_{functionality_id}.pdf"
 
    # Verifica se já existe um arquivo de gravação antigo com este nome na IA
    old_functionality_recording_id = find_file_by_name(
        filename=filename_recording,
        purpose="assistants"
    )

    # Se existir uma gravação antiga, ela é removida para evitar que a IA use dados desatualizados
    if old_functionality_recording_id:
        try:
            delete_file(old_functionality_recording_id)
        except Exception:
            # Caso ocorra erro no delete (ex: arquivo já removido manualmente), prossegue para o upload
            pass

    # Realiza o upload do novo arquivo PDF gerado nesta execução
    functionality_recording_id = upload_file(
        file_path=record_file,
        name=filename_recording,
        type="application/pdf"
    )

    # 9. Preparação dos prompts e envio para o agente
    user_prompt = intelligent_usability_inspection_agent.get_user_prompt()
    system_prompt = intelligent_usability_inspection_agent.get_system_prompt()

    response = send_message_to_agent(
        user_message=user_prompt,
        system_message=system_prompt,
        dataset_id=dataset_id,
        recording_id=functionality_recording_id
    )

    # 10. Salva o resultado da inspeção em um arquivo de texto local
    result_path = Path(path_to_save_video, "result.txt")
    with open(result_path, "w") as result_file:
            result_file.write(response)

    return response
