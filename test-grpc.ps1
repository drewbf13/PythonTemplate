$ErrorActionPreference = "Stop"

$body = '{"operation_name":"ExampleOperation","payload_json":"{}","correlation_id":"grpc-local-test"}'

$body |
  Out-String |
  grpcurl -plaintext -d '@' localhost:50051 analytics.runtime.AnalyticsRuntime/Execute
