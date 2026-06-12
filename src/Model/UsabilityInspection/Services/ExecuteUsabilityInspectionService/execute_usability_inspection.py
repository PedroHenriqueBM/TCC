import uuid
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

from Database.repositories.functional_requirement_repository import get_personas_of_requirement
from Database.repositories.system_test_repository import create_usability_inspection_execution
from Database.repositories.comment_repository import create_comment, list_comments_by_entity, format_comments_as_text


def execute_usability_inspection(functionality_id: str, tester_comment: str = '') -> str:
    """
    Executa a Inspeção de Usabilidade com auxílio do agente inteligente. (7)

    7.1 - Agente consulta política
    7.2 - Agente consulta base de dados heurística
    7.3 - Agente consulta comentários anteriores
    7.4 - Agente registra carimbo de execução de inspeção
    7.5 - Agente cadastra novo comentário com a análise
    7.6 - Tester adiciona comentário (se fornecido)
    """
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

    # 4. Busca os detalhes da funcionalidade (com critérios de aceite e comentários)
    functionality = get_functionality_by_id(functionality_id)

    # 5. Busca personas associadas para contextualizar a inspeção
    personas_rows = get_personas_of_requirement(functionality_id)
    personas_text = ""
    if personas_rows:
        personas_text = "Personas associadas:\n" + "\n".join(
            f"  - {p['name']}: {p.get('description', '')} | "
            f"Necessidades: {p.get('needs', '')} | Desafios: {p.get('challenges', '')}"
            for p in personas_rows
        )

    # 7.3 - Consulta comentários anteriores de inspeção
    past_comments_rows = list_comments_by_entity('usability_inspection', functionality_id)
    previous_comments_text = format_comments_as_text(past_comments_rows)

    # 6. Configuração da política de governança e comportamento da IA (7.1)
    usability_policy = Policy(
        governance=(
            "Você é uma IA que realiza inspeções de usabilidade em gravações de vídeo transformadas "
            "em PDF (que simulam a execução de uma determinada funcionalidade por parte de uma persona) "
            "utilizando as heurísticas de Nielsen e base de referência salva que contém sistemas "
            "que se destacam no cumprimento delas. Você receberá um PDF oriundo de uma gravação e "
            "realizará a inspeção, devolvendo a resposta contendo as heurísticas e elementos que as ferem. "
            "Devolva no formato:\n\n(numero) heuristica:\n    - comentários\n    - comentários\n"
        ),
        transparency_and_explainability=(
            "Você deve, em cada comentário, além de dizer o elemento que fere a heurística, "
            "explicar como chegou a cada conclusão."
        ),
        justice_and_mitigation_of_bias=(
            "Nas suas respostas, utilize linguagem formal, acessível (sem palavras complexas) e direta "
            "que evite a discriminação de pessoas e a disseminação de preconceitos."
        ),
        safety_and_robustness=(
            "Para a entrada dos dados, em caso de conteúdo indevido, ilegal ou anômalo, devolver uma "
            "mensagem dizendo que a realização da inspeção está impossibilitada devido ao não "
            "cumprimento das normas de justiça."
        ),
        privacy_and_data_protection=(
            "Você deve assegurar a confidencialidade das informações inseridas, evitando vazamentos "
            "para outras conversas e contextos."
        )
    )

    # 7.2 - Inicialização da base de dados de heurísticas e do agente inteligente
    usability_heuristic_database = UsabilityHeuristicDatabase()
    intelligent_usability_inspection_agent = IntelligentUsabilityInspectionAgent(
        functionality=functionality,
        policy=usability_policy,
        usability_heuristic_database=usability_heuristic_database
    )

    # Enriquece o prompt do usuário com personas e comentários anteriores
    user_prompt = intelligent_usability_inspection_agent.get_user_prompt()
    if personas_text:
        user_prompt = user_prompt + f"\n\n{personas_text}"
    if previous_comments_text:
        user_prompt = user_prompt + f"\n\nComentários anteriores do Tester:\n{previous_comments_text}"

    system_prompt = intelligent_usability_inspection_agent.get_system_prompt()

    # Gerenciamento do Dataset de Heurísticas (Knowledge Base)
    dataset_filename = intelligent_usability_inspection_agent.usability_heuristic_database.get_name_of_dataset()
    dataset_id = find_file_by_name(dataset_filename, purpose="assistants")

    if not dataset_id:
        dataset_path = intelligent_usability_inspection_agent.usability_heuristic_database.get_path_of_dataset()
        if not Path(dataset_path).is_file():
            raise DatasetNotExistsOnPath("Dataset is missing on path setted")
        dataset_id = upload_file(name=dataset_filename, file_path=dataset_path, type="application/json")

    # Gerenciamento do Arquivo de Gravação (sempre usa a versão mais recente)
    filename_recording = f"execuction_recording_{functionality_id}.pdf"
    old_recording_id = find_file_by_name(filename=filename_recording, purpose="assistants")
    if old_recording_id:
        try:
            delete_file(old_recording_id)
        except Exception:
            pass

    functionality_recording_id = upload_file(
        file_path=record_file,
        name=filename_recording,
        type="application/pdf"
    )

    # Envia para o agente e obtém resposta
    response = send_message_to_agent(
        user_message=user_prompt,
        system_message=system_prompt,
        dataset_id=dataset_id,
        recording_id=functionality_recording_id
    )

    # 7.4 - Registra carimbo de execução de inspeção no banco de dados
    execution_id = str(uuid.uuid4())
    create_usability_inspection_execution(
        id=execution_id,
        requirement_id=functionality_id,
        result_text=response,
        recording_path=record_file
    )

    # 7.5 - Cadastra novo comentário com a análise da inspeção
    create_comment(
        id=str(uuid.uuid4()),
        entity_type='usability_inspection',
        entity_id=functionality_id,
        content=response,
        author='Agente Inteligente de Inspeção de Usabilidade'
    )

    # 7.6 - Adiciona comentário do tester, caso fornecido
    if tester_comment:
        create_comment(
            id=str(uuid.uuid4()),
            entity_type='usability_inspection',
            entity_id=functionality_id,
            content=tester_comment,
            author='Tester'
        )

    # Salva o resultado em arquivo local (compatibilidade com fluxo existente)
    result_path = Path(path_to_save_video, "result.txt")
    with open(result_path, "w", encoding='utf-8') as result_file:
        result_file.write(response)

    return response
