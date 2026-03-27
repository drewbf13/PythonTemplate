from __future__ import annotations

from analytics_runtime.errors import AnalyticsRuntimeError
from app.runtime_service import initialize_host


class OperationExecutionError(Exception):
    """Raised when a registered operation cannot be executed successfully."""


async def execute(operation_name: str, payload_json: str, correlation_id: str | None = None) -> str:
    host = initialize_host()

    try:
        return host.execute(operation_name, payload_json, correlation_id)
    except AnalyticsRuntimeError as exc:
        raise OperationExecutionError(str(exc)) from exc
