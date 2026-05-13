import cv2
import numpy as np

from .layout import (
    MARKER_SIZE_MM,
    PAGE_HEIGHT_MM,
    PAGE_WIDTH_MM,
    READ_AREA_BOTTOM_MM,
    READ_AREA_LEFT_MM,
    READ_AREA_RIGHT_MM,
    READ_AREA_TOP_MM,
)


def distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


def _resize_for_detection(image, max_side=1200):
    h, w = image.shape[:2]
    longest = max(h, w)

    if longest <= max_side:
        return image, 1.0

    scale = max_side / float(longest)
    resized = cv2.resize(
        image,
        (int(w * scale), int(h * scale)),
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale


def find_markers(image, debug=False):
    """
    Detecta os marcadores quadrados pretos da folha.
    A imagem recebida aqui ja pode estar reduzida para estabilizar fotos grandes
    de celular.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    _, otsu = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU,
    )

    adaptive = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        41,
        8,
    )

    thresh = cv2.bitwise_or(otsu, adaptive)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    image_h, image_w = image.shape[:2]
    min_dim = min(image_h, image_w)
    min_marker_side = max(8, int(min_dim * 0.012))
    max_marker_side = max(35, int(min_dim * 0.10))
    min_area = max(80, min_marker_side * min_marker_side * 0.45)
    max_area = max_marker_side * max_marker_side

    markers = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < min_area or area > max_area:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        if w == 0 or h == 0:
            continue

        aspect_ratio = w / float(h)
        extent = area / float(w * h)

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        is_square_like = 0.65 < aspect_ratio < 1.45
        is_filled = extent > 0.45
        has_corners = 4 <= len(approx) <= 6
        valid_size = (
            min_marker_side <= w <= max_marker_side and min_marker_side <= h <= max_marker_side
        )

        if is_square_like and is_filled and has_corners and valid_size:
            markers.append(
                {
                    "center": (x + w / 2, y + h / 2),
                    "box": (x, y, w, h),
                    "area": area,
                }
            )

    return markers


def scale_markers(markers, scale):
    if scale == 1.0:
        return markers

    inv = 1.0 / scale
    scaled = []

    for marker in markers:
        cx, cy = marker["center"]
        x, y, w, h = marker["box"]
        scaled.append(
            {
                "center": (cx * inv, cy * inv),
                "box": (
                    int(round(x * inv)),
                    int(round(y * inv)),
                    int(round(w * inv)),
                    int(round(h * inv)),
                ),
                "area": marker["area"] * inv * inv,
            }
        )

    return scaled


def choose_corner_markers(markers, image_shape):
    """
    Escolhe marcadores extremos e mantem a ordem:
    top-left, top-right, bottom-right, bottom-left.
    """
    points = np.array([m["center"] for m in markers], dtype="float32")

    sums = points[:, 0] + points[:, 1]
    diffs = points[:, 0] - points[:, 1]

    indexes = [
        int(np.argmin(sums)),
        int(np.argmax(diffs)),
        int(np.argmax(sums)),
        int(np.argmin(diffs)),
    ]

    if len(set(indexes)) < 4:
        h, w = image_shape[:2]
        corners = {
            "top_left": (0, 0),
            "top_right": (w, 0),
            "bottom_right": (w, h),
            "bottom_left": (0, h),
        }

        selected = []
        used = set()
        for corner_point in corners.values():
            ordered = sorted(
                enumerate(markers),
                key=lambda item: distance(item[1]["center"], corner_point),
            )
            for idx, marker in ordered:
                if idx not in used:
                    used.add(idx)
                    selected.append(marker)
                    break
    else:
        selected = [markers[i] for i in indexes]

    source_points = np.array([marker["center"] for marker in selected], dtype="float32")

    selected_by_name = {
        "top_left": selected[0],
        "top_right": selected[1],
        "bottom_right": selected[2],
        "bottom_left": selected[3],
    }

    return source_points, selected_by_name


def marker_destination_points(output_width, output_height):
    half = MARKER_SIZE_MM / 2

    points_mm = [
        (READ_AREA_LEFT_MM + half, READ_AREA_TOP_MM + half),
        (READ_AREA_RIGHT_MM - half, READ_AREA_TOP_MM + half),
        (READ_AREA_RIGHT_MM - half, READ_AREA_BOTTOM_MM - half),
        (READ_AREA_LEFT_MM + half, READ_AREA_BOTTOM_MM - half),
    ]

    return np.array(
        [
            [
                x_mm * output_width / PAGE_WIDTH_MM,
                y_mm * output_height / PAGE_HEIGHT_MM,
            ]
            for x_mm, y_mm in points_mm
        ],
        dtype="float32",
    )


def align_sheet(image, output_width=600, output_height=800, debug=False):
    """
    Alinha a folha usando os 4 marcadores quadrados pretos.
    Os marcadores nao ficam nos cantos da pagina; por isso eles sao mapeados
    para suas coordenadas fisicas no template A4, e nao para os cantos da imagem.
    """
    detection_image, scale = _resize_for_detection(image)
    markers = scale_markers(find_markers(detection_image, debug=debug), scale)

    if len(markers) < 4:
        raise ValueError(
            f"Nao foi possivel detectar 4 marcadores quadrados. Detectados: {len(markers)}"
        )

    source_points, selected = choose_corner_markers(markers, image.shape)
    destination_points = marker_destination_points(output_width, output_height)

    matrix = cv2.getPerspectiveTransform(source_points, destination_points)

    aligned = cv2.warpPerspective(
        image,
        matrix,
        (output_width, output_height),
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255),
    )

    if debug:
        debug_img = image.copy()

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
                1,
            )

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
                1,
            )

        cv2.imwrite("debug_markers.jpg", debug_img)
        cv2.imwrite("debug_aligned.jpg", aligned)

    return aligned
