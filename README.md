# Python Analytics Runtime Template (Plugin Host)

This template is now a **plugin-based analytics runtime host**.

## Architecture at a glance

- Host service exposes REST + gRPC transport.
- Host discovers installed analytics plugins from Python entry points (`analytics.plugins`).
- Plugins publish:
  - operations (`operation_name -> handler`)
  - startup hooks (run before serving)
- Runtime dispatch contract:
  - `Execute(operation_name, payload_json, correlation_id)`

Analytics teams should build plugins; they should not modify host internals.

## Repository layout

```text
app/
  main.py                # starts host + REST + gRPC
  runtime_service.py     # singleton AnalyticsHost bootstrap
  executor.py            # Execute wrapper used by REST/gRPC transports
analytics_runtime/
  __init__.py
  types.py               # PluginRegistration + ExecutionContext
  decorators.py          # @operation, @startup
  builder.py             # PluginBuilder
  discovery.py           # entry point discovery (analytics.plugins)
  dispatcher.py          # operation dispatch + JSON handling
  host.py                # plugin loading + startup hook execution
plugins/
  trade_example_plugin/  # example plugin package with entry point
scripts/
  setup-dev.ps1
  run-local.ps1
  test-plugin-runtime.ps1
  invoke_runtime.py
```

## How plugin discovery works

`analytics_runtime.discovery.discover_plugins()` calls `importlib.metadata.entry_points(group="analytics.plugins")`.

Each entry point is expected to resolve to a callable factory (typically `get_plugin`) that returns `PluginRegistration`.

## Plugin contract

```python
@dataclass
class PluginRegistration:
    name: str
    operations: dict[str, OperationHandler]
    startup_hooks: list[StartupHook]
```

Context passed to handlers:

```python
@dataclass
class ExecutionContext:
    correlation_id: str | None
```

## Quick start for plugin authors

```python
from analytics_runtime import PluginBuilder, operation, startup

builder = PluginBuilder("my-plugin")

@startup
def init_models():
    print("ready")

@operation("EvaluateTradeScenario")
def evaluate_trade(payload: dict, context):
    return {"ok": True, "correlation_id": context.correlation_id}


def get_plugin():
    return builder.build(globals())
```

Then register in your plugin package `pyproject.toml`:

```toml
[project.entry-points."analytics.plugins"]
my_plugin = "my_plugin.plugin:get_plugin"
```

## Example plugin included

`plugins/trade_example_plugin` includes:

- one startup hook (`load_models`)
- two operations:
  - `EvaluateTradeScenario`
  - `PredictDraftPickOutcome`

## Runtime lifecycle

1. Host starts.
2. Discovers plugins via entry points.
3. Registers operations.
4. Runs startup hooks (fail-fast if any hook raises).
5. Begins serving REST + gRPC execute requests.

## Error handling

Runtime returns clear errors for:

- unknown operation
- duplicate operation registration
- startup hook failure
- malformed JSON payload
- handler exceptions

## Local development (Windows PowerShell)

### 1) Setup environment

```powershell
./scripts/setup-dev.ps1
```

This creates `.venv` (if missing), installs host package editable, installs example plugin editable, and installs pytest.

### 2) Run host

```powershell
./scripts/run-local.ps1
```

### 3) Test plugin discovery + dispatch

```powershell
./scripts/test-plugin-runtime.ps1
```

This calls `scripts/invoke_runtime.py`, which initializes the runtime and executes sample calls.

## Transport APIs

REST and gRPC still route through the same internal execution path (`app/executor.py`) and now use the plugin runtime under the hood.
