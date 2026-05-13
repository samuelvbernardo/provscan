import cv2

# Limites calibrados para cartões A4 impressos em 72–150 DPI, redimensionados
# para o espaço normalizado de 600×800 px usado pelo pipeline.
#
# AREA_MIN / AREA_MAX: área em px² de uma bolha preenchida na escala normalizada.
#   - Menor que AREA_MIN → ruído ou sombra
#   - Maior que AREA_MAX → contorno grande (borda do cartão, mancha, etc.)
#
# ASPECT_RATIO_MIN / MAX: bolhas são aproximadamente quadradas (círculo inscrito).
#   Valores muito fora de [0.8, 1.2] indicam riscos ou artefatos de compressão.
#
# WIDTH_MIN / WIDTH_MAX: largura esperada da bolha em px na escala normalizada.
AREA_MIN = 200
AREA_MAX = 800
ASPECT_RATIO_MIN = 0.8
ASPECT_RATIO_MAX = 1.2
WIDTH_MIN = 10
WIDTH_MAX = 40


def find_bubbles(thresh):
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    bubbles = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < AREA_MIN:
            continue

        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = w / float(h)

        if (
            AREA_MIN < area < AREA_MAX
            and ASPECT_RATIO_MIN < aspect_ratio < ASPECT_RATIO_MAX
            and WIDTH_MIN < w < WIDTH_MAX
        ):
            bubbles.append((x, y, w, h))

    return bubbles
