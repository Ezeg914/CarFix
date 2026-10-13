"""Flujo completo: imagen -> vehículo -> piezas y daños -> presupuesto."""

from dataclasses import dataclass

import numpy as np

from .assignment import assign_damages
from .budget import build_budget
from .config import Settings
from .detection import Detection, Detector, keep_on_vehicle
from .imaging import draw
from .rules import load_rules


@dataclass
class FrameAnalysis:
    image: np.ndarray          # recorte del vehículo (o imagen completa si no se encontró)
    found_vehicle: bool
    parts: list[Detection]
    damages: list[Detection]   # ya filtrados a la silueta del vehículo
    dropped: int               # daños descartados por caer fuera del vehículo
    assigned: dict
    unassigned: list

    def overlay(self) -> np.ndarray:
        return draw(self.image, self.parts, self.damages)


@dataclass
class Result:
    budget: dict
    overlay: np.ndarray


class Analyzer:
    """Punto de entrada del backend. Se crea una vez (carga los modelos) y se reutiliza."""

    def __init__(self, settings: Settings | None = None):
        self.settings = settings or Settings()
        self.detector = Detector(self.settings)
        self.rules = load_rules(self.settings.rules_csv)

    def analyze_frame(self, image) -> FrameAnalysis:
        s = self.settings
        crop = self.detector.find_vehicle(image)
        if crop is None:
            vehicle_mask = np.ones(image.shape[:2], dtype=bool)
        else:
            image = image[crop.y0:crop.y1, crop.x0:crop.x1]
            vehicle_mask = crop.mask[crop.y0:crop.y1, crop.x0:crop.x1]

        parts = self.detector.parts(image)
        damages, dropped = keep_on_vehicle(self.detector.damages(image), vehicle_mask, s.min_on_vehicle)
        assigned, unassigned = assign_damages(parts, damages, s)
        return FrameAnalysis(image, crop is not None, parts, damages, dropped, assigned, unassigned)

    def analyze_image(self, image, vehicle: dict) -> Result:
        frame = self.analyze_frame(image)
        budget = build_budget(frame.assigned, frame.unassigned, self.rules, vehicle, self.settings)
        budget["modo"] = "foto"
        budget["vehiculo_encontrado"] = frame.found_vehicle
        budget["danios_fuera_del_vehiculo"] = frame.dropped
        return Result(budget, frame.overlay())
