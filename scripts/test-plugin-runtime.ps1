param(
  [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"
$python = Join-Path $VenvPath "Scripts/python.exe"

if (-not (Test-Path $python)) {
  throw "Virtual environment python not found. Run scripts/setup-dev.ps1 first."
}

Write-Host "Running plugin discovery + dispatch smoke test..."
& $python .\scripts\invoke_runtime.py
