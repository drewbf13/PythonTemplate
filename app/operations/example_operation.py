from __future__ import annotations

from typing import Any

from app.db import AzureSqlClient
from app.operation_registry import register_operation


@register_operation("ExampleOperation")
def example_operation(payload: dict[str, Any], correlation_id: str | None) -> dict[str, Any]:
    db_ping_ok: bool | None = None
    db_ping_error: str | None = None

    try:
        db_ping_ok = AzureSqlClient().ping()
    except Exception as exc:  # noqa: BLE001
        db_ping_ok = False
        db_ping_error = str(exc)

    return {
        "template": True,
        "operation": "ExampleOperation",
        "received_payload": payload,
        "correlation_id": correlation_id,
        "db_ping_ok": db_ping_ok,
        "db_ping_error": db_ping_error,
    }
