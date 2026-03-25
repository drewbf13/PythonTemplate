from __future__ import annotations

import json

from app.operation_registry import get_operation


class OperationExecutionError(Exception):
    """Raised when a registered operation cannot be executed successfully."""


async def execute(operation_name: str, payload_json: str, correlation_id: str | None = None) -> str:
    handler = get_operation(operation_name)
    if handler is None:
        raise OperationExecutionError(f"Unknown operation: {operation_name}")

    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as exc:
        raise OperationExecutionError("Invalid payload_json. Expected a valid JSON object string.") from exc

    if not isinstance(payload, dict):
        raise OperationExecutionError("Invalid payload_json. Expected a JSON object.")

    try:
        result = handler(payload, correlation_id)
    except Exception as exc:  # noqa: BLE001
        raise OperationExecutionError(f"Operation '{operation_name}' failed: {exc}") from exc

    if not isinstance(result, dict):
        raise OperationExecutionError(
            f"Operation '{operation_name}' must return a dict, got {type(result).__name__}."
        )

    return json.dumps(result)
