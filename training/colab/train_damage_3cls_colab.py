# Entrenamiento del modelo de daños con 3 clases (Rotura, Golpe, Pintura) en Google Colab.
#
# Uso en Colab:
#   1. Entorno de ejecución > Cambiar tipo > GPU T4.
#   2. !pip install -q ultralytics
#   3. Subí la carpeta training/data/processed/damages_3cls (generada con remap_damage_3cls.py)
#      y ajustá DATASET_DIR.
#   4. !python train_damage_3cls_colab.py
#
# Con SINGLE_CLS = True entrena "hay daño / no hay daño" (una sola clase),
# para medir cuánto detecta el modelo sin importar el tipo.

from pathlib import Path
import shutil

from ultralytics import YOLO

DATASET_DIR = Path("/content/damages_3cls")
SINGLE_CLS = False

CLASSES = ["Rotura", "Golpe", "Pintura"]
RUN_NAME = "automotive_damage_any" if SINGLE_CLS else "automotive_damage_3cls"

# Reescribir data.yaml con la ruta de Colab.
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

# El modelo "n" rindió igual que el "s" con este dataset y pesa 3 veces menos.
model = YOLO("yolo11n-seg.pt")

model.train(
    data=str(data_yaml),
    single_cls=SINGLE_CLS,
    imgsz=1024,
    epochs=150,
    batch=16,
    device=0,
    workers=2,
    cache=True,
    patience=30,

    # Algo más de aumentación: hay pocas imágenes.
    degrees=5.0,
    copy_paste=0.3,
    mixup=0.1,

    save=True,
    plots=True,
    name=RUN_NAME,
)

if (DATASET_DIR / "test" / "images").exists():
    best = YOLO(f"/content/runs/segment/{RUN_NAME}/weights/best.pt")
    metrics = best.val(
        data=str(data_yaml),
        split="test",
        imgsz=1024,
        single_cls=SINGLE_CLS,
        plots=True,
    )
    print(f"Test máscara mAP50: {metrics.seg.map50:.3f}  mAP50-95: {metrics.seg.map:.3f}")

# Bajá el zip y descomprimilo en CarFix/training/runs/<nombre>.
archive = shutil.make_archive(f"/content/{RUN_NAME}", "zip", f"/content/runs/segment/{RUN_NAME}")
print("Descargá:", archive)
