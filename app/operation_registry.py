from __future__ import annotations

from collections.abc import Callable
from typing import Any

OperationHandler = Callable[[dict[str, Any], str | None], dict[str, Any]]

_OPERATION_REGISTRY: dict[str, OperationHandler] = {}


def register_operation(name: str) -> Callable[[OperationHandler], OperationHandler]:
    """Decorator used to register an operation handler by name."""

    def decorator(func: OperationHandler) -> OperationHandler:
        _OPERATION_REGISTRY[name] = func
        return func

    return decorator


def get_operation(name: str) -> OperationHandler | None:
    return _OPERATION_REGISTRY.get(name)


def list_operations() -> list[str]:
    return sorted(_OPERATION_REGISTRY.keys())
