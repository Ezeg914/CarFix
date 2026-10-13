"""Lectura de imágenes y dibujo de resultados."""

from pathlib import Path

import cv2
import numpy as np


def load_image(path) -> np.ndarray:
    """Abre la imagen con OpenCV y, si no puede (AVIF, etc.), con Pillow. Devuelve BGR."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo: {path}")
    image = cv2.imread(str(path))
    if image is not None:
        return image
    try:
        from PIL import Image

        with Image.open(path) as im:
            rgb = np.array(im.convert("RGB"))
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    except Exception as e:
        raise ValueError(
            f"No se pudo abrir la imagen: {path} ({e}). "
            "Puede que el formato real no sea JPG (por ej. AVIF). Convertila a JPG."
        ) from e


def decode_image(data: bytes) -> np.ndarray:
    """Decodifica una imagen recibida en memoria (por ej. desde la API)."""
    image = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if image is not None:
        return image
    from io import BytesIO

    from PIL import Image

    with Image.open(BytesIO(data)) as im:
        return cv2.cvtColor(np.array(im.convert("RGB")), cv2.COLOR_RGB2BGR)


def draw(image, parts, damages) -> np.ndarray:
    """Dibuja las piezas (contorno celeste) y los daños (relleno rojo)."""
    out = image.copy()
    for det in parts:
        contours, _ = cv2.findContours(det.mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(out, contours, -1, (255, 200, 0), 2)
        ys, xs = np.nonzero(det.mask)
        cv2.putText(out, det.name, (int(xs.mean()), int(ys.mean())),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 0), 2)
    for det in damages:
        layer = out.copy()
        layer[det.mask] = (0, 0, 255)
        out = cv2.addWeighted(layer, 0.4, out, 0.6, 0)
        ys, xs = np.nonzero(det.mask)
        cv2.putText(out, f"{det.name} {det.conf:.0%}", (int(xs.min()), int(ys.min()) + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    return out
