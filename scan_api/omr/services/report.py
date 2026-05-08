import io
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from omr.models import ScanResult


def _calculate_stats(scan_result: ScanResult) -> dict[str, Any]:
    all_results = list(
        ScanResult.active.filter(exam=scan_result.exam)
        .exclude(is_deleted=True)
        .order_by("-score")
        .values("id", "score", "answers")
    )

    total_students = len(all_results)
    if total_students == 0:
        return {
            "rank": 1,
            "total_students": 1,
            "percentile": 100.0,
            "ci_per_question": [],
        }

    # Rank: how many students scored strictly higher
    rank = sum(1 for r in all_results if r["score"] > scan_result.score) + 1

    # Percentile: percentage of students scored below this student
    below = sum(1 for r in all_results if r["score"] < scan_result.score)
    percentile = round((below / total_students) * 100, 1)

    # CI (Confidence Index) per question: % of students who answered correctly
    answer_key = scan_result.exam.answer_key
    ci_per_question = []
    for i, correct_answer in enumerate(answer_key):
        correct_count = sum(
            1
            for r in all_results
            if r["answers"] and i < len(r["answers"]) and r["answers"][i] == correct_answer
        )
        ci = round((correct_count / total_students) * 100, 1) if total_students > 0 else 0.0
        ci_per_question.append(ci)

    return {
        "rank": rank,
        "total_students": total_students,
        "percentile": percentile,
        "ci_per_question": ci_per_question,
    }


def generate_report_card(scan_result: ScanResult) -> bytes:
    stats = _calculate_stats(scan_result)
    answer_key = scan_result.exam.answer_key
    answers = scan_result.answers or []

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=2,
        alignment=TA_LEFT,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=1,
    )
    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#94a3b8"),
        spaceBefore=0,
        spaceAfter=0,
    )
    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=13,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
        spaceBefore=0,
        spaceAfter=0,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Normal"],
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#475569"),
        spaceBefore=8,
        spaceAfter=4,
    )

    COLOR_GREEN = colors.HexColor("#dcfce7")
    COLOR_GREEN_DARK = colors.HexColor("#16a34a")
    COLOR_RED = colors.HexColor("#fee2e2")
    COLOR_RED_DARK = colors.HexColor("#dc2626")
    COLOR_HEADER = colors.HexColor("#f1f5f9")
    COLOR_BORDER = colors.HexColor("#e2e8f0")

    story = []

    # Title block
    student_name = scan_result.student.name if scan_result.student else "Aluno não identificado"
    story.append(Paragraph(student_name, title_style))
    story.append(Paragraph(scan_result.exam.title, subtitle_style))

    if scan_result.exam.class_group:
        story.append(Paragraph(scan_result.exam.class_group.name, subtitle_style))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=1, color=COLOR_BORDER))
    story.append(Spacer(1, 4 * mm))

    # Summary stats row
    correct_count = sum(
        1
        for i, ans in enumerate(answers)
        if ans is not None and i < len(answer_key) and ans == answer_key[i]
    )
    incorrect_count = sum(
        1
        for i, ans in enumerate(answers)
        if ans is not None and i < len(answer_key) and ans != answer_key[i]
    )
    blank_count = sum(1 for ans in answers if ans is None)
    pct = round((correct_count / scan_result.total_questions) * 100, 1) if scan_result.total_questions else 0

    summary_data = [
        [
            Paragraph("ACERTOS", label_style),
            Paragraph("ERROS", label_style),
            Paragraph("EM BRANCO", label_style),
            Paragraph("APROVEITAMENTO", label_style),
            Paragraph("COLOCAÇÃO", label_style),
            Paragraph("PERCENTIL", label_style),
        ],
        [
            Paragraph(str(correct_count), value_style),
            Paragraph(str(incorrect_count), value_style),
            Paragraph(str(blank_count), value_style),
            Paragraph(f"{pct}%", value_style),
            Paragraph(f"{stats['rank']}º de {stats['total_students']}", value_style),
            Paragraph(f"{stats['percentile']}%", value_style),
        ],
    ]

    summary_table = Table(summary_data, colWidths="*")
    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), COLOR_HEADER),
            ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("ROUNDEDCORNERS", [4]),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 5 * mm))

    # Per-question table
    story.append(Paragraph("Desempenho por questão", section_style))

    header = [
        Paragraph("Nº", ParagraphStyle("TH", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("Gabarito", ParagraphStyle("TH", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("Marcado", ParagraphStyle("TH", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("Resultado", ParagraphStyle("TH", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER)),
        Paragraph("IC da turma", ParagraphStyle("TH", parent=styles["Normal"], fontSize=8, fontName="Helvetica-Bold", alignment=TA_CENTER)),
    ]

    cell_style = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER)
    correct_cell_style = ParagraphStyle("CellCorrect", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=COLOR_GREEN_DARK, fontName="Helvetica-Bold")
    incorrect_cell_style = ParagraphStyle("CellWrong", parent=styles["Normal"], fontSize=8, alignment=TA_CENTER, textColor=COLOR_RED_DARK, fontName="Helvetica-Bold")

    table_data = [header]
    row_colors = []

    for i, correct_answer in enumerate(answer_key):
        given = answers[i] if i < len(answers) else None
        is_blank = given is None
        is_correct = not is_blank and given == correct_answer
        ci = stats["ci_per_question"][i] if i < len(stats["ci_per_question"]) else 0.0

        if is_blank:
            result_text = "Em branco"
            result_para = Paragraph(result_text, cell_style)
            marked_para = Paragraph("—", cell_style)
            row_bg = colors.white
        elif is_correct:
            result_text = "Correto"
            result_para = Paragraph(result_text, correct_cell_style)
            marked_para = Paragraph(given, correct_cell_style)
            row_bg = COLOR_GREEN
        else:
            result_text = "Incorreto"
            result_para = Paragraph(result_text, incorrect_cell_style)
            marked_para = Paragraph(given, incorrect_cell_style)
            row_bg = COLOR_RED

        row_colors.append(row_bg)
        table_data.append([
            Paragraph(str(i + 1), cell_style),
            Paragraph(correct_answer, cell_style),
            marked_para,
            result_para,
            Paragraph(f"{ci}%", cell_style),
        ])

    col_widths = [12 * mm, 22 * mm, 22 * mm, 30 * mm, 30 * mm]
    q_table = Table(table_data, colWidths=col_widths, repeatRows=1)

    table_style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
    ]

    for row_idx, bg in enumerate(row_colors):
        data_row = row_idx + 1
        table_style_cmds.append(("BACKGROUND", (0, data_row), (-1, data_row), bg))

    q_table.setStyle(TableStyle(table_style_cmds))
    story.append(q_table)

    doc.build(story)
    return buf.getvalue()
