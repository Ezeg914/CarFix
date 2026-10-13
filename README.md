# CarFix

![tests](https://github.com/Ezeg914/CarFix/actions/workflows/tests.yml/badge.svg)

Detecta daños en un vehículo a partir de una foto y arma un presupuesto de reparación:
qué piezas cambiar, cuáles reparar y cuáles pintar. Tiene una API en FastAPI y una app
mobile en Flutter.

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
│   │   ├── api.py           # API HTTP (FastAPI) que usa la app
│   │   └── cli.py           # uso por consola
│   ├── data/reglas_presupuesto.csv
│   ├── tests/
│   └── requirements.txt
├── mobile/                  # app Flutter (ver mobile/README.md)
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
```

**API** (la que usa la app):

```powershell
uvicorn carfix.api:app --host 0.0.0.0 --port 8000
```

- `POST /analizar` recibe `foto`, `marca`, `modelo` y `anio` (multipart). Devuelve
  `presupuesto` (JSON) e `imagen` (JPEG en base64, con piezas y daños marcados).
- `GET /salud` sirve para chequear que esté arriba.
- Documentación interactiva: http://localhost:8000/docs

**Consola:**

```powershell
python -m carfix ..\samples\vento_2012.jpg --marca Volkswagen --modelo Vento --anio 2012
```

**App:** ver [mobile/README.md](mobile/README.md).

Tests:

```powershell
cd backend
python -m pytest
cd ..\mobile
flutter test
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
- [x] API (FastAPI)
- [x] App mobile (Flutter)
- [ ] Precios de repuestos por marca/modelo/año
