import os

from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .layout import (
    QUESTION_ROW_GAP_MM,
    QUESTIONS_COLUMNS,
    QUESTIONS_START_X_MM,
    QUESTIONS_START_Y_MM,
    READ_AREA_BOTTOM_MM,
    READ_AREA_LEFT_MM,
    READ_AREA_RIGHT_MM,
    READ_AREA_TOP_MM,
    STUDENT_NUMBER_COLUMNS_X_MM,
    STUDENT_NUMBER_ROW_GAP_MM,
    STUDENT_NUMBER_START_X_MM,
    STUDENT_NUMBER_START_Y_MM,
    question_column_width_mm,
    question_letter_x_mm,
    question_option_x_mm,
    questions_per_column,
)


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
    # MARCADORES DA ÁREA DE LEITURA
    # -----------------------------
    marker_size = 7 * mm

    # Área útil que precisa aparecer na foto.
    # Os marcadores ficam próximos ao bloco do gabarito,
    # e não nos cantos da folha inteira.
    read_area_left = READ_AREA_LEFT_MM * mm
    read_area_right = READ_AREA_RIGHT_MM * mm
    read_area_top = page_height - READ_AREA_TOP_MM * mm
    read_area_bottom = page_height - READ_AREA_BOTTOM_MM * mm

    markers = [
        # superior esquerdo
        (read_area_left, read_area_top - marker_size),

        # superior direito
        (read_area_right - marker_size, read_area_top - marker_size),

        # inferior esquerdo
        (read_area_left, read_area_bottom),

        # inferior direito
        (read_area_right - marker_size, read_area_bottom),
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

    group_names = ", ".join(
        exam.class_groups.values_list("name", flat=True).order_by("name")
    )
    if group_names:
        c.drawString(25 * mm, page_height - 31 * mm, f"Turma: {group_names}")

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

    start_x_num = STUDENT_NUMBER_START_X_MM * mm
    start_y_num = page_height - STUDENT_NUMBER_START_Y_MM * mm

    row_gap = STUDENT_NUMBER_ROW_GAP_MM * mm
    circle_radius = 2.5 * mm

    digit_col_1_x = STUDENT_NUMBER_COLUMNS_X_MM[0] * mm
    digit_col_2_x = STUDENT_NUMBER_COLUMNS_X_MM[1] * mm

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
    c.drawString(QUESTIONS_START_X_MM * mm, page_height - 60 * mm, "QUESTÕES")

    total_columns = QUESTIONS_COLUMNS
    per_column = questions_per_column(exam.questions_count)

    start_x_questions = QUESTIONS_START_X_MM * mm
    start_y_questions = page_height - QUESTIONS_START_Y_MM * mm

    column_width = question_column_width_mm(exam.options_count) * mm
    question_row_gap = QUESTION_ROW_GAP_MM * mm

    for col in range(total_columns):
        col_x = start_x_questions + col * column_width

        # letras A/B/C/D/E no topo da coluna
        c.setFont("Helvetica-Bold", 8)

        for opt_idx, opt in enumerate(options):
            x = question_letter_x_mm(col_x / mm, opt_idx) * mm
            c.drawString(x - 1.5 * mm, start_y_questions + 7 * mm, opt)

        for row in range(per_column):
            question_number = col * per_column + row + 1

            if question_number > exam.questions_count:
                break

            y = start_y_questions - row * question_row_gap

            c.setFont("Helvetica-Bold", 8)
            c.drawString(col_x, y - 1 * mm, f"{question_number:02d}")

            for opt_idx in range(exam.options_count):
                x = question_option_x_mm(col_x / mm, opt_idx) * mm
                c.circle(x, y, circle_radius, stroke=1, fill=0)

    # -----------------------------
    # INSTRUÇÕES
    # -----------------------------
    c.setFont("Helvetica", 8)

    instructions_y = 25 * mm

    instructions = [
        "Instruções:",
        "1. Preencha completamente a opção escolhida.",
        "2. Marque apenas uma alternativa por questão.",
        "3. Não rasure os marcadores pretos dos cantos.",
    ]

    for idx, text in enumerate(instructions):
        c.drawString(25 * mm, instructions_y - idx * 5 * mm, text)

    c.showPage()
    c.save()

    relative_path = f"exam_templates/{filename}"

    return relative_path
