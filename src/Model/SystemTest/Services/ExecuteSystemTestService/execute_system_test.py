import shutil
import uuid
import os
from pathlib import Path

from Model.SystemTest.IntelligentSystemTestAgent.IntelligentSystemTestAgent import IntelligentSystemTestAgent
from Model.SystemTest.SystemTestExecution.SystemTestExecution import SystemTestExecution

from Database.repositories.functional_requirement_repository import (
    get_functional_requirement_by_id,
    functional_requirement_exists,
)
from Database.repositories.acceptance_criteria_repository import list_acceptance_criteria_by_requirement
from Database.repositories.system_test_repository import (
    create_system_test_execution,
    list_system_test_executions_by_requirement,
)
from Database.repositories.comment_repository import (
    create_comment,
    list_comments_by_entity,
    format_comments_as_text,
)


class RequirementNotFoundError(Exception):
    pass


class ScriptNotFoundError(Exception):
    pass


def _storage_dir(requirement_id: str) -> Path:
    return Path(os.getcwd()) / "src" / "Storage" / requirement_id


def _get_script_path(requirement_id: str) -> Path:
    return _storage_dir(requirement_id) / f"execuction_recording_{requirement_id}.py"


def _get_pdf_path(requirement_id: str) -> Path | None:
    d = _storage_dir(requirement_id)
    if not d.exists():
        return None
    pdfs = sorted(d.glob("*.pdf"))
    return pdfs[-1] if pdfs else None


def execute_system_test(requirement_id: str, tester_comment: str = "") -> SystemTestExecution:
    """
    Executa o Teste de Sistema com auxílio de agente inteligente.

    Fluxo:
    1. Executa o script de teste com gravação de vídeo (contexto do que foi feito)
    2. Salva o vídeo no Storage para download
    3. O agente analisa VISUALMENTE o PDF da gravação + critérios de aceite → passed/failed
    4. Registra execução, avaliação e comentários
    """
    if not functional_requirement_exists(requirement_id):
        raise RequirementNotFoundError(f"Requisito Funcional '{requirement_id}' não encontrado.")

    req_data = get_functional_requirement_by_id(requirement_id)

    criteria_rows = list_acceptance_criteria_by_requirement(requirement_id)
    acceptance_criteria_text = (
        "\n".join(f"- {ac['content']}" for ac in criteria_rows)
        if criteria_rows
        else "(Nenhum critério de aceite cadastrado)"
    )

    script_path = _get_script_path(requirement_id)
    if not script_path.is_file():
        raise ScriptNotFoundError(
            f"Script de teste não encontrado em {script_path}. "
            "Execute a gravação primeiro."
        )

    recording_pdf = _get_pdf_path(requirement_id)

    print(f"\n{'='*50}")
    print(f"TESTE DE SISTEMA: {req_data['name']}")
    print(f"{'='*50}")

    agent = IntelligentSystemTestAgent()
    agent.consults_policy()

    past_comments_rows = list_comments_by_entity("system_test", requirement_id)
    previous_comments = format_comments_as_text(past_comments_rows)

    # Pre-allocate execution ID so the video dir name is stable
    execution_id = str(uuid.uuid4())
    video_tmp_dir = _storage_dir(requirement_id) / f"_vtmp_{execution_id}"
    video_tmp_dir.mkdir(parents=True, exist_ok=True)

    # ── 1. Execute script and record video ───────────────────────────────────
    print("  -> Executando script de teste (com gravação de vídeo)...")
    result = agent.run_test_with_retry(
        script_path=str(script_path),
        acceptance_criteria=acceptance_criteria_text,
        video_output_dir=str(video_tmp_dir),
    )
    if result.rewritten:
        print("  -> Script reescrito pela IA e re-executado.")

    # ── 2. Move video to stable path in Storage ───────────────────────────────
    final_video_path: str | None = None
    if result.video_path and Path(result.video_path).exists():
        dest = _storage_dir(requirement_id) / f"test_video_{execution_id}.webm"
        shutil.move(str(result.video_path), str(dest))
        final_video_path = str(dest)
        print(f"  -> Vídeo salvo: {dest.name}")
    shutil.rmtree(str(video_tmp_dir), ignore_errors=True)

    # ── 3. Evaluate using PDF (primary) or script output (fallback) ───────────
    script_content = script_path.read_text(encoding="utf-8")

    if recording_pdf and recording_pdf.is_file():
        print(f"  -> Avaliando resultado via PDF ({recording_pdf.name})...")
        agent_comment, ai_passed = agent.evaluate_with_pdf(
            pdf_path=str(recording_pdf),
            requirement_name=req_data["name"],
            acceptance_criteria=acceptance_criteria_text,
            script_content=script_content,
            previous_comments=previous_comments,
        )
    else:
        print("  -> PDF de gravação não encontrado. Avaliando via saída do script...")
        agent_comment, ai_passed = agent.generate_evaluation_comment(
            requirement_name=req_data["name"],
            acceptance_criteria=acceptance_criteria_text,
            returncode_passed=result.passed,
            stdout=result.stdout,
            stderr=result.stderr,
            previous_comments=previous_comments,
        )

    status_label = "PASSOU ✓" if ai_passed else "FALHOU ✗"
    print(f"  -> Resultado: {status_label}")

    # ── 4. Persist execution and comments ────────────────────────────────────
    script_output = result.stdout or result.stderr or ""
    result_text = f"=== AVALIAÇÃO DO AGENTE ===\n{agent_comment}"
    if script_output:
        result_text += f"\n\n=== SAÍDA DO SCRIPT ===\n{script_output}"

    execution_data = create_system_test_execution(
        id=execution_id,
        requirement_id=requirement_id,
        passed=ai_passed,
        result_text=result_text,
        script_path=str(script_path),
        video_path=final_video_path,
    )

    create_comment(
        id=str(uuid.uuid4()),
        entity_type="system_test",
        entity_id=requirement_id,
        content=agent_comment,
        author="Agente Inteligente de Teste de Sistema",
    )

    if tester_comment:
        create_comment(
            id=str(uuid.uuid4()),
            entity_type="system_test",
            entity_id=requirement_id,
            content=tester_comment,
            author="Tester",
        )

    print(f"\nAvaliação do Agente:\n{agent_comment}")
    print(f"{'='*50}\n")

    return SystemTestExecution.from_dict(execution_data)
