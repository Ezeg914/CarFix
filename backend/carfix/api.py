"""
API HTTP del backend. La usa la app mobile.

Uso (desde la carpeta backend):
    uvicorn carfix.api:app --host 0.0.0.0 --port 8000

Documentación interactiva en http://localhost:8000/docs
"""

import base64
import threading
from contextlib import asynccontextmanager
from functools import lru_cache

import cv2
from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .imaging import decode_image
from .pipeline import Analyzer

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
# Lado máximo de la imagen marcada que se devuelve (para no mandar fotos enormes al celular).
MAX_OVERLAY_SIDE = 1280

# YOLO no garantiza ser seguro entre hilos: se analiza una foto a la vez.
_lock = threading.Lock()


@lru_cache
def get_analyzer() -> Analyzer:
    """Carga los modelos una sola vez y los comparte entre pedidos."""
    return Analyzer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_analyzer()  # carga los modelos al arrancar y no en el primer pedido
    yield


app = FastAPI(title="CarFix API", version=__version__, lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def encode_jpeg(image) -> str:
    h, w = image.shape[:2]
    scale = MAX_OVERLAY_SIDE / max(h, w)
    if scale < 1:
        image = cv2.resize(image, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    ok, buf = cv2.imencode(".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, 85])
    if not ok:
        raise RuntimeError("No se pudo codificar la imagen resultado")
    return base64.b64encode(buf.tobytes()).decode("ascii")


@app.get("/salud")
def salud():
    return {"estado": "ok", "version": __version__}


@app.post("/analizar")
def analizar(
    foto: UploadFile = File(..., description="foto del vehículo"),
    marca: str = Form(""),
    modelo: str = Form(""),
    anio: str = Form(""),
    analyzer: Analyzer = Depends(get_analyzer),
):
    """Analiza la foto y devuelve el presupuesto y la imagen con los daños marcados (JPEG en base64)."""
    data = foto.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"La foto supera los {MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
    try:
        image = decode_image(data)
    except Exception:
        raise HTTPException(400, "El archivo no es una imagen válida")

    vehicle = {"marca": marca.strip(), "modelo": modelo.strip(), "anio": anio.strip()}
    with _lock:
        result = analyzer.analyze_image(image, vehicle)

    return {"presupuesto": result.budget, "imagen": encode_jpeg(result.overlay)}
