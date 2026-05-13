import io
from datetime import date
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from core.models import Student
from omr.models import Exam, ScanResult

C_HEADER_BG = colors.HexColor("#f1f5f9")
C_HEADER_TEXT = colors.HexColor("#1e293b")
C_BORDER = colors.HexColor("#cbd5e1")
C_ALT_ROW = colors.HexColor("#f8fafc")
C_SUMMARY_BG = colors.HexColor("#e2e8f0")
C_GREEN = colors.HexColor("#15803d")
C_RED = colors.HexColor("#b91c1c")
C_MUTED = colors.HexColor("#94a3b8")
C_TITLE = colors.HexColor("#0f172a")
C_SUBTITLE = colors.HexColor("#475569")


def _nota(score: int, total: int) -> str:
    if total == 0:
        return "—"
    return f"{score / total * 10:.1f}".replace(".", ",")


def _build_section(
    exam_title: str,
    class_name: str,
    questions_count: int,
    rows_data: list[dict[str, Any]],
) -> list:
    TH = ParagraphStyle(
        "TH",
        fontSize=8,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        leading=10,
        textColor=C_HEADER_TEXT,
    )
    TH_L = ParagraphStyle(
        "THL",
        fontSize=8,
        fontName="Helvetica-Bold",
        alignment=TA_LEFT,
        leading=10,
        textColor=C_HEADER_TEXT,
    )
    TD_C = ParagraphStyle("TDC", fontSize=8, alignment=TA_CENTER, leading=10)
    TD = ParagraphStyle("TD", fontSize=8, alignment=TA_LEFT, leading=10)
    TD_MUTED = ParagraphStyle(
        "TDM",
        fontSize=8,
        alignment=TA_LEFT,
        leading=10,
        textColor=C_MUTED,
        fontName="Helvetica-Oblique",
    )
    S_TITLE = ParagraphStyle(
        "ST", fontSize=12, fontName="Helvetica-Bold", textColor=C_TITLE, spaceAfter=1
    )
    S_SUB = ParagraphStyle("SS", fontSize=8, textColor=C_SUBTITLE, spaceAfter=4)
    S_AVG = ParagraphStyle(
        "SA", fontSize=8, fontName="Helvetica-Bold", alignment=TA_LEFT, leading=10
    )
    S_AVG_C = ParagraphStyle(
        "SAC", fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=10
    )

    story = [
        Paragraph(f"{exam_title}  –  {class_name}", S_TITLE),
        Paragraph(
            f"{questions_count} questões  ·  Gerado em {date.today().strftime('%d/%m/%Y')}",
            S_SUB,
        ),
    ]

    if not rows_data:
        story.append(Paragraph("Nenhum aluno cadastrado nesta turma.", TD))
        story.append(Spacer(1, 6 * mm))
        return story

    header_row = [
        Paragraph("Nº", TH),
        Paragraph("Nome", TH_L),
        Paragraph("Acertos", TH),
        Paragraph("Nota", TH),
    ]
    table_rows = [header_row]
    row_bgs = []

    scored = [r for r in rows_data if r["score"] is not None]
    total_score = sum(r["score"] for r in scored)

    for i, r in enumerate(rows_data):
        num = str(r["number"]).zfill(2) if r["number"] else "??"
        name = r["name"]
        has_result = r["score"] is not None

        if has_result:
            nota = _nota(r["score"], r["total_questions"])
            pct = r["score"] / max(r["total_questions"], 1)
            score_color = C_GREEN if pct >= 0.5 else C_RED
            TD_SCORE = ParagraphStyle(
                f"TDS{i}",
                fontSize=8,
                fontName="Helvetica-Bold",
                alignment=TA_CENTER,
                leading=10,
                textColor=score_color,
            )
            acertos_cell = Paragraph(str(r["score"]), TD_SCORE)
            nota_cell = Paragraph(nota, TD_SCORE)
        else:
            acertos_cell = Paragraph("—", TD_C)
            nota_cell = Paragraph("—", TD_C)

        name_style = TD if r["identified"] else TD_MUTED
        table_rows.append(
            [
                Paragraph(num, TD_C),
                Paragraph(name, name_style),
                acertos_cell,
                nota_cell,
            ]
        )
        row_bgs.append(colors.white if i % 2 == 0 else C_ALT_ROW)

    n_scored = len(scored)
    n_total = len(rows_data)
    if n_scored > 0:
        avg_score = total_score / n_scored
        avg_nota = _nota(round(avg_score), scored[0]["total_questions"])
        avg_label = f"Média  ({n_scored}/{n_total} aluno{'s' if n_total != 1 else ''} avaliado{'s' if n_scored != 1 else ''})"
        avg_acertos = f"{avg_score:.1f}".replace(".", ",")
    else:
        avg_nota = "—"
        avg_label = f"Nenhum resultado registrado  ({n_total} aluno{'s' if n_total != 1 else ''})"
        avg_acertos = "—"

    table_rows.append(
        [
            Paragraph("", TD_C),
            Paragraph(avg_label, S_AVG),
            Paragraph(avg_acertos, S_AVG_C),
            Paragraph(avg_nota, S_AVG_C),
        ]
    )

    col_w = [12 * mm, None, 20 * mm, 18 * mm]
    table = Table(table_rows, colWidths=col_w, repeatRows=1)

    style = [
        ("BACKGROUND", (0, 0), (-1, 0), C_HEADER_BG),
        ("LINEBELOW", (0, 0), (-1, 0), 1, C_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.75, C_BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, C_BORDER),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (1, 0), (1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("BACKGROUND", (0, len(table_rows) - 1), (-1, len(table_rows) - 1), C_SUMMARY_BG),
        ("LINEABOVE", (0, len(table_rows) - 1), (-1, len(table_rows) - 1), 0.75, C_BORDER),
    ]
    for idx, bg in enumerate(row_bgs):
        style.append(("BACKGROUND", (0, idx + 1), (-1, idx + 1), bg))

    table.setStyle(TableStyle(style))
    story.append(KeepTogether([table]))
    return story


def _build_rows_for_class(exam: Exam, cg) -> list[dict]:
    students = list(Student.active.filter(class_group=cg, is_active=True).order_by("name"))

    results_by_student = {
        r.student_id: r
        for r in ScanResult.active.filter(exam=exam, student__class_group=cg).select_related(
            "student"
        )
    }

    unidentified = list(
        ScanResult.active.filter(exam=exam, student__isnull=True).order_by("student_number")
    )

    rows: list[dict] = []

    for student in students:
        result = results_by_student.get(student.id)
        rows.append(
            {
                "number": student.number,
                "name": student.name,
                "identified": True,
                "score": result.score if result else None,
                "total_questions": result.total_questions if result else exam.questions_count,
            }
        )

    for r in unidentified:
        rows.append(
            {
                "number": r.student_number,
                "name": "Não identificado",
                "identified": False,
                "score": r.score,
                "total_questions": r.total_questions,
            }
        )

    return rows


def generate_class_report(exams: list[Exam]) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
    )

    story = []
    sections: list[dict] = []

    for exam in exams:
        class_groups = list(exam.class_groups.filter(is_deleted=False).order_by("name"))

        for cg in class_groups:
            rows = _build_rows_for_class(exam, cg)
            sections.append(
                {
                    "exam_title": exam.title,
                    "class_name": cg.name,
                    "questions_count": exam.questions_count,
                    "rows": rows,
                }
            )

        if not class_groups:
            results_qs = ScanResult.active.filter(exam=exam).select_related("student")
            rows = [
                {
                    "number": r.student_number,
                    "name": r.student.name if r.student else "Não identificado",
                    "identified": r.student is not None,
                    "score": r.score,
                    "total_questions": r.total_questions,
                }
                for r in results_qs
            ]
            rows.sort(key=lambda r: r["name"].lower())
            sections.append(
                {
                    "exam_title": exam.title,
                    "class_name": "Sem turma",
                    "questions_count": exam.questions_count,
                    "rows": rows,
                }
            )

    for i, sec in enumerate(sections):
        story.extend(
            _build_section(
                sec["exam_title"],
                sec["class_name"],
                sec["questions_count"],
                sec["rows"],
            )
        )
        if i < len(sections) - 1:
            story.append(PageBreak())

    doc.build(story)
    return buf.getvalue()
