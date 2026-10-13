"""Tabla de reglas y precios por pieza (backend/data/reglas_presupuesto.csv)."""

import csv
from pathlib import Path

PRICE_COLUMNS = ("repuesto", "mano_obra_cambio", "mano_obra_reparacion", "pintura")
THRESHOLD_COLUMNS = ("umbral_cambio", "umbral_rotura", "conf_minima")
VALID_TYPES = {"cambio", "chapa", "ignorar"}


def load_rules(path: Path) -> dict:
    """
    Columnas:
      pieza                 nombre de la clase en el modelo de piezas
      nombre                nombre para mostrar
      tipo                  cambio (se cambia ante cualquier daño) | chapa | ignorar
      umbral_cambio         chapa: golpe que cubre más que esto de la pieza -> cambiar
      umbral_rotura         chapa: rotura que cubre más que esto -> cambiar (si no, reparar)
      conf_minima           confianza mínima propia de la pieza (por ej. vidrios, por reflejos)
      repuesto, mano_obra_cambio, mano_obra_reparacion, pintura   precios
    """
    rules = {}
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["tipo"] not in VALID_TYPES:
                raise ValueError(f"Tipo inválido '{row['tipo']}' para {row['pieza']} en {path}")
            for key in PRICE_COLUMNS + THRESHOLD_COLUMNS:
                row[key] = float(row.get(key) or 0)
            rules[row["pieza"]] = row
    return rules
