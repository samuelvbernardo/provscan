import cv2

def find_bubbles(thresh):
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    bubbles = []

    for cnt in contours:
        area = cv2.contourArea(cnt)

        if area < 150:
            continue

        x, y, w, h = cv2.boundingRect(cnt)

        aspect_ratio = w / float(h)

        # 🔥 MAIS RESTRITIVO
        if 200 < area < 800 and 0.8 < aspect_ratio < 1.2 and 10 < w < 40:
            bubbles.append((x, y, w, h))

    return bubbles

