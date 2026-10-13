# Entrenamiento del modelo de daños v2 en Google Colab (GPU T4).
# Mismas 8 clases que v1. Cambios: modelo "s", imgsz 1024, batch 16, patience 40.
#
# Uso en Colab:
#   1. Entorno de ejecución > Cambiar tipo > GPU T4.
#   2. !pip install -q ultralytics
#   3. Subí el dataset (carpeta con train/, val/, test/ y data.yaml) y ajustá DATASET_DIR.
#   4. !python train_damage_v2_colab.py   (o pegá el contenido en una celda)

from pathlib import Path
import shutil

from ultralytics import YOLO

DATASET_DIR = Path("/content/damages/damages")
RUN_NAME = "automotive_damage_v2"

CLASSES = [
    "Missing part",
    "Broken part",
    "Scratch",
    "Cracked",
    "Dent",
    "Flaking",
    "Paint chip",
    "Corrosion",
]

# Reescribir data.yaml con la ruta de Colab
# (el original apunta a una carpeta de Windows).
data_yaml = DATASET_DIR / "data.yaml"
names = ", ".join(f'"{c}"' for c in CLASSES)
data_yaml.write_text(
    f"path: {DATASET_DIR.as_posix()}\n"
    "train: train/images\n"
    "val: val/images\n"
    "test: test/images\n\n"
    f"nc: {len(CLASSES)}\n"
    f"names: [{names}]\n",
    encoding="utf-8",
)
print("data.yaml listo:", data_yaml)

model = YOLO("yolo11s-seg.pt")

model.train(
    data=str(data_yaml),

    # Más resolución para que no se pierdan rayones y picaduras
    imgsz=1024,

    epochs=150,

    # Si da "CUDA out of memory", bajar a 8
    batch=16,

    device=0,
    workers=2,

    # Cargar imágenes en RAM (son pocas) para ir más rápido
    cache=True,

    # Más margen antes de cortar por early stopping
    patience=40,

    save=True,
    plots=True,
    name=RUN_NAME,
)

# Evaluar el mejor modelo en test (imágenes que no vio nunca)
if (DATASET_DIR / "test" / "images").exists():
    best = YOLO(f"/content/runs/segment/{RUN_NAME}/weights/best.pt")
    metrics = best.val(data=str(data_yaml), split="test", imgsz=1024, plots=True)
    print(f"Test máscara mAP50: {metrics.seg.map50:.3f}  mAP50-95: {metrics.seg.map:.3f}")

# Comprimir resultados para descargarlos y copiarlos a CarFix/training/runs/
archive = shutil.make_archive(f"/content/{RUN_NAME}", "zip", f"/content/runs/segment/{RUN_NAME}")
print("Descargá:", archive)
