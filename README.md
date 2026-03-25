# Python Analytics Runtime Template

A production-leaning template for a **generic Python service** that exposes both:

- **REST** (FastAPI)
- **gRPC** (grpc.aio)

Both transports call the same shared executor using this contract:

- `Execute(operation_name, payload_json)`

This keeps business execution transport-agnostic, easy to test, and easy to extend.

## Project structure

```text
myapp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── rest_api.py
│   ├── grpc_server.py
│   ├── executor.py
│   ├── operation_registry.py
│   ├── models.py
│   ├── config.py
│   ├── db.py
│   └── operations/
│       ├── __init__.py
│       └── example_operation.py
├── proto/
│   └── analytics_runtime.proto
├── .vscode/
│   └── launch.json
├── requirements.txt
├── README.md
├── test-grpc.ps1
├── test-rest.ps1
└── .gitignore
```

## What the template provides

- `POST /execute`, `GET /health`, `GET /operations` over REST
- `analytics.runtime.AnalyticsRuntime/Execute` over gRPC
- Shared execution layer (`app/executor.py`) for both transports
- Decorator-based operation registry (`app/operation_registry.py`)
- Generic example operation (`ExampleOperation`) with optional DB connectivity check
- Azure SQL helper with `DefaultAzureCredential` and token-based `pyodbc` auth
- gRPC reflection enabled for `grpcurl` without providing local proto files

## Setup (Windows PowerShell)

### 1) Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Generate gRPC Python bindings (into project root)

```powershell
python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/analytics_runtime.proto
```

This generates:

- `analytics_runtime_pb2.py`
- `analytics_runtime_pb2_grpc.py`

> The template intentionally imports these from project root for Windows-friendly local module behavior.

### 4) Run the app

```powershell
python -m app.main
```

Servers start concurrently:

- REST on `0.0.0.0:8000`
- gRPC on `0.0.0.0:50051`

## Docker (production-ready baseline)

This repo includes a `Dockerfile` that:

- installs OS dependencies and ODBC Driver 18 for SQL Server (`pyodbc` support)
- installs Python dependencies from `requirements.txt`
- generates gRPC bindings during image build
- runs as a non-root user
- exposes REST (`8000`) and gRPC (`50051`)
- includes a container healthcheck against `/health`

### Build image

```powershell
docker build -t analytics-runtime-template:latest .
```

### Run container (example)

```powershell
docker run --rm -p 8000:8000 -p 50051:50051 \
  -e SQL_CONNECTION_STRING="Driver={ODBC Driver 18 for SQL Server};Server=tcp:host,1433;Database=mydb;UID=user;PWD=pass;Encrypt=yes;TrustServerCertificate=no;" \
  analytics-runtime-template:latest
```

> Use your own auth settings as appropriate. If `SQL_CONNECTION_STRING` is not set, the service falls back to Azure AD token auth.

## AKS deployment manifests (Deployment + Service)

The repo includes Kubernetes manifests under `k8s/`:

- `k8s/deployment.yaml`
- `k8s/service.yaml`
- `k8s/serviceaccount.yaml` (for AKS Workload Identity scenarios)

### What they do

- Deploy 2 replicas of the runtime container
- Expose REST on port `80` -> container `8000`
- Expose gRPC on port `50051` -> container `50051`
- Add readiness/liveness probes on `/health`
- Read DB/Auth settings from a secret named `analytics-runtime-secrets`

### Apply manifests

```powershell
kubectl apply -f k8s/serviceaccount.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### Example secret creation

```powershell
kubectl create secret generic analytics-runtime-secrets \
  --from-literal=sql-connection-string="Driver={ODBC Driver 18 for SQL Server};Server=tcp:host,1433;Database=mydb;UID=user;PWD=pass;Encrypt=yes;TrustServerCertificate=no;" \
  --from-literal=sql-server="your-server.database.windows.net" \
  --from-literal=sql-database="your-database" \
  --from-literal=azure-client-id="<optional-user-assigned-managed-identity-client-id>"
```

> Set `image:` in `k8s/deployment.yaml` to your pushed image (for example, ACR).

## REST quick tests

### Manual examples

```powershell
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/health"
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/operations"

$body = @{
  operation_name = "ExampleOperation"
  payload_json = '{"message":"hello"}'
  correlation_id = "manual-rest"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://localhost:8000/execute" -ContentType "application/json" -Body $body
```

### Scripted

```powershell
./test-rest.ps1
```

## gRPC quick tests

### Install grpcurl on Windows

Option A (Winget):

```powershell
winget install fullstorydev.grpcurl
```

Option B (Chocolatey):

```powershell
choco install grpcurl
```

Option C (manual): download a release binary from:

- https://github.com/fullstorydev/grpcurl/releases

### Why grpcurl accepts JSON if gRPC is binary

gRPC uses Protobuf binary messages on the wire. `grpcurl` is a client helper that maps your JSON input to the Protobuf request type, serializes it to binary, sends it over gRPC, then converts the binary response back to JSON for display.

### Manual example (PowerShell-safe stdin pattern)

```powershell
$body = '{"operation_name":"ExampleOperation","payload_json":"{}"}'
$body | Out-String | grpcurl -plaintext -d '@' localhost:50051 analytics.runtime.AnalyticsRuntime/Execute
```

### Scripted

```powershell
./test-grpc.ps1
```

## Azure SQL + managed identity notes

Environment variables supported:

- `SQL_CONNECTION_STRING` (optional, if set it is used directly)
- `SQL_SERVER` (required for DB use)
- `SQL_DATABASE` (required for DB use)
- `SQL_PORT` (optional, default `1433`)
- `AZURE_CLIENT_ID` (optional, used for user-assigned managed identity)

`app/db.py` uses:

- `DefaultAzureCredential`
- scope: `https://database.windows.net/.default`
- `pyodbc` token auth via `attrs_before` with `SQL_COPT_SS_ACCESS_TOKEN = 1256`

Local development behavior:

- On local machines, `DefaultAzureCredential` usually resolves to **developer credentials** (Azure CLI, VS Code, shared token cache, etc.), not managed identity.
- In Azure-hosted environments, the same code path can use **managed identity**.
- Set `AZURE_CLIENT_ID` to target a **user-assigned managed identity**.

Connection mode behavior:

- If `SQL_CONNECTION_STRING` is set, `app/db.py` uses it directly with `pyodbc.connect(...)`.
- If `SQL_CONNECTION_STRING` is not set, the template uses Azure AD token auth with `DefaultAzureCredential`.

## VS Code debugging

Use the included launch profile in `.vscode/launch.json`:

- module: `app.main`
- integrated terminal
- workspace cwd
- `justMyCode: true`
- `subProcess: true`

## Notes for extension

- Add new operations using `@register_operation("OperationName")`
- Keep handlers returning `dict`
- Keep transport layers thin and route through `app/executor.py`
- Keep payload contract generic to avoid transport/domain lock-in
