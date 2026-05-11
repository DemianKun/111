@echo off
title KitchenOS - Sistema de Arranque Principal
color 0E

echo ===================================================
echo     Iniciando Ecosistema KitchenOS (K-OS) ...
echo     Ruta raiz: C:\KitchenOS
echo ===================================================
echo.

:: 1. Iniciar el Backend (Base de datos y API)
echo [1/4] Levantando Backend (FastAPI)...
start "K-OS Backend" cmd /k "cd /d C:\KitchenOS\backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"

:: MODIFICACIÓN: 6 segundos de espera para evitar el error WinError 10061
timeout /t 6 /nobreak >nul

:: 2. Iniciar el Bot de WhatsApp (Node.js)
echo [2/4] Despertando Bot Maestro (WhatsApp)...
start "K-OS Bot Maestro" cmd /k "cd /d C:\KitchenOS\bot_maestro && node bot_maestro.js"
timeout /t 3 /nobreak >nul

:: 3. Iniciar el Cerebro (IA Autónoma)
echo [3/4] Activando Agente de Inteligencia Artificial...
start "K-OS IA Autonoma" cmd /k "cd /d C:\KitchenOS\ia && python ia_asignador.py"
timeout /t 2 /nobreak >nul

:: 4. Servir el Frontend para evitar problemas de CORS
echo [4/4] Sirviendo Interfaz Web...
start "K-OS Frontend" cmd /k "cd /d C:\KitchenOS\Frontend && python -m http.server 8080"
timeout /t 2 /nobreak >nul

echo.
echo ===================================================
echo  TODO ACTIVO. Abriendo Centro de Mando...
echo ===================================================

:: Abre la ruta del dashboard en tu navegador predeterminado
start http://localhost:8080/chef_panel.html

echo.
echo Puedes minimizar esta ventana azul.
echo PRECAUCION: Para apagar el sistema, cierra las 4 ventanas negras que se abrieron.
pause