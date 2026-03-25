from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ExecuteRequestModel(BaseModel):
    operation_name: str = Field(..., min_length=1)
    payload_json: str
    correlation_id: str | None = None


class ExecuteResponseModel(BaseModel):
    result_json: str


class HealthResponseModel(BaseModel):
    status: str = "ok"


class OperationsResponseModel(BaseModel):
    operations: list[str]


OperationResult = dict[str, Any]
