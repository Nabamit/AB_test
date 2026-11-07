@echo off
title Marketing AB Testing - ZoomCharts Dashboard
cd /d "%~dp0"

echo =========================================================
echo  Launching Marketing A/B Testing Dashboard (ZoomCharts Style)
echo =========================================================
echo.

if exist .venv\Scripts\streamlit.exe (
    set "USERPROFILE=%~dp0"
    .venv\Scripts\streamlit.exe run app.py
) else (
    echo Virtual environment not found. Using system python...
    streamlit run app.py
)

pause

