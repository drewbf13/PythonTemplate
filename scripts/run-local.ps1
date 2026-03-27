param(
  [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"
$python = Join-Path $VenvPath "Scripts/python.exe"

if (-not (Test-Path $python)) {
  throw "Virtual environment python not found. Run scripts/setup-dev.ps1 first."
}

Write-Host "Starting analytics runtime host (REST :8000, gRPC :50051)..."
& $python -m app.main
