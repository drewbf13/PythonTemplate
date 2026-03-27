from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


OPERATION_ATTR = "_analytics_operation_name"
STARTUP_ATTR = "_analytics_startup_hook"


def operation(name: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        setattr(func, OPERATION_ATTR, name)
        return func

    return decorator


def startup(func: F) -> F:
    setattr(func, STARTUP_ATTR, True)
    return func
