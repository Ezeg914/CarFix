"""
Modo video (experimental): analiza varios cuadros y solo cuenta los daños que
se repiten. Los reflejos se mueven al mover la cámara; un daño real se queda.
"""

import cv2
import numpy as np

from .budget import build_budget
from .pipeline import Analyzer, Result


def read_frames(path, fps):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise ValueError(f"No se pudo abrir el video: {path}")
    step = max(int(round((cap.get(cv2.CAP_PROP_FPS) or 30) / fps)), 1)
    index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if index % step == 0:
            yield frame
        index += 1
    cap.release()


def aggregate(frames, settings):
    """
    Por pieza (por nombre) cuenta en cuántos cuadros se ve y en cuántos tiene
    cada tipo de daño confiable. Devuelve (assigned, descartados).
    Limitación: las piezas repetidas (dos ópticas) se juntan en una.
    """
    visible, hits = {}, {}
    for frame in frames:
        for name in {p.name for p in frame.parts}:
            visible[name] = visible.get(name, 0) + 1
        per_part = {}
        for (_, name), damages in frame.assigned.items():
            for d in damages:
                if d["conf"] >= settings.min_decision_conf(d["categoria"]):
                    per_part.setdefault(name, {}).setdefault(d["categoria"], []).append(d)
        for name, by_cat in per_part.items():
            for category, ds in by_cat.items():
                hits.setdefault(name, {}).setdefault(category, []).append(max(ds, key=lambda d: d["cobertura"]))

    assigned, discarded = {}, []
    for name, by_cat in hits.items():
        seen = visible.get(name, 0)
        for category, ds in by_cat.items():
            if seen < settings.min_visible_frames or len(ds) / max(seen, 1) < settings.video_persistence:
                discarded.append({"pieza": name, "categoria": category, "cuadros": len(ds), "visible": seen})
                continue
            assigned.setdefault((name, name), []).append({
                "categoria": category,
                "clase": category,
                "conf": round(float(np.median([d["conf"] for d in ds])), 3),
                "cobertura": round(float(np.median([d["cobertura"] for d in ds])), 3),
                "cuadros": f"{len(ds)}/{seen}",
            })
    return assigned, discarded


def analyze_video(analyzer: Analyzer, path, vehicle: dict, progress=None) -> Result:
    s = analyzer.settings
    frames = []
    for image in read_frames(path, s.video_fps):
        frame = analyzer.analyze_frame(image)
        if frame.found_vehicle:
            frames.append(frame)
            if progress:
                progress(len(frames))
    if not frames:
        raise ValueError("No se encontró el vehículo en ningún cuadro del video "
                         "(si es .mov de iPhone, probá convertirlo a .mp4).")

    assigned, discarded = aggregate(frames, s)
    for d in discarded:
        d["nombre"] = analyzer.rules.get(d["pieza"], {}).get("nombre", d["pieza"])
    # En video, la repetición entre cuadros reemplaza a la confianza mínima por pieza.
    budget = build_budget(assigned, [], analyzer.rules, vehicle, s, use_part_conf=False)
    budget.update(modo="video", cuadros_analizados=len(frames), descartados_por_no_repetirse=discarded)

    confirmed = {name for (_, name) in assigned}
    best = max(frames, key=lambda f: sum(1 for (_, n) in f.assigned if n in confirmed))
    return Result(budget, best.overlay())
