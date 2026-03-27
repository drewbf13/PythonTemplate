param(
  [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $VenvPath)) {
  python -m venv $VenvPath
}

$python = Join-Path $VenvPath "Scripts/python.exe"

& $python -m pip install --upgrade pip
& $python -m pip install -e .
& $python -m pip install -e .\plugins\trade_example_plugin
& $python -m pip install pytest

Write-Host "Setup complete. Activate with: .\\$VenvPath\\Scripts\\Activate.ps1"
