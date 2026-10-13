# CarFix mobile

App en Flutter: cargás marca, modelo y año, sacás o elegís una foto del auto y muestra
la foto con los daños marcados y el presupuesto. El análisis lo hace la API del backend.

```
lib/
├── main.dart
├── app.dart                       # tema y pantalla inicial
├── models/presupuesto.dart        # JSON de la API -> clases Dart
├── services/
│   ├── carfix_api.dart            # POST /analizar
│   └── ajustes.dart               # dirección de la API guardada en el teléfono
├── screens/
│   ├── nuevo_presupuesto_screen.dart   # datos del auto + foto
│   └── resultado_screen.dart           # imagen marcada + presupuesto
└── widgets/                       # tarjeta de pieza y formatos
```

## Probar

Atajo en Windows con el celular por USB: abrir `scripts\iniciar_api.bat` y después
`scripts\iniciar_app.bat`. La app queda apuntando a la API sola (usa `adb reverse`).

A mano:

1. Levantar la API en la PC (ver el README principal).
2. Conectar el celular por USB con la depuración USB activada, o abrir un emulador.
3. Desde esta carpeta:

```powershell
flutter pub get
flutter run
```

4. En la app, tocar el engranaje y poner la dirección de la API:
   - Emulador de Android: `http://10.0.2.2:8000` (ya viene así).
   - Celular real: `http://<IP de la PC>:8000`. La IP sale de `ipconfig` (IPv4), y el
     celular tiene que estar en la misma red Wi-Fi.

Tests: `flutter test`
