$ErrorActionPreference = "Stop"

$apiKey = $env:API_KEY
if ([string]::IsNullOrWhiteSpace($apiKey)) {
  $apiKey = "dev-api-key"
}

$body = '{"operation_name":"ExampleOperation","payload_json":"{}","correlation_id":"grpc-local-test"}'

$body |
  Out-String |
  grpcurl -plaintext -H "x-api-key: $apiKey" -d '@' localhost:50051 analytics.runtime.AnalyticsRuntime/Execute
