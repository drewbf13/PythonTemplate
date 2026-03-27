from __future__ import annotations

import json

from analytics_runtime.errors import (
    DuplicateOperationError,
    HandlerExecutionError,
    MalformedPayloadError,
    UnknownOperationError,
)
from analytics_runtime.types import ExecutionContext, OperationHandler, PluginRegistration


class OperationDispatcher:
    def __init__(self) -> None:
        self._operations: dict[str, OperationHandler] = {}

    def register_plugin(self, plugin: PluginRegistration) -> None:
        for operation_name, handler in plugin.operations.items():
            if operation_name in self._operations:
                raise DuplicateOperationError(
                    f"Duplicate operation registration '{operation_name}' from plugin '{plugin.name}'."
                )
            self._operations[operation_name] = handler

    def list_operations(self) -> list[str]:
        return sorted(self._operations.keys())

    def execute(self, operation_name: str, payload_json: str, correlation_id: str | None = None) -> str:
        handler = self._operations.get(operation_name)
        if handler is None:
            raise UnknownOperationError(f"Unknown operation: {operation_name}")

        try:
            payload = json.loads(payload_json)
        except json.JSONDecodeError as exc:
            raise MalformedPayloadError("Invalid payload_json. Expected valid JSON object string.") from exc

        if not isinstance(payload, dict):
            raise MalformedPayloadError("Invalid payload_json. Expected a JSON object.")

        try:
            result = handler(payload, ExecutionContext(correlation_id=correlation_id))
        except Exception as exc:  # noqa: BLE001
            raise HandlerExecutionError(f"Operation '{operation_name}' failed: {exc}") from exc

        if not isinstance(result, dict):
            raise HandlerExecutionError(
                f"Operation '{operation_name}' must return a dict, got {type(result).__name__}."
            )

        return json.dumps(result)
