import os
from math import ceil

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def generate_exam_template(exam):
    """
    Gera um PDF de cartão-resposta com base na prova.

    Usa:
    - exam.questions_count
    - exam.options_count
    - exam.title
    """

    output_dir = os.path.join(settings.MEDIA_ROOT, "exam_templates")
    os.makedirs(output_dir, exist_ok=True)

    filename = f"exam_template_{exam.id}.pdf"
    output_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(output_path, pagesize=A4)

    page_width, page_height = A4

    # -----------------------------
    # MARCADORES EXTERNOS
    # -----------------------------
    marker_size = 8 * mm
    marker_margin = 10 * mm

    markers = [
        (marker_margin, page_height - marker_margin - marker_size),
        (page_width - marker_margin - marker_size, page_height - marker_margin - marker_size),
        (marker_margin, marker_margin),
        (page_width - marker_margin - marker_size, marker_margin),
    ]

    for x, y in markers:
        c.rect(x, y, marker_size, marker_size, fill=1, stroke=0)

    # -----------------------------
    # CABEÇALHO
    # -----------------------------
    c.setFont("Helvetica-Bold", 16)
    c.drawString(25 * mm, page_height - 18 * mm, "CARTÃO-RESPOSTA")

    c.setFont("Helvetica", 10)
    c.drawString(25 * mm, page_height - 25 * mm, f"Prova: {exam.title}")

    if exam.class_group:
        c.drawString(25 * mm, page_height - 31 * mm, f"Turma: {exam.class_group.name}")

    c.drawString(
        25 * mm,
        page_height - 37 * mm,
        f"Questões: {exam.questions_count} | Alternativas: {exam.options_count}",
    )

    # -----------------------------
    # CAMPO NOME
    # -----------------------------
    c.setFont("Helvetica", 9)
    c.drawString(25 * mm, page_height - 47 * mm, "Nome do aluno:")
    c.line(50 * mm, page_height - 47 * mm, 140 * mm, page_height - 47 * mm)

    # -----------------------------
    # NÚMERO DO ALUNO
    # 2 colunas x 10 linhas
    # -----------------------------
    c.setFont("Helvetica-Bold", 10)
    c.drawString(25 * mm, page_height - 60 * mm, "NÚMERO DO ALUNO")

    c.setFont("Helvetica", 8)
    c.drawString(25 * mm, page_height - 66 * mm, "Marque um número em cada coluna.")

    start_x_num = 25 * mm
    start_y_num = page_height - 78 * mm

    row_gap = 7 * mm
    circle_radius = 2.5 * mm

    digit_col_1_x = start_x_num + 18 * mm
    digit_col_2_x = start_x_num + 32 * mm

    c.setFont("Helvetica-Bold", 8)
    c.drawString(digit_col_1_x - 2 * mm, start_y_num + 7 * mm, "1º")
    c.drawString(digit_col_2_x - 2 * mm, start_y_num + 7 * mm, "2º")

    for digit in range(10):
        y = start_y_num - digit * row_gap

        c.setFont("Helvetica-Bold", 8)
        c.drawString(start_x_num, y - 1 * mm, str(digit))

        c.circle(digit_col_1_x, y, circle_radius, stroke=1, fill=0)
        c.circle(digit_col_2_x, y, circle_radius, stroke=1, fill=0)

    # -----------------------------
    # QUESTÕES
    # -----------------------------
    options = [chr(65 + i) for i in range(exam.options_count)]

    c.setFont("Helvetica-Bold", 10)
    c.drawString(75 * mm, page_height - 60 * mm, "QUESTÕES")

    total_columns = 2
    questions_per_column = ceil(exam.questions_count / total_columns)

    start_x_questions = 75 * mm
    start_y_questions = page_height - 78 * mm

    column_width = 48 * mm
    question_row_gap = 7 * mm
    option_gap = 8 * mm

    for col in range(total_columns):
        col_x = start_x_questions + col * column_width

        # letras A/B/C/D/E no topo da coluna
        c.setFont("Helvetica-Bold", 8)

        for opt_idx, opt in enumerate(options):
            x = col_x + 14 * mm + opt_idx * option_gap
            c.drawString(x - 1.5 * mm, start_y_questions + 7 * mm, opt)

        for row in range(questions_per_column):
            question_number = col * questions_per_column + row + 1

            if question_number > exam.questions_count:
                break

            y = start_y_questions - row * question_row_gap

            c.setFont("Helvetica-Bold", 8)
            c.drawString(col_x, y - 1 * mm, f"{question_number:02d}")

            for opt_idx in range(exam.options_count):
                x = col_x + 15 * mm + opt_idx * option_gap
                c.circle(x, y, circle_radius, stroke=1, fill=0)

    # -----------------------------
    # INSTRUÇÕES
    # -----------------------------
    c.setFont("Helvetica", 8)

    instructions_y = 25 * mm

    instructions = [
        "Instruções:",
        "1. Preencha completamente a bolha escolhida.",
        "2. Marque apenas uma alternativa por questão.",
        "3. Não rasure os marcadores pretos dos cantos.",
        "4. Use este cartão no modelo padronizado do sistema.",
    ]

    for idx, text in enumerate(instructions):
        c.drawString(25 * mm, instructions_y - idx * 5 * mm, text)

    c.showPage()
    c.save()

    relative_path = f"exam_templates/{filename}"

    return relative_path