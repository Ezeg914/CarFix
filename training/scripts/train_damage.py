"""
Entrena el modelo de daños en la PC (CPU). Es lento: para daños conviene Colab
(ver training/colab/).

Uso, desde la carpeta CarFix:
    python training/scripts/train_damage.py
"""

from ultralytics import YOLO

from paths import DAMAGES_3CLS_DATASET, RUNS_DIR, fix_data_yaml

RUN_NAME = "automotive_damage_v4"

model = YOLO("yolo11n-seg.pt")
model.train(
    data=str(fix_data_yaml(DAMAGES_3CLS_DATASET)),
    imgsz=1024,
    epochs=150,
    batch=4,
    device="cpu",
    workers=2,
    patience=30,
    degrees=5.0,
    copy_paste=0.3,
    mixup=0.1,
    save=True,
    plots=True,
    project=str(RUNS_DIR),
    name=RUN_NAME,
)
print(f"Listo. Pesos en {RUNS_DIR / RUN_NAME / 'weights'}")
