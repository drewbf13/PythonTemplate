from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from analytics_runtime.decorators import OPERATION_ATTR, STARTUP_ATTR
from analytics_runtime.types import OperationHandler, PluginRegistration, StartupHook


class PluginBuilder:
    def __init__(self, name: str) -> None:
        self.name = name

    def build(self, namespace: Mapping[str, Any]) -> PluginRegistration:
        operations: dict[str, OperationHandler] = {}
        startup_hooks: list[StartupHook] = []

        for value in namespace.values():
            op_name = getattr(value, OPERATION_ATTR, None)
            if op_name:
                operations[op_name] = value
            if getattr(value, STARTUP_ATTR, False):
                startup_hooks.append(value)

        return PluginRegistration(
            name=self.name,
            operations=operations,
            startup_hooks=startup_hooks,
        )
