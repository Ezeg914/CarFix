"""Rutas compartidas por los scripts de entrenamiento."""

from pathlib import Path

TRAINING_DIR = Path(__file__).resolve().parents[1]
ROOT = TRAINING_DIR.parent

# Datasets originales de Kaggle (humansintheloop/car-parts-and-car-damages).
# OJO: en ese dataset los nombres de carpeta están cruzados:
#   "Car damages dataset" trae las anotaciones de PIEZAS
#   "Car parts dataset"   trae las anotaciones de DAÑOS
RAW_DIR = TRAINING_DIR / "data" / "raw"
RAW_PARTS = RAW_DIR / "Car damages dataset"
RAW_DAMAGES = RAW_DIR / "Car parts dataset"

# Datasets ya convertidos a formato YOLO.
PROCESSED_DIR = TRAINING_DIR / "data" / "processed"
PARTS_DATASET = PROCESSED_DIR / "parts"
DAMAGES_DATASET = PROCESSED_DIR / "damages"
DAMAGES_3CLS_DATASET = PROCESSED_DIR / "damages_3cls"

# Resultados de cada entrenamiento (un subcarpeta por experimento).
RUNS_DIR = TRAINING_DIR / "runs"

# Modelos que usa el backend.
MODELS_DIR = ROOT / "models"


def fix_data_yaml(dataset_dir: Path) -> Path:
    """Actualiza la línea 'path:' del data.yaml a la ubicación real del dataset."""
    yaml_path = dataset_dir / "data.yaml"
    lines = yaml_path.read_text(encoding="utf-8").splitlines()
    lines = [f"path: {dataset_dir.resolve().as_posix()}" if l.startswith("path:") else l for l in lines]
    yaml_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return yaml_path
