import base64

import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from carfix.api import MAX_OVERLAY_SIDE, app, get_analyzer
from carfix.pipeline import Result


class FakeAnalyzer:
    """Reemplaza al Analyzer real para no cargar los modelos en los tests."""

    def __init__(self):
        self.calls = []

    def analyze_image(self, image, vehicle):
        self.calls.append((image.shape, vehicle))
        budget = {"vehiculo": vehicle, "piezas": [], "revisar": [], "total": 0.0}
        return Result(budget, np.zeros((2000, 1000, 3), dtype=np.uint8))


@pytest.fixture
def fake():
    analyzer = FakeAnalyzer()
    app.dependency_overrides[get_analyzer] = lambda: analyzer
    yield analyzer
    app.dependency_overrides.clear()


@pytest.fixture
def client(fake):
    # Sin "with": no corre el arranque, que cargaría los modelos reales.
    return TestClient(app)


def jpeg_bytes(h=60, w=80):
    ok, buf = cv2.imencode(".jpg", np.full((h, w, 3), 128, dtype=np.uint8))
    return buf.tobytes()


def test_salud(client):
    r = client.get("/salud")
    assert r.status_code == 200
    assert r.json()["estado"] == "ok"


def test_analizar_devuelve_presupuesto_e_imagen(client, fake):
    r = client.post(
        "/analizar",
        files={"foto": ("auto.jpg", jpeg_bytes(), "image/jpeg")},
        data={"marca": " Volkswagen ", "modelo": "Vento", "anio": "2012"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["presupuesto"]["vehiculo"] == {"marca": "Volkswagen", "modelo": "Vento", "anio": "2012"}
    assert fake.calls[0][0] == (60, 80, 3)

    overlay = cv2.imdecode(np.frombuffer(base64.b64decode(body["imagen"]), np.uint8), cv2.IMREAD_COLOR)
    assert max(overlay.shape[:2]) == MAX_OVERLAY_SIDE


def test_analizar_rechaza_archivo_que_no_es_imagen(client, fake):
    r = client.post("/analizar", files={"foto": ("nota.txt", b"hola", "text/plain")})
    assert r.status_code == 400
    assert fake.calls == []


def test_analizar_exige_foto(client):
    assert client.post("/analizar", data={"marca": "VW"}).status_code == 422
