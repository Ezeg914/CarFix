"""Rutas y parámetros del backend. Todo lo ajustable está acá."""

from dataclasses import dataclass, field
from pathlib import Path

# backend/carfix/config.py -> raíz del proyecto CarFix
ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = ROOT / "backend"
MODELS_DIR = ROOT / "models"
OUTPUTS_DIR = ROOT / "outputs"


@dataclass(frozen=True)
class Settings:
    # Modelos
    parts_model: Path = MODELS_DIR / "parts.pt"
    damage_model: Path = MODELS_DIR / "damage.pt"
    # Modelo general de Ultralytics (COCO), solo para encontrar el vehículo.
    vehicle_model: Path = MODELS_DIR / "vehicle.pt"

    rules_csv: Path = BACKEND_DIR / "data" / "reglas_presupuesto.csv"
    outputs_dir: Path = OUTPUTS_DIR

    # Vehículo
    vehicle_classes: frozenset = frozenset({"car", "truck", "bus"})
    vehicle_conf: float = 0.40
    # Margen alrededor del vehículo al recortar (fracción del ancho/alto).
    crop_margin: float = 0.05
    # Un daño se descarta si menos de esta fracción cae sobre el vehículo.
    min_on_vehicle: float = 0.50

    # Confianza mínima de cada modelo para considerar una detección.
    part_conf: float = 0.15
    damage_conf: float = 0.20

    # Resolución con la que se entrenó cada modelo.
    part_imgsz: int = 640
    damage_imgsz: int = 1024

    # Un daño se asigna a una pieza si al menos esta fracción del daño cae
    # sobre ella, o si cubre al menos MIN_PART_COVERAGE de la pieza.
    min_overlap: float = 0.20
    min_part_coverage: float = 0.10
    # Para sumar un daño a una pieza secundaria (por ej. la óptica al lado de
    # un paragolpes roto), tiene que cubrir al menos esta fracción de ella.
    min_secondary_coverage: float = 0.30

    # Daños con menos confianza que esto se muestran, pero no deciden cambiar
    # ni reparar (suelen ser reflejos o falsos positivos).
    decision_conf: float = 0.35
    # Los golpes son la clase más floja del modelo: se acepta menos confianza.
    decision_conf_by_category: dict = field(default_factory=lambda: {"Golpe": 0.20})

    # Modo video
    video_fps: float = 2
    min_visible_frames: int = 3
    # Un daño cuenta si aparece en al menos esta fracción de los cuadros donde
    # se ve la pieza. Los reflejos se mueven con la cámara; un daño real no.
    video_persistence: float = 0.5

    def min_decision_conf(self, category: str) -> float:
        return self.decision_conf_by_category.get(category, self.decision_conf)


# Piezas que reciben también daños asignados a una pieza vecina. A la chapa
# solo se le asigna el daño si es la pieza principal afectada.
SECONDARY_PARTS = frozenset({
    "Headlight", "Tail-light", "Mirror",
    "Windshield", "Back-windshield", "Front-window", "Back-window",
})

# Clases del modelo de daños -> categoría del presupuesto. Cubre el modelo de
# 8 clases y el de 3 clases (que ya devuelve la categoría).
CATEGORY = {
    "Missing part": "Rotura",
    "Broken part": "Rotura",
    "Cracked": "Rotura",
    "Dent": "Golpe",
    "Scratch": "Pintura",
    "Flaking": "Pintura",
    "Paint chip": "Pintura",
    "Corrosion": "Pintura",
    "Rotura": "Rotura",
    "Golpe": "Golpe",
    "Pintura": "Pintura",
}

VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".avi", ".mkv", ".m4v", ".webm"})
