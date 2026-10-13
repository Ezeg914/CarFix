@echo off
rem Levanta la API del backend en el puerto 8000.
cd /d "%~dp0..\backend"
title CarFix - API
echo Instalando dependencias (solo la primera vez tarda)...
python -m pip install -q -r requirements.txt
echo.
echo API en http://localhost:8000  (documentacion: http://localhost:8000/docs)
echo Para cortarla: Ctrl+C
echo.
python -m uvicorn carfix.api:app --host 0.0.0.0 --port 8000
pause
