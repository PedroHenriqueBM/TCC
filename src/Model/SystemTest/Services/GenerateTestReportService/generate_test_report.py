"""
Project-level PDF report — all requirements, inspections and system tests.
"""
import io
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

_DARK   = colors.HexColor("#0f172a")
_BLUE   = colors.HexColor("#2563eb")
_INDIGO = colors.HexColor("#4f46e5")
_GREEN  = colors.HexColor("#16a34a")
_RED    = colors.HexColor("#dc2626")
_MUTED  = colors.HexColor("#64748b")
_BG_PASS  = colors.HexColor("#f0fdf4")
_BG_FAIL  = colors.HexColor("#fef2f2")
_BG_INSP  = colors.HexColor("#eff6ff")
_BORDER   = colors.HexColor("#e2e8f0")
_BG_GRAY  = colors.HexColor("#f8fafc")


def _styles():
    base = getSampleStyleSheet()

    def _s(name, **kw):
        return ParagraphStyle(name, parent=base["Normal"], **kw)

    return {
        "h1":    _s("h1",  fontSize=22, textColor=_DARK,  spaceAfter=4,  spaceBefore=0, fontName="Helvetica-Bold"),
        "h2":    _s("h2",  fontSize=14, textColor=_BLUE,  spaceAfter=4,  spaceBefore=12, fontName="Helvetica-Bold"),
        "h3":    _s("h3",  fontSize=11, textColor=_INDIGO, spaceAfter=3,  spaceBefore=8,  fontName="Helvetica-Bold"),
        "h4":    _s("h4",  fontSize=9,  textColor=_DARK,  spaceAfter=2,  spaceBefore=5,  fontName="Helvetica-Bold"),
        "body":  _s("body", fontSize=9, textColor=_DARK,  spaceAfter=2,  leading=13),
        "muted": _s("muted", fontSize=8, textColor=_MUTED, spaceAfter=1),
        "pass":  _s("pass", fontSize=9, textColor=_GREEN, fontName="Helvetica-Bold"),
        "fail":  _s("fail", fontSize=9, textColor=_RED,   fontName="Helvetica-Bold"),
        "code":  _s("code", fontSize=7.5, fontName="Courier", textColor=_DARK,
                     backColor=colors.HexColor("#f1f5f9"),
                     leftIndent=4, rightIndent=4,
                     borderPadding=(4, 4, 4, 4), leading=11),
        "center": _s("center", fontSize=8, alignment=TA_CENTER, textColor=_MUTED),
    }


def _hr(story, color=_BORDER, thickness=0.5):
    story.append(HRFlowable(width="100%", thickness=thickness, color=color,
                            spaceAfter=4, spaceBefore=4))


def _safe(text: str, limit: int = 3000) -> str:
    if not text:
        return ""
    text = str(text)[:limit]
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;"))


def _kv_table(rows, doc, st):
    """Render a two-column key/value table."""
    data = [
        [Paragraph(_safe(k), st["muted"]),
         Paragraph(_safe(str(v)), st["body"])]
        for k, v in rows
    ]
    t = Table(data, colWidths=[3.8 * cm, doc.width - 3.8 * cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def _colored_box(text, bg, doc, st):
    """Render evaluation text inside a background box."""
    t = Table(
        [[Paragraph(_safe(text), st["body"])]],
        colWidths=[doc.width],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, -1), bg),
        ("LEFTPADDING",  (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING",   (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 6),
    ]))
    return t


def generate_project_report_pdf(
    project: dict,
    requirements_data: list[dict],
) -> bytes:
    """
    Generate a complete project-level PDF report.

    Each entry in requirements_data is a dict with keys:
        requirement  – dict (id, name, url, created_at)
        personas     – list[dict] (name, …)
        criteria     – list[dict] (content, …)
        inspections  – list[dict] (id, result_text, created_at)
        tests        – list[dict] (id, passed, result_text, created_at, video_path)
    """
    st = _styles()
    buf = io.BytesIO()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Relatório — {project.get('name', '')}",
        author="QA com IA",
    )

    story = []

    # ── Cover ──────────────────────────────────────────────────────────────────
    story.append(Paragraph("QA com IA", st["muted"]))
    story.append(Paragraph("Relatório de Qualidade de Software", st["h1"]))
    story.append(Spacer(1, 0.2 * cm))

    cover_rows = [
        ("Projeto",     project.get("name", "—")),
        ("Descrição",   project.get("description", "")),
        ("Gerado em",   datetime.now().strftime("%d/%m/%Y %H:%M")),
    ]
    story.append(_kv_table(cover_rows, doc, st))
    story.append(Spacer(1, 0.4 * cm))
    _hr(story, thickness=1, color=_BLUE)

    # ── Global summary ─────────────────────────────────────────────────────────
    total_reqs  = len(requirements_data)
    total_insp  = sum(len(r["inspections"]) for r in requirements_data)
    total_tests = sum(len(r["tests"]) for r in requirements_data)
    total_pass  = sum(sum(1 for t in r["tests"] if t.get("passed")) for r in requirements_data)
    total_fail  = total_tests - total_pass
    rate        = f"{round(total_pass / total_tests * 100)}%" if total_tests else "—"

    story.append(Paragraph("Resumo do Projeto", st["h2"]))
    summary_data = [
        ["Requisitos funcionais",  str(total_reqs)],
        ["Inspeções de usabilidade", str(total_insp)],
        ["Testes de sistema",      str(total_tests)],
        [f"Testes passou ✅",       str(total_pass)],
        [f"Testes falhou ❌",       str(total_fail)],
        ["Taxa de sucesso",        rate],
    ]
    sum_table = Table(
        [[Paragraph(k, st["muted"]), Paragraph(v, st["body"])]
         for k, v in summary_data],
        colWidths=[5.5 * cm, None],
        hAlign="LEFT",
    )
    sum_table.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(sum_table)

    # ── Per-requirement sections ───────────────────────────────────────────────
    for req_data in requirements_data:
        req        = req_data["requirement"]
        personas   = req_data["personas"]
        criteria   = req_data["criteria"]
        inspections= req_data["inspections"]
        tests      = req_data["tests"]

        story.append(PageBreak())
        story.append(Paragraph(_safe(req.get("name", "—")), st["h2"]))
        _hr(story, color=_BLUE)

        # Metadata
        meta = []
        if req.get("url"):
            meta.append(("URL", req["url"]))
        if req.get("created_at"):
            meta.append(("Criado em", req["created_at"][:10]))
        if personas:
            meta.append(("Personas", ", ".join(p.get("name", "") for p in personas)))
        if meta:
            story.append(_kv_table(meta, doc, st))
            story.append(Spacer(1, 0.2 * cm))

        # Acceptance criteria
        if criteria:
            story.append(Paragraph("Critérios de Aceite", st["h3"]))
            for i, ac in enumerate(criteria, 1):
                story.append(Paragraph(f"{i}. {_safe(ac.get('content', ''))}", st["body"]))
            story.append(Spacer(1, 0.2 * cm))

        # ── Inspections ───────────────────────────────────────────────────────
        story.append(Paragraph(
            f"Inspeções de Usabilidade ({len(inspections)})", st["h3"]
        ))

        if not inspections:
            story.append(Paragraph("Nenhuma inspeção executada.", st["muted"]))
        else:
            for idx, ex in enumerate(inspections):
                num     = len(inspections) - idx
                created = ex.get("created_at", "")[:19].replace("T", " ")
                story.append(Paragraph(f"Execução {num} — {created}", st["h4"]))
                result  = (ex.get("result_text") or "").strip()
                if result:
                    story.append(_colored_box(result[:1500], _BG_INSP, doc, st))
                else:
                    story.append(Paragraph("(sem resultado registrado)", st["muted"]))
                if idx < len(inspections) - 1:
                    story.append(Spacer(1, 0.2 * cm))

        story.append(Spacer(1, 0.3 * cm))

        # ── Tests ──────────────────────────────────────────────────────────────
        passed_count = sum(1 for t in tests if t.get("passed"))
        story.append(Paragraph(
            f"Testes de Sistema ({len(tests)} — {passed_count} passou / {len(tests)-passed_count} falhou)",
            st["h3"],
        ))

        if not tests:
            story.append(Paragraph("Nenhum teste executado.", st["muted"]))
        else:
            for idx, ex in enumerate(tests):
                num     = len(tests) - idx
                created = ex.get("created_at", "")[:19].replace("T", " ")
                passed  = ex.get("passed", False)
                badge   = "✅ PASSOU" if passed else "❌ FALHOU"
                bg      = _BG_PASS if passed else _BG_FAIL

                story.append(Paragraph(f"Execução {num} — {created}", st["h4"]))
                story.append(Paragraph(badge, st["pass"] if passed else st["fail"]))

                result_text = ex.get("result_text", "")
                if result_text:
                    parts      = result_text.split("\n\n=== SAÍDA DO SCRIPT ===\n")
                    evaluation = parts[0].replace("=== AVALIAÇÃO DO AGENTE ===\n", "").strip()
                    script_out = parts[1].strip() if len(parts) > 1 else ""

                    story.append(_colored_box(evaluation, bg, doc, st))

                    if script_out:
                        story.append(Spacer(1, 0.1 * cm))
                        story.append(Paragraph("Saída do script:", st["muted"]))
                        truncated = script_out[:600] + ("…" if len(script_out) > 600 else "")
                        story.append(Paragraph(_safe(truncated), st["code"]))

                if ex.get("video_path") and Path(str(ex["video_path"])).exists():
                    story.append(Paragraph(
                        f"Vídeo: <i>{Path(ex['video_path']).name}</i>", st["muted"]
                    ))

                if idx < len(tests) - 1:
                    story.append(Spacer(1, 0.25 * cm))

    # ── Footer ─────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    _hr(story)
    story.append(Paragraph(
        f"Relatório gerado por QA com IA · {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        st["center"],
    ))

    doc.build(story)
    return buf.getvalue()
