import cv2
import numpy as np
from django.conf import settings


def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def find_markers(image, debug=False):
    """
    Detecta marcadores quadrados pretos da folha.
    Evita capturar bolhas circulares preenchidas.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # pega regiões bem escuras
    _, thresh = cv2.threshold(
        blur,
        90,
        255,
        cv2.THRESH_BINARY_INV
    )

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    markers = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 120:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        if w == 0 or h == 0:
            continue

        aspect_ratio = w / float(h)
        extent = area / float(w * h)

        # aproxima contorno para verificar se é quadrado/retângulo
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        # filtros principais:
        # - formato quadrado
        # - preenchido
        # - 4 vértices
        # - tamanho compatível com marcador
        is_square_like = 0.75 < aspect_ratio < 1.30
        is_filled = extent > 0.60
        has_four_corners = len(approx) == 4
        valid_size = 10 < w < 60 and 10 < h < 60

        if is_square_like and is_filled and has_four_corners and valid_size:
            cx = x + w / 2
            cy = y + h / 2

            markers.append({
                "center": (cx, cy),
                "box": (x, y, w, h),
                "area": area
            })

    return markers


def choose_corner_markers(markers, image_shape):
    """
    Escolhe 4 marcadores mais próximos dos cantos da imagem.
    """
    h, w = image_shape[:2]

    corners = {
        "top_left": (0, 0),
        "top_right": (w, 0),
        "bottom_right": (w, h),
        "bottom_left": (0, h),
    }

    selected = {}

    for name, corner_point in corners.items():
        closest_marker = min(
            markers,
            key=lambda m: distance(m["center"], corner_point)
        )
        selected[name] = closest_marker

    points = np.array([
        selected["top_left"]["center"],
        selected["top_right"]["center"],
        selected["bottom_right"]["center"],
        selected["bottom_left"]["center"],
    ], dtype="float32")

    return points, selected


def align_sheet(image, output_width=600, output_height=800, debug=False):
    """
    Alinha a folha usando 4 marcadores quadrados pretos.
    """
    markers = find_markers(image, debug=debug)

    if len(markers) < 4:
        raise ValueError(
            f"Não foi possível detectar 4 marcadores quadrados. Detectados: {len(markers)}"
        )

    source_points, selected = choose_corner_markers(markers, image.shape)

    destination_points = np.array([
        [0, 0],
        [output_width - 1, 0],
        [output_width - 1, output_height - 1],
        [0, output_height - 1],
    ], dtype="float32")

    matrix = cv2.getPerspectiveTransform(source_points, destination_points)

    aligned = cv2.warpPerspective(
        image,
        matrix,
        (output_width, output_height)
    )

    if debug:
        debug_img = image.copy()

        # desenha todos os candidatos
        for i, marker in enumerate(markers):
            x, y, w, h = marker["box"]

            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(
                debug_img,
                str(i),
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1
            )

        # destaca os 4 usados no alinhamento
        for name, marker in selected.items():
            x, y, w, h = marker["box"]

            cv2.rectangle(debug_img, (x, y), (x + w, y + h), (0, 255, 255), 3)
            cv2.putText(
                debug_img,
                name,
                (x, y + h + 15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (0, 255, 255),
                1
            )

        cv2.imwrite("debug_markers.jpg", debug_img)
        cv2.imwrite("debug_aligned.jpg", aligned)

    return aligned