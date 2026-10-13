"""
Entrena el modelo de piezas (21 clases) en la PC (CPU).

Uso, desde la carpeta CarFix:
    python training/scripts/train_parts.py
"""

from ultralytics import YOLO

from paths import PARTS_DATASET, RUNS_DIR, fix_data_yaml

RUN_NAME = "automotive_parts_v2"

model = YOLO("yolo11n-seg.pt")
model.train(
    data=str(fix_data_yaml(PARTS_DATASET)),
    imgsz=640,
    epochs=100,
    batch=8,
    device="cpu",  # sin GPU NVIDIA
    workers=4,
    patience=20,
    save=True,
    plots=True,
    project=str(RUNS_DIR),
    name=RUN_NAME,
)
print(f"Listo. Pesos en {RUNS_DIR / RUN_NAME / 'weights'}")
