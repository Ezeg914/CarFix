"""Modelos de visión: vehículo, piezas y daños."""

from typing import NamedTuple, Optional

import cv2
import numpy as np

from .config import Settings


class Detection(NamedTuple):
    name: str
    conf: float
    mask: np.ndarray  # booleana, del tamaño de la imagen analizada


class VehicleCrop(NamedTuple):
    x0: int
    y0: int
    x1: int
    y1: int
    mask: np.ndarray  # silueta del vehículo en la imagen completa


def masks_from_result(result, shape) -> list[Detection]:
    """Convierte un resultado de Ultralytics en detecciones con máscara."""
    if result.masks is None:
        return []
    h, w = shape
    detections = []
    for polygon, cls, conf in zip(result.masks.xy, result.boxes.cls, result.boxes.conf):
        if len(polygon) < 3:
            continue
        mask = np.zeros((h, w), dtype=np.uint8)
        cv2.fillPoly(mask, [polygon.astype(np.int32)], 1)
        detections.append(Detection(result.names[int(cls)], float(conf), mask.astype(bool)))
    return detections


def keep_on_vehicle(damages, vehicle_mask, min_on_vehicle) -> tuple[list[Detection], int]:
    """Recorta cada daño a la silueta del vehículo y descarta los que caen afuera."""
    kept, dropped = [], 0
    for det in damages:
        area = det.mask.sum()
        inside = np.logical_and(det.mask, vehicle_mask)
        if area == 0 or inside.sum() / area < min_on_vehicle:
            dropped += 1
            continue
        kept.append(det._replace(mask=inside))
    return kept, dropped


class Detector:
    """Carga los tres modelos una sola vez y los reutiliza en cada análisis."""

    def __init__(self, settings: Settings):
        from ultralytics import YOLO

        for path in (settings.vehicle_model, settings.parts_model, settings.damage_model):
            if not path.exists():
                raise FileNotFoundError(f"No se encontró el modelo: {path}")
        self.settings = settings
        self.vehicle_model = YOLO(str(settings.vehicle_model))
        self.parts_model = YOLO(str(settings.parts_model))
        self.damage_model = YOLO(str(settings.damage_model))

    def find_vehicle(self, image) -> Optional[VehicleCrop]:
        """Busca el vehículo de mayor superficie y devuelve el recorte a su alrededor."""
        s = self.settings
        result = self.vehicle_model.predict(image, conf=s.vehicle_conf, verbose=False)[0]
        vehicles = [d for d in masks_from_result(result, image.shape[:2]) if d.name in s.vehicle_classes]
        if not vehicles:
            return None
        mask = max(vehicles, key=lambda d: d.mask.sum()).mask
        ys, xs = np.nonzero(mask)
        h, w = mask.shape
        mx = int((xs.max() - xs.min()) * s.crop_margin)
        my = int((ys.max() - ys.min()) * s.crop_margin)
        return VehicleCrop(
            x0=max(int(xs.min()) - mx, 0), x1=min(int(xs.max()) + mx + 1, w),
            y0=max(int(ys.min()) - my, 0), y1=min(int(ys.max()) + my + 1, h),
            mask=mask,
        )

    def parts(self, image) -> list[Detection]:
        s = self.settings
        result = self.parts_model.predict(image, conf=s.part_conf, imgsz=s.part_imgsz, verbose=False)[0]
        return masks_from_result(result, image.shape[:2])

    def damages(self, image) -> list[Detection]:
        s = self.settings
        result = self.damage_model.predict(image, conf=s.damage_conf, imgsz=s.damage_imgsz, verbose=False)[0]
        return masks_from_result(result, image.shape[:2])
