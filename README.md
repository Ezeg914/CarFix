# CarFix

![tests](https://github.com/Ezeg914/CarFix/actions/workflows/tests.yml/badge.svg)

Detecta daños en un vehículo a partir de una foto y arma un presupuesto de reparación:
qué piezas cambiar, cuáles reparar y cuáles pintar.

1. Un modelo general (COCO) encuentra el vehículo y recorta la foto a su alrededor.
2. El modelo de **piezas** (YOLO11n-seg, 21 clases) segmenta capot, paragolpes, ópticas, etc.
3. El modelo de **daños** (YOLO11n-seg, 3 clases: Rotura, Golpe, Pintura) segmenta los daños.
4. Cada daño se asigna a la pieza sobre la que cae y se calcula qué parte de la pieza cubre.
5. Una tabla de reglas decide cambiar / reparar / pintar y suma los precios.

## Estructura

```
CarFix/
├── backend/                 # código de la app
│   ├── carfix/              # paquete Python
│   │   ├── config.py        # rutas y umbrales (todo lo ajustable)
│   │   ├── detection.py     # modelos: vehículo, piezas y daños
│   │   ├── assignment.py    # cruce de daños con piezas
│   │   ├── rules.py         # carga de la tabla de reglas y precios
│   │   ├── budget.py        # decisión por pieza y presupuesto
│   │   ├── pipeline.py      # flujo completo (Analyzer)
│   │   ├── video.py         # modo video (experimental)
│   │   ├── imaging.py       # leer imágenes y dibujar resultados
│   │   └── cli.py           # uso por consola
│   ├── data/reglas_presupuesto.csv
│   ├── tests/
│   └── requirements.txt
├── models/                  # pesos que usa el backend (parts.pt, damage.pt, vehicle.pt)
├── samples/                 # fotos de prueba
├── outputs/                 # presupuestos generados (json + imagen)
└── training/                # todo lo de entrenamiento (ver training/README.md)
```

## Uso

```powershell
git clone https://github.com/Ezeg914/CarFix.git
cd CarFix/backend
pip install -r requirements.txt
python -m carfix ..\samples\vento_2012.jpg --marca Volkswagen --modelo Vento --anio 2012
```

Tests:

```powershell
cd backend
python -m pytest
```

Los modelos entrenados ya vienen en `models/`. Los datasets no se suben al repo porque
pesan mucho; para reentrenar hay que bajarlos de Kaggle (ver `training/README.md`).

## Ajustes

- **Reglas y precios por pieza:** `backend/data/reglas_presupuesto.csv`.
- **Umbrales de detección:** `backend/carfix/config.py`.
- **Cambiar de modelo:** reemplazar el archivo en `models/` (ver `models/README.md`).

## Estado

- [x] Modelo de piezas
- [x] Modelo de daños (3 clases; Golpe y Pintura todavía flojos)
- [x] Cruce piezas/daños y presupuesto por reglas
- [ ] API (FastAPI)
- [ ] Frontend
- [ ] Precios de repuestos por marca/modelo/año
