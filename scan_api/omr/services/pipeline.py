import cv2
import numpy as np
from django.conf import settings

from .align import align_sheet
from .detect import find_bubbles
from .image_io import load_image_for_omr
from .layout import (
    PAGE_HEIGHT_MM,
    PAGE_WIDTH_MM,
    STUDENT_NUMBER_COLUMNS_X_MM,
    STUDENT_NUMBER_ROW_GAP_MM,
    STUDENT_NUMBER_START_Y_MM,
    question_option_x_mm,
    question_position_mm,
)
from .preprocess import preprocess_image_from_array

IMAGE_WIDTH = 600
IMAGE_HEIGHT = 800

LETRAS = ["A", "B", "C", "D", "E"]


def mm_to_px_x(mm_value):
    return mm_value * IMAGE_WIDTH / PAGE_WIDTH_MM


def mm_to_px_y(mm_value):
    return mm_value * IMAGE_HEIGHT / PAGE_HEIGHT_MM


def score_bolha(image, thresh, x_centro, y_centro, raio=4, gray=None, hsv=None):
    """
    Lê apenas o centro da bolha.
    Evita contar a borda da bolha vazia.
    """

    x1 = max(int(x_centro - raio), 0)
    x2 = min(int(x_centro + raio), IMAGE_WIDTH)

    y1 = max(int(y_centro - raio), 0)
    y2 = min(int(y_centro + raio), IMAGE_HEIGHT)

    roi_thresh = thresh[y1:y2, x1:x2]

    if roi_thresh.size == 0:
        score_thresh = 0
    else:
        total = cv2.countNonZero(roi_thresh)
        area = roi_thresh.shape[0] * roi_thresh.shape[1]
        score_thresh = total / float(area)

    if hsv is None:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    if gray is None:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    roi_hsv = hsv[y1:y2, x1:x2]
    roi_gray = gray[y1:y2, x1:x2]

    if roi_hsv.size == 0:
        score_cor = 0
    else:
        saturacao = roi_hsv[:, :, 1]
        score_cor = cv2.mean(saturacao)[0] / 255.0

    score_escuro = 0 if roi_gray.size == 0 else max(0.0, 1.0 - (cv2.mean(roi_gray)[0] / 245.0))

    return max(score_thresh, score_cor, score_escuro)


def escolher_marcacao(scores, limite_minimo=0.35, diferenca_minima=0.12):
    """
    Escolhe a alternativa/dígito marcado.
    Se estiver vazio ou duvidoso, retorna None.
    """

    if not scores:
        return None

    maior = max(scores)
    ordenados = sorted(scores, reverse=True)

    if maior < limite_minimo:
        return None

    if len(ordenados) > 1 and ordenados[0] - ordenados[1] < diferenca_minima:
        return None

    return int(np.argmax(scores))


def ler_numero_aluno(image, thresh):
    """
    Lê o número do aluno usando a grade fixa do modelo gerado.

    No template_generator.py:
    start_x_num = 25mm
    digit_col_1_x = start_x_num + 18mm = 43mm
    digit_col_2_x = start_x_num + 32mm = 57mm
    start_y_num = 78mm
    row_gap = 7mm
    """

    colunas_x_mm = STUDENT_NUMBER_COLUMNS_X_MM
    start_y_mm = STUDENT_NUMBER_START_Y_MM
    row_gap_mm = STUDENT_NUMBER_ROW_GAP_MM

    numero = ""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for idx_coluna, x_mm in enumerate(colunas_x_mm, start=1):
        x_centro = mm_to_px_x(x_mm)

        scores = []

        for digit in range(10):
            y_mm = start_y_mm + digit * row_gap_mm
            y_centro = mm_to_px_y(y_mm)

            score = score_bolha(
                image=image,
                thresh=thresh,
                x_centro=x_centro,
                y_centro=y_centro,
                raio=4,
                gray=gray,
                hsv=hsv,
            )

            scores.append(score)

        if settings.DEBUG:
            print(f"Scores aluno coluna {idx_coluna}:", scores)

        digito = escolher_marcacao(
            scores,
            limite_minimo=0.28,
            diferenca_minima=0.10,
        )

        if digito is None:
            numero += "?"
        else:
            numero += str(digito)

    return numero


def processar_respostas(image, thresh, questions_count, options_count):
    """
    Lê as respostas usando a grade fixa do modelo gerado.

    No template_generator.py:
    start_x_questions = 68mm
    start_y_questions = 78mm
    column_width = 50mm para 4 alternativas e 60mm para 5 alternativas
    question_row_gap = 7mm
    option_gap = 8mm
    x da bolha = col_x + 15mm + opção * 8mm
    """

    respostas = []
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for question_index in range(questions_count):
        question_number = question_index + 1

        col_x_base_mm, y_mm = question_position_mm(
            question_index,
            questions_count,
            options_count,
        )

        y_centro = mm_to_px_y(y_mm)

        scores = []

        for option_index in range(options_count):
            x_mm = question_option_x_mm(col_x_base_mm, option_index)
            x_centro = mm_to_px_x(x_mm)

            score = score_bolha(
                image=image,
                thresh=thresh,
                x_centro=x_centro,
                y_centro=y_centro,
                raio=4,
                gray=gray,
                hsv=hsv,
            )

            scores.append(score)

        if settings.DEBUG:
            print(f"Scores questão {question_number}:", scores)

        marcada = escolher_marcacao(
            scores,
            limite_minimo=0.28,
            diferenca_minima=0.10,
        )

        if marcada is None:
            respostas.append(None)
        else:
            respostas.append(LETRAS[marcada])

    return respostas


def calcular_nota(respostas, gabarito):
    nota = 0

    if not gabarito:
        return nota

    for i in range(min(len(respostas), len(gabarito))):
        if respostas[i] == gabarito[i]:
            nota += 1

    return nota


def salvar_debug(image, thresh, bubbles, questions_count, options_count):
    debug_img = image.copy()

    # Desenha bolhas detectadas por contorno
    for i, (x, y, w, h) in enumerate(bubbles):
        cv2.rectangle(
            debug_img,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2,
        )

        cv2.putText(
            debug_img,
            str(i),
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 0, 255),
            1,
        )

    # Desenha pontos do número do aluno
    colunas_x_mm = STUDENT_NUMBER_COLUMNS_X_MM
    start_y_mm = STUDENT_NUMBER_START_Y_MM
    row_gap_mm = STUDENT_NUMBER_ROW_GAP_MM

    for x_mm in colunas_x_mm:
        for digit in range(10):
            x = int(mm_to_px_x(x_mm))
            y = int(mm_to_px_y(start_y_mm + digit * row_gap_mm))

            cv2.circle(debug_img, (x, y), 4, (255, 0, 0), 2)

    # Desenha pontos das questões
    for question_index in range(questions_count):
        col_x_base_mm, y_mm = question_position_mm(
            question_index,
            questions_count,
            options_count,
        )

        y = int(mm_to_px_y(y_mm))

        for option_index in range(options_count):
            x_mm = question_option_x_mm(col_x_base_mm, option_index)
            x = int(mm_to_px_x(x_mm))

            cv2.circle(debug_img, (x, y), 4, (0, 0, 255), 2)

    cv2.imwrite("debug_resultado.jpg", debug_img)
    cv2.imwrite("debug_threshold.jpg", thresh)


def process_image(
    path,
    gabarito=None,
    questions_count=8,
    options_count=5,
):
    raw_image = load_image_for_omr(path)

    try:
        image = align_sheet(
            raw_image, output_width=IMAGE_WIDTH, output_height=IMAGE_HEIGHT, debug=settings.DEBUG
        )
        if settings.DEBUG:
            print("Alinhamento: OK (marcadores detectados)")
    except Exception as exc:
        if settings.DEBUG:
            print("Alinhamento: falhou ao detectar marcadores")
        raise ValueError(
            "Nao foi possivel alinhar o cartao. Garanta que os quatro marcadores pretos aparecam na foto."
        ) from exc

    image, thresh = preprocess_image_from_array(image)

    bubbles = find_bubbles(thresh)

    if settings.DEBUG:
        print(f"Encontrou {len(bubbles)} bolhas (antes do filtro)")

    h_img, w_img = thresh.shape

    filtered = []

    for x, y, w, h in bubbles:
        if x < 20 or y < 20 or x > w_img - 20 or y > h_img - 20:
            continue

        filtered.append((x, y, w, h))

    bubbles = filtered

    if settings.DEBUG:
        print(f"Após filtro de borda: {len(bubbles)} bolhas")

    numero_aluno = ler_numero_aluno(image, thresh)

    if settings.DEBUG:
        print("Número do aluno:", numero_aluno)

    respostas = processar_respostas(
        image=image,
        thresh=thresh,
        questions_count=questions_count,
        options_count=options_count,
    )

    if settings.DEBUG:
        print("Respostas:", respostas)

    if gabarito is None:
        gabarito = []

    nota = calcular_nota(respostas, gabarito)

    if settings.DEBUG:
        print(f"Nota: {nota}/{len(gabarito)}")

    if settings.DEBUG:
        salvar_debug(
            image=image,
            thresh=thresh,
            bubbles=bubbles,
            questions_count=questions_count,
            options_count=options_count,
        )

    return {
        "numero_aluno": numero_aluno,
        "respostas": respostas,
        "total": len(respostas),
        "nota": nota,
    }
