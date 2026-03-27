from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    correlation_id: str | None = None


OperationHandler = Callable[[dict[str, Any], ExecutionContext], dict[str, Any]]
StartupHook = Callable[[], None]


@dataclass(slots=True)
class PluginRegistration:
    name: str
    operations: dict[str, OperationHandler] = field(default_factory=dict)
    startup_hooks: list[StartupHook] = field(default_factory=list)
