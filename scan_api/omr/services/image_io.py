import cv2
import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


def register_heif_opener():
    try:
        from pillow_heif import register_heif_opener as _register_heif_opener
    except ImportError:
        return

    _register_heif_opener()


def load_image_for_omr(path):
    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)

            if img.mode in ("RGBA", "LA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.getchannel("A"))
                img = background
            else:
                img = img.convert("RGB")

            rgb = np.array(img)
            return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except (UnidentifiedImageError, OSError, ValueError):
        image = cv2.imread(path)
        if image is None:
            raise ValueError(f"Imagem nao encontrada ou formato nao suportado: {path}")
        return image
