# Launch script for Marketing A/B Test Dashboard
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

$env:USERPROFILE = $scriptDir

Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host " Launching Marketing A/B Testing Dashboard (ZoomCharts Style)" -ForegroundColor White
Write-Host "=========================================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".venv\Scripts\streamlit.exe") {
    & ".venv\Scripts\streamlit.exe" run app.py
} else {
    Write-Host "Virtual environment not detected. Running with system streamlit..." -ForegroundColor Yellow
    streamlit run app.py
}

