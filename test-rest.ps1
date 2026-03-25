$ErrorActionPreference = "Stop"

Write-Host "GET /health"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"

Write-Host "GET /operations"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/operations"

Write-Host "POST /execute"
$body = @{
  operation_name = "ExampleOperation"
  payload_json = '{"message":"hello from rest"}'
  correlation_id = "rest-local-test"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/execute" -ContentType "application/json" -Body $body
