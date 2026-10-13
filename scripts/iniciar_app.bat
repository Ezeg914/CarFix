@echo off
rem Instala y abre la app en el celular conectado por USB.
rem Con "adb reverse" el celular llega a la API de la PC como localhost:8000,
rem sin depender del Wi-Fi ni del firewall.
cd /d "%~dp0..\mobile"
title CarFix - App
set "ADB=adb"
where adb >nul 2>nul || set "ADB=%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"
"%ADB%" reverse tcp:8000 tcp:8000
if errorlevel 1 (
  echo No se pudo conectar con el celular. Revisa el cable y que la depuracion USB este activada.
  pause
  exit /b 1
)
call flutter pub get
call flutter run --dart-define=API_URL=http://localhost:8000
pause
