# Entrenamiento

Todo lo necesario para preparar datasets y entrenar los modelos. El backend no
depende de esta carpeta: solo usa los pesos copiados en `models/`.

```
training/
├── data/
│   ├── raw/          # datasets originales de Kaggle
│   └── processed/    # datasets en formato YOLO (parts, damages, damages_3cls)
├── scripts/          # preparar datasets y entrenar en la PC
├── colab/            # entrenar en Google Colab (GPU)
├── runs/             # resultados de cada entrenamiento
└── notes/            # logs y notas
```

Dataset: [Car parts and car damages (Kaggle)](https://www.kaggle.com/datasets/humansintheloop/car-parts-and-car-damages).
Ojo: los nombres de carpeta están cruzados. "Car damages dataset" trae las anotaciones de
piezas y "Car parts dataset" las de daños.

## Pasos

Desde la carpeta CarFix:

```powershell
# Piezas
python training/scripts/prepare_parts_dataset.py
python training/scripts/train_parts.py

# Daños
python training/scripts/prepare_damage_dataset.py   # 8 clases
python training/scripts/remap_damage_3cls.py        # 8 -> 3 clases
# Entrenar en Colab con training/colab/train_damage_3cls_colab.py
```

Al terminar, copiar el `best.pt` elegido a `models/` (ver `models/README.md`).

## Historial

| Run | Modelo | Datos | Máscara mAP50 | Notas |
|-----|--------|-------|---------------|-------|
| automotive_parts_v1  | yolo11n-seg, 640, CPU | piezas, 21 clases | 0,88 (val) | En uso |
| automotive_damage_v1 | yolo11n-seg, 640, Colab | daños, 8 clases | 0,10 (val) | |
| automotive_damage_v2 | yolo11s-seg, 1024, Colab | daños, 8 clases | 0,10 (test) | El modelo más grande no ayudó |
| automotive_damage_v3 | yolo11n-seg, 1024, Colab | daños, 3 clases | 0,145 (test) | En uso. Rotura 0,28 · Golpe 0,08 · Pintura 0,08 |

Lo que más limita al modelo de daños es la cantidad de datos (569 imágenes de entrenamiento).
