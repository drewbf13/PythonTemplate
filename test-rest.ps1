$ErrorActionPreference = "Stop"

$apiKey = $env:API_KEY
if ([string]::IsNullOrWhiteSpace($apiKey)) {
  $apiKey = "dev-api-key"
}
$headers = @{ "x-api-key" = $apiKey }

Write-Host "GET /health"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"

Write-Host "GET /operations"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/operations" -Headers $headers

Write-Host "POST /execute"
$body = @{
  operation_name = "ExampleOperation"
  payload_json = '{"message":"hello from rest"}'
  correlation_id = "rest-local-test"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/execute" -Headers $headers -ContentType "application/json" -Body $body
