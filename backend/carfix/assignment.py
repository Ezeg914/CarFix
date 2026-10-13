"""Cruce de daños con piezas."""

import numpy as np

from .config import CATEGORY, SECONDARY_PARTS, Settings


def part_keys(parts):
    """
    Si el modelo detecta la misma pieza dos veces (dos ópticas, dos puertas),
    las distingue con un sufijo: Headlight, Headlight#2.
    """
    seen = {}
    keyed = []
    for det in parts:
        seen[det.name] = seen.get(det.name, 0) + 1
        key = det.name if seen[det.name] == 1 else f"{det.name}#{seen[det.name]}"
        keyed.append((key, det))
    return keyed


def assign_damages(parts, damages, settings: Settings):
    """
    Asigna cada daño a la pieza que más superficie del daño contiene. Además,
    a ópticas, vidrios y espejos vecinos si el daño los cubre lo suficiente.

    Devuelve:
      assigned:   {(clave, pieza): [ {categoria, clase, conf, cobertura} ]}
      unassigned: [ {clase, conf} ] daños que no caen sobre ninguna pieza
    """
    keyed = part_keys(parts)
    assigned, unassigned = {}, []

    for dmg in damages:
        d_area = dmg.mask.sum()
        if d_area == 0:
            continue
        candidates = []
        for key, part in keyed:
            inter = np.logical_and(dmg.mask, part.mask).sum()
            if inter == 0:
                continue
            overlap = inter / d_area
            coverage = inter / max(part.mask.sum(), 1)
            if overlap < settings.min_overlap and coverage < settings.min_part_coverage:
                continue
            candidates.append((overlap, coverage, key, part.name))

        if not candidates:
            unassigned.append({"clase": dmg.name, "conf": round(dmg.conf, 3)})
            continue

        main = max(candidates, key=lambda c: c[0])
        targets = [main] + [
            c for c in candidates
            if c is not main and c[3] in SECONDARY_PARTS and c[1] >= settings.min_secondary_coverage
        ]
        for _, coverage, key, name in targets:
            assigned.setdefault((key, name), []).append({
                "categoria": CATEGORY.get(dmg.name, "Pintura"),
                "clase": dmg.name,
                "conf": round(dmg.conf, 3),
                "cobertura": round(float(coverage), 3),
            })
    return assigned, unassigned
