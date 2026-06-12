from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file, Response
from pathlib import Path
from datetime import datetime
import os

from AppSettings import get_setting, set_setting

from Database.database import initialize_database
from Database.repositories.project_repository import (
    list_projects, get_project_by_id, update_project, delete_project,
)
from Database.repositories.persona_repository import (
    list_personas_by_project, get_persona_by_id, update_persona, delete_persona,
)
from Database.repositories.functional_requirement_repository import (
    list_functional_requirements_by_project, get_functional_requirement_by_id,
    get_personas_of_requirement, update_functional_requirement, delete_functional_requirement,
)
from Database.repositories.acceptance_criteria_repository import (
    list_acceptance_criteria_by_requirement, get_acceptance_criteria_by_id,
    update_acceptance_criteria, delete_acceptance_criteria,
)
from Database.repositories.system_test_repository import (
    list_system_test_executions_by_requirement,
    list_usability_inspection_executions_by_requirement,
)
from Database.repositories.comment_repository import list_comments_by_entity

from Model.Projects.Services.CreateProjectService.create_project import (
    create_project, ProjectConformityError,
)
from Model.Projects.Services.CreatePersonaService.create_persona import (
    create_persona, PersonaConformityError,
)
from Model.Projects.Services.CreateFunctionalRequirementService.create_functional_requirement import (
    create_functional_requirement, FunctionalRequirementConformityError,
)
from Model.Projects.Services.CreateAcceptanceCriteriaService.create_acceptance_criteria import (
    create_acceptance_criteria, AcceptanceCriteriaConformityError,
)
from Model.UsabilityInspection.Services.CreateFunctionalityVideoRecordService.create_functionality_video_record import (
    create_functionality_video_record,
)
from Model.UsabilityInspection.Services.ExecuteUsabilityInspectionService.execute_usability_inspection import (
    execute_usability_inspection,
)
from Model.SystemTest.Services.ExecuteSystemTestService.execute_system_test import (
    execute_system_test, RequirementNotFoundError, ScriptNotFoundError,
)
from Model.SystemTest.Services.GenerateTestReportService.generate_test_report import (
    generate_project_report_pdf,
)


def _conformity_messages(exc) -> list[str]:
    if hasattr(exc, "results"):
        return [r.feedback for r in exc.results if not r.valid]
    if hasattr(exc, "result"):
        return [exc.result.feedback]
    return [str(exc)]


def register_routes(app: Flask):
    initialize_database()

    # ── Context processor — injeta sidebar em todos os templates ─────────────
    @app.context_processor
    def inject_sidebar():
        from flask import session as s
        projects = list_projects()
        reqs = []
        if s.get("project_id"):
            reqs = list_functional_requirements_by_project(s["project_id"])
        return {"sidebar_projects": projects, "sidebar_reqs": reqs}

    # ── Auto-select único projeto/requisito ──────────────────────────────────
    @app.before_request
    def auto_select_context():
        if request.endpoint in (None, "static"):
            return
        if not session.get("project_id"):
            projects = list_projects()
            if len(projects) == 1:
                session["project_id"] = projects[0]["id"]
                session["project_name"] = projects[0]["name"]
        if session.get("project_id") and not session.get("requirement_id"):
            reqs = list_functional_requirements_by_project(session["project_id"])
            if len(reqs) == 1:
                session["requirement_id"] = reqs[0]["id"]
                session["requirement_name"] = reqs[0]["name"][:70]

    # ── Seleção rápida via sidebar ────────────────────────────────────────────
    @app.route("/sidebar/selecionar", methods=["POST"])
    def sidebar_selecionar():
        from flask import request as req, session as s
        next_url = req.form.get("next", "/")
        project_id = req.form.get("project_id", "").strip()
        requirement_id = req.form.get("requirement_id", "").strip()

        if project_id:
            for p in list_projects():
                if p["id"] == project_id:
                    if s.get("project_id") != project_id:
                        s["project_id"] = p["id"]
                        s["project_name"] = p["name"]
                        s.pop("requirement_id", None)
                        s.pop("requirement_name", None)
                    break

        if requirement_id:
            pid = s.get("project_id")
            if pid:
                for r in list_functional_requirements_by_project(pid):
                    if r["id"] == requirement_id:
                        s["requirement_id"] = r["id"]
                        s["requirement_name"] = r["name"][:70]
                        break

        return redirect(next_url)

    # ── Dashboard ────────────────────────────────────────────────────────────
    @app.route("/")
    def dashboard():
        projects = list_projects()
        total_reqs = total_insp = total_tests = 0
        for p in projects:
            reqs = list_functional_requirements_by_project(p["id"])
            total_reqs += len(reqs)
            for r in reqs:
                total_insp += len(list_usability_inspection_executions_by_requirement(r["id"]))
                total_tests += len(list_system_test_executions_by_requirement(r["id"]))
        return render_template(
            "index.html",
            projects=projects,
            total_reqs=total_reqs,
            total_insp=total_insp,
            total_tests=total_tests,
            openai_ok=bool(os.environ.get("OPENAI_API_KEY") or get_setting("openai_api_key")),
        )

    # ── Projetos ──────────────────────────────────────────────────────────────
    @app.route("/projetos", methods=["GET", "POST"])
    def projetos():
        form_data = None
        if request.method == "POST":
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()
            if not name or not description:
                flash("Preencha o nome e a descrição.", "warning")
                form_data = {"name": name, "description": description}
            else:
                try:
                    p = create_project(name=name, description=description)
                    session["project_id"] = p.get_id()
                    session["project_name"] = p.get_name()
                    flash(f"Projeto \"{p.get_name()}\" criado com sucesso!", "success")
                    return redirect(url_for("projetos"))
                except (ProjectConformityError, EnvironmentError, Exception) as e:
                    if isinstance(e, ProjectConformityError):
                        for msg in _conformity_messages(e):
                            flash(msg, "danger")
                    else:
                        flash(str(e), "danger")
                    form_data = {"name": name, "description": description}

        return render_template("projetos.html", projects=list_projects(), form_data=form_data)

    @app.route("/projetos/<project_id>/editar", methods=["POST"])
    def editar_projeto(project_id):
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name or not description:
            flash("Preencha o nome e a descrição.", "warning")
            return redirect(url_for("projetos"))
        try:
            from Model.Projects.ConformityAgents.ProjectConformityAgent.ProjectConformityAgent import ProjectConformityAgent
            agent = ProjectConformityAgent()
            results = [agent.validate_name(name), agent.validate_description(description)]
            failures = [r for r in results if not r.valid]
            if failures:
                for r in failures:
                    flash(r.feedback, "danger")
            else:
                update_project(project_id, name, description)
                if session.get("project_id") == project_id:
                    session["project_name"] = name
                flash("Projeto atualizado!", "success")
        except EnvironmentError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erro inesperado: {e}", "danger")
        return redirect(url_for("projetos"))

    @app.route("/projetos/<project_id>/deletar", methods=["POST"])
    def deletar_projeto(project_id):
        delete_project(project_id)
        if session.get("project_id") == project_id:
            session.pop("project_id", None)
            session.pop("project_name", None)
            session.pop("requirement_id", None)
            session.pop("requirement_name", None)
        flash("Projeto excluído.", "success")
        return redirect(url_for("projetos"))

    @app.route("/projetos/<project_id>/relatorio")
    def projeto_relatorio(project_id):
        """Download a full quality report (all requirements, inspections, tests) as PDF."""
        from Database.repositories.project_repository import get_project_by_id
        from Database.repositories.functional_requirement_repository import list_functional_requirements_by_project, get_personas_of_requirement

        project = get_project_by_id(project_id)
        if not project:
            flash("Projeto não encontrado.", "danger")
            return redirect(url_for("projetos"))

        reqs = list_functional_requirements_by_project(project_id)
        requirements_data = []
        for req in reqs:
            rid = req["id"]
            requirements_data.append({
                "requirement": req,
                "personas":    get_personas_of_requirement(rid),
                "criteria":    list_acceptance_criteria_by_requirement(rid),
                "inspections": list_usability_inspection_executions_by_requirement(rid),
                "tests":       list_system_test_executions_by_requirement(rid),
            })

        try:
            pdf_bytes = generate_project_report_pdf(
                project=project,
                requirements_data=requirements_data,
            )
        except Exception as e:
            flash(f"Erro ao gerar relatório: {e}", "danger")
            return redirect(url_for("projetos"))

        slug     = project_id[:8]
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"relatorio_{slug}_{date_str}.pdf"
        return Response(
            pdf_bytes,
            mimetype="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.route("/projetos/<project_id>/ativar", methods=["POST"])
    def ativar_projeto(project_id):
        projects = list_projects()
        for p in projects:
            if p["id"] == project_id:
                session["project_id"] = p["id"]
                session["project_name"] = p["name"]
                session.pop("requirement_id", None)
                session.pop("requirement_name", None)
                flash(f"Projeto \"{p['name']}\" selecionado.", "success")
                break
        return redirect(url_for("projetos"))

    # ── Personas ──────────────────────────────────────────────────────────────
    @app.route("/personas", methods=["GET", "POST"])
    def personas():
        project_id = session.get("project_id")
        if not project_id:
            flash("Selecione um projeto primeiro.", "warning")
            return redirect(url_for("projetos"))

        form_data = None
        if request.method == "POST":
            fields = {
                "name": request.form.get("name", "").strip(),
                "opportunities": request.form.get("opportunities", "").strip(),
                "key_attributes": request.form.get("key_attributes", "").strip(),
                "description": request.form.get("description", "").strip(),
                "needs": request.form.get("needs", "").strip(),
                "challenges": request.form.get("challenges", "").strip(),
            }
            if not all(fields.values()):
                flash("Preencha todos os campos.", "warning")
                form_data = fields
            else:
                try:
                    p = create_persona(project_id=project_id, **fields)
                    flash(f"Persona \"{p.get_name()}\" criada!", "success")
                    return redirect(url_for("personas"))
                except (PersonaConformityError, EnvironmentError, Exception) as e:
                    if isinstance(e, PersonaConformityError):
                        for msg in _conformity_messages(e):
                            flash(msg, "danger")
                    else:
                        flash(str(e), "danger")
                    form_data = fields

        return render_template(
            "personas.html",
            personas=list_personas_by_project(project_id),
            project_name=session.get("project_name"),
            form_data=form_data,
        )

    # ── Requisitos ────────────────────────────────────────────────────────────
    @app.route("/personas/<persona_id>/editar", methods=["POST"])
    def editar_persona(persona_id):
        fields = {k: request.form.get(k, "").strip() for k in
                  ["name", "opportunities", "key_attributes", "description", "needs", "challenges"]}
        if not all(fields.values()):
            flash("Preencha todos os campos.", "warning")
            return redirect(url_for("personas"))
        try:
            from Model.Projects.ConformityAgents.PersonaConformityAgent.PersonaConformityAgent import PersonaConformityAgent
            agent = PersonaConformityAgent()
            results = agent.validate_all(**fields)
            failures = [r for r in results if not r.valid]
            if failures:
                for r in failures:
                    flash(r.feedback, "danger")
            else:
                update_persona(persona_id, **fields)
                flash("Persona atualizada!", "success")
        except EnvironmentError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erro inesperado: {e}", "danger")
        return redirect(url_for("personas"))

    @app.route("/personas/<persona_id>/deletar", methods=["POST"])
    def deletar_persona(persona_id):
        delete_persona(persona_id)
        flash("Persona excluída.", "success")
        return redirect(url_for("personas"))

    @app.route("/requisitos", methods=["GET", "POST"])
    def requisitos():
        project_id = session.get("project_id")
        if not project_id:
            flash("Selecione um projeto primeiro.", "warning")
            return redirect(url_for("projetos"))

        req_form_data = None
        ac_form_data = None      # preserva campos do critério rejeitado
        ac_open_req_id = None    # mantém o accordion do AC aberto

        if request.method == "POST":
            action = request.form.get("action")

            if action == "create_req":
                name = request.form.get("name", "").strip()
                url = request.form.get("url", "").strip()
                persona_ids = request.form.getlist("persona_ids")
                if not name or not url:
                    flash("Preencha o nome (ARO) e a URL.", "warning")
                    req_form_data = {"name": name, "url": url, "persona_ids": persona_ids}
                else:
                    try:
                        r = create_functional_requirement(
                            project_id=project_id, name=name, url=url,
                            persona_ids=persona_ids or None,
                        )
                        session["requirement_id"] = r.get_id()
                        session["requirement_name"] = r.get_name()[:70]
                        flash("Requisito criado!", "success")
                        return redirect(url_for("requisitos"))
                    except (FunctionalRequirementConformityError, EnvironmentError, Exception) as e:
                        if isinstance(e, FunctionalRequirementConformityError):
                            for msg in _conformity_messages(e):
                                flash(msg, "danger")
                        else:
                            flash(str(e), "danger")
                        req_form_data = {"name": name, "url": url, "persona_ids": persona_ids}

            elif action == "create_ac":
                req_id = request.form.get("req_id")
                content = request.form.get("content", "").strip()
                author = request.form.get("author", "Tester").strip()
                if not content:
                    flash("Preencha o critério de aceite.", "warning")
                    ac_form_data = {"content": content, "author": author}
                    ac_open_req_id = req_id
                else:
                    try:
                        create_acceptance_criteria(
                            requirement_id=req_id, content=content, author=author,
                        )
                        flash("Critério de aceite adicionado!", "success")
                        return redirect(url_for("requisitos"))
                    except (AcceptanceCriteriaConformityError, EnvironmentError, Exception) as e:
                        if isinstance(e, AcceptanceCriteriaConformityError):
                            for msg in _conformity_messages(e):
                                flash(msg, "danger")
                        else:
                            flash(str(e), "danger")
                        ac_form_data = {"content": content, "author": author}
                        ac_open_req_id = req_id

        reqs = list_functional_requirements_by_project(project_id)
        personas = list_personas_by_project(project_id)
        req_details = []
        for r in reqs:
            req_details.append({
                **r,
                "personas": get_personas_of_requirement(r["id"]),
                "criteria": list_acceptance_criteria_by_requirement(r["id"]),
                "active": r["id"] == session.get("requirement_id"),
            })

        return render_template(
            "requisitos.html",
            reqs=req_details,
            personas=personas,
            project_name=session.get("project_name"),
            req_form_data=req_form_data,
            ac_form_data=ac_form_data,
            ac_open_req_id=ac_open_req_id,
        )

    @app.route("/requisitos/<req_id>/editar", methods=["POST"])
    def editar_requisito(req_id):
        name = request.form.get("name", "").strip()
        url = request.form.get("url", "").strip()
        persona_ids = request.form.getlist("persona_ids")
        if not name or not url:
            flash("Preencha o nome (ARO) e a URL.", "warning")
            return redirect(url_for("requisitos"))
        try:
            from Model.Projects.ConformityAgents.FunctionalRequirementConformityAgent.FunctionalRequirementConformityAgent import FunctionalRequirementConformityAgent
            agent = FunctionalRequirementConformityAgent()
            result = agent.validate_name(name)
            if not result.valid:
                flash(result.feedback, "danger")
            else:
                update_functional_requirement(req_id, name, url, persona_ids or None)
                if session.get("requirement_id") == req_id:
                    session["requirement_name"] = name[:70]
                flash("Requisito atualizado!", "success")
        except EnvironmentError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erro inesperado: {e}", "danger")
        return redirect(url_for("requisitos"))

    @app.route("/requisitos/<req_id>/deletar", methods=["POST"])
    def deletar_requisito(req_id):
        delete_functional_requirement(req_id)
        if session.get("requirement_id") == req_id:
            session.pop("requirement_id", None)
            session.pop("requirement_name", None)
        flash("Requisito excluído.", "success")
        return redirect(url_for("requisitos"))

    @app.route("/criterios/<ac_id>/editar", methods=["POST"])
    def editar_criterio(ac_id):
        content = request.form.get("content", "").strip()
        author = request.form.get("author", "Tester").strip()
        if not content:
            flash("Preencha o critério.", "warning")
            return redirect(url_for("requisitos"))
        try:
            from Model.Projects.ConformityAgents.AcceptanceCriteriaConformityAgent.AcceptanceCriteriaConformityAgent import AcceptanceCriteriaConformityAgent
            agent = AcceptanceCriteriaConformityAgent()
            result = agent.validate(content)
            if not result.valid:
                flash(result.feedback, "danger")
            else:
                update_acceptance_criteria(ac_id, content, author)
                flash("Critério de aceite atualizado!", "success")
        except EnvironmentError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erro inesperado: {e}", "danger")
        return redirect(url_for("requisitos"))

    @app.route("/criterios/<ac_id>/deletar", methods=["POST"])
    def deletar_criterio(ac_id):
        delete_acceptance_criteria(ac_id)
        flash("Critério de aceite excluído.", "success")
        return redirect(url_for("requisitos"))

    @app.route("/requisitos/<req_id>/ativar", methods=["POST"])
    def ativar_requisito(req_id):
        project_id = session.get("project_id")
        if project_id:
            for r in list_functional_requirements_by_project(project_id):
                if r["id"] == req_id:
                    session["requirement_id"] = r["id"]
                    session["requirement_name"] = r["name"][:70]
                    flash("Requisito selecionado.", "success")
                    break
        return redirect(url_for("requisitos"))

    # ── Inspeção de Usabilidade ───────────────────────────────────────────────
    @app.route("/inspecao")
    def inspecao():
        req_id = session.get("requirement_id")
        if not req_id:
            return render_template(
                "inspecao.html",
                req_id=None, req_name=None, pdf_file=None, execucoes=[], comments=[],
            )

        storage_dir = Path(os.getcwd()) / "src" / "Storage" / req_id
        pdf_files = sorted(storage_dir.glob("*.pdf")) if storage_dir.exists() else []
        execucoes = list_usability_inspection_executions_by_requirement(req_id)
        comments = list_comments_by_entity("usability_inspection", req_id)

        return render_template(
            "inspecao.html",
            req_name=session.get("requirement_name"),
            req_id=req_id,
            pdf_file=pdf_files[-1].name if pdf_files else None,
            execucoes=execucoes,
            comments=comments,
        )

    @app.route("/inspecao/gravar", methods=["POST"])
    def inspecao_gravar():
        req_id = session.get("requirement_id")
        if not req_id:
            flash("Selecione um requisito primeiro.", "warning")
            return redirect(url_for("requisitos"))
        try:
            path = create_functionality_video_record(req_id)
            flash(f"Gravação salva: {path}", "success")
        except Exception as e:
            flash(f"Erro na gravação: {e}", "danger")
        return redirect(url_for("inspecao"))

    @app.route("/inspecao/executar", methods=["POST"])
    def inspecao_executar():
        req_id = session.get("requirement_id")
        if not req_id:
            flash("Selecione um requisito primeiro.", "warning")
            return redirect(url_for("requisitos"))
        tester_comment = request.form.get("tester_comment", "").strip()
        try:
            execute_usability_inspection(functionality_id=req_id, tester_comment=tester_comment)
            flash("Inspeção de usabilidade concluída!", "success")
        except FileNotFoundError as e:
            flash(f"Gravação não encontrada: {e}", "danger")
        except EnvironmentError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erro na inspeção: {e}", "danger")
        return redirect(url_for("inspecao"))

    # ── Teste de Sistema ──────────────────────────────────────────────────────
    @app.route("/teste")
    def teste():
        req_id = session.get("requirement_id")
        if not req_id:
            return render_template(
                "teste.html",
                req_id=None, req_name=None, script_exists=False,
                script_content=None, execucoes=[], comments=[],
                passed_count=0, failed_count=0,
            )

        storage_dir = Path(os.getcwd()) / "src" / "Storage" / req_id
        script_path = storage_dir / f"execuction_recording_{req_id}.py"
        script_content = script_path.read_text(encoding="utf-8") if script_path.exists() else None
        execucoes = list_system_test_executions_by_requirement(req_id)
        comments = list_comments_by_entity("system_test", req_id)

        passed_count = sum(1 for e in execucoes if e["passed"])

        return render_template(
            "teste.html",
            req_name=session.get("requirement_name"),
            req_id=req_id,
            script_exists=script_path.exists(),
            script_content=script_content,
            execucoes=execucoes,
            comments=comments,
            passed_count=passed_count,
            failed_count=len(execucoes) - passed_count,
        )

    # ── Downloads — Inspeção ──────────────────────────────────────────────────
    @app.route("/inspecao/download/pdf")
    def inspecao_download_pdf():
        req_id = session.get("requirement_id")
        if not req_id:
            flash("Selecione um requisito primeiro.", "warning")
            return redirect(url_for("requisitos"))
        storage_dir = Path(os.getcwd()) / "src" / "Storage" / req_id
        pdf_files = sorted(storage_dir.glob("*.pdf")) if storage_dir.exists() else []
        if not pdf_files:
            flash("PDF de gravação não encontrado.", "danger")
            return redirect(url_for("inspecao"))
        return send_file(pdf_files[-1], as_attachment=True)

    @app.route("/inspecao/download/resultado/<exec_id>")
    def inspecao_download_resultado(exec_id):
        req_id = session.get("requirement_id")
        if not req_id:
            return redirect(url_for("requisitos"))
        execucoes = list_usability_inspection_executions_by_requirement(req_id)
        ex = next((e for e in execucoes if e["id"] == exec_id), None)
        if not ex or not ex.get("result_text"):
            flash("Resultado não encontrado.", "danger")
            return redirect(url_for("inspecao"))
        date_str = ex["created_at"][:10]
        filename = f"inspecao_{date_str}_{exec_id[:8]}.txt"
        return Response(
            ex["result_text"],
            mimetype="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    # ── Downloads — Teste de Sistema ──────────────────────────────────────────
    @app.route("/teste/download/script")
    def teste_download_script():
        req_id = session.get("requirement_id")
        if not req_id:
            flash("Selecione um requisito primeiro.", "warning")
            return redirect(url_for("requisitos"))
        storage_dir = Path(os.getcwd()) / "src" / "Storage" / req_id
        script_path = storage_dir / f"execuction_recording_{req_id}.py"
        if not script_path.exists():
            flash("Script não encontrado.", "danger")
            return redirect(url_for("teste"))
        return send_file(script_path, as_attachment=True)

    @app.route("/teste/video/<exec_id>")
    def teste_video(exec_id):
        """Serve the WebM execution video — inline for the player, or as attachment."""
        req_id = session.get("requirement_id")
        if not req_id:
            return redirect(url_for("requisitos"))
        execucoes = list_system_test_executions_by_requirement(req_id)
        ex = next((e for e in execucoes if e["id"] == exec_id), None)
        if not ex or not ex.get("video_path"):
            flash("Vídeo não disponível para esta execução.", "warning")
            return redirect(url_for("teste"))
        video_file = Path(ex["video_path"])
        if not video_file.exists():
            flash("Arquivo de vídeo não encontrado no servidor.", "danger")
            return redirect(url_for("teste"))
        download = request.args.get("download") == "1"
        return send_file(
            video_file,
            mimetype="video/webm",
            as_attachment=download,
            download_name=f"teste_{exec_id[:8]}.webm",
        )

    @app.route("/teste/download/resultado/<exec_id>")
    def teste_download_resultado(exec_id):
        req_id = session.get("requirement_id")
        if not req_id:
            return redirect(url_for("requisitos"))
        execucoes = list_system_test_executions_by_requirement(req_id)
        ex = next((e for e in execucoes if e["id"] == exec_id), None)
        if not ex or not ex.get("result_text"):
            flash("Resultado não encontrado.", "danger")
            return redirect(url_for("teste"))
        status = "passou" if ex["passed"] else "falhou"
        date_str = ex["created_at"][:10]
        filename = f"teste_{status}_{date_str}_{exec_id[:8]}.txt"
        return Response(
            ex["result_text"],
            mimetype="text/plain; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.route("/teste/executar", methods=["POST"])
    def teste_executar():
        req_id = session.get("requirement_id")
        if not req_id:
            flash("Selecione um requisito primeiro.", "warning")
            return redirect(url_for("requisitos"))
        tester_comment = request.form.get("tester_comment", "").strip()
        try:
            execucao = execute_system_test(requirement_id=req_id, tester_comment=tester_comment)
            if execucao.get_passed():
                flash("✅ Teste PASSOU!", "success")
            else:
                flash("❌ Teste FALHOU.", "danger")
        except ScriptNotFoundError as e:
            flash(str(e), "danger")
        except RequirementNotFoundError as e:
            flash(str(e), "danger")
        except EnvironmentError as e:
            flash(str(e), "danger")
        except Exception as e:
            flash(f"Erro no teste: {e}", "danger")
        return redirect(url_for("teste"))

    # ── Configurações ─────────────────────────────────────────────────────────
    @app.route("/configuracoes", methods=["GET", "POST"])
    def configuracoes():
        _allowed_policies = {
            "policy_project", "policy_persona", "policy_requirement",
            "policy_criteria", "policy_test_script",
        }

        if request.method == "POST":
            action = request.form.get("action")

            if action == "save_api_key":
                key = request.form.get("openai_api_key", "").strip()
                if not key:
                    flash("A chave não pode ser vazia.", "warning")
                elif not key.startswith("sk-"):
                    flash("Chave inválida — deve começar com 'sk-'.", "danger")
                else:
                    set_setting("openai_api_key", key)
                    flash("Chave da API OpenAI salva com sucesso!", "success")
                return redirect(url_for("configuracoes"))

            if action == "remove_api_key":
                set_setting("openai_api_key", "")
                os.environ.pop("OPENAI_API_KEY", None)
                flash("Chave removida.", "success")
                return redirect(url_for("configuracoes"))

            if action == "save_policy":
                key = request.form.get("policy_key", "").strip()
                value = request.form.get("policy_value", "").strip()
                if key in _allowed_policies and value:
                    set_setting(key, value)
                    flash("Prompt do agente atualizado.", "success")
                return redirect(url_for("configuracoes"))

            if action == "reset_policy":
                key = request.form.get("policy_key", "").strip()
                if key in _allowed_policies:
                    set_setting(key, "")
                    flash("Prompt restaurado para o padrão.", "success")
                return redirect(url_for("configuracoes"))

        # ── GET ──
        from Model.Projects.ConformityAgents.ProjectConformityAgent.Policy import _DEFAULT_PROMPT as _dp_proj
        from Model.Projects.ConformityAgents.PersonaConformityAgent.Policy import _DEFAULT_PROMPT as _dp_pers
        from Model.Projects.ConformityAgents.FunctionalRequirementConformityAgent.Policy import _DEFAULT_PROMPT as _dp_req
        from Model.Projects.ConformityAgents.AcceptanceCriteriaConformityAgent.Policy import _DEFAULT_PROMPT as _dp_crit
        from Model.SystemTest.ConformityAgent.Policy import _DEFAULT_PROMPT as _dp_test

        policies = [
            {"key": "policy_project",     "label": "Agente de Projetos",              "default": _dp_proj, "current": get_setting("policy_project") or ""},
            {"key": "policy_persona",     "label": "Agente de Personas",              "default": _dp_pers, "current": get_setting("policy_persona") or ""},
            {"key": "policy_requirement", "label": "Agente de Requisitos Funcionais", "default": _dp_req,  "current": get_setting("policy_requirement") or ""},
            {"key": "policy_criteria",    "label": "Agente de Critérios de Aceite",   "default": _dp_crit, "current": get_setting("policy_criteria") or ""},
            {"key": "policy_test_script", "label": "Agente de Scripts de Teste",      "default": _dp_test, "current": get_setting("policy_test_script") or ""},
        ]

        current_key = os.environ.get("OPENAI_API_KEY", "").strip() or get_setting("openai_api_key")
        masked = None
        if current_key:
            visible = current_key[-6:] if len(current_key) >= 6 else current_key
            masked = "sk-…" + visible

        return render_template(
            "configuracoes.html",
            active_page="configuracoes",
            has_key=bool(current_key),
            masked_key=masked,
            policies=policies,
        )
