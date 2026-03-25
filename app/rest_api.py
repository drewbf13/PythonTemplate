from __future__ import annotations

from fastapi import FastAPI, HTTPException

from app.executor import OperationExecutionError, execute
from app.models import ExecuteRequestModel, ExecuteResponseModel, HealthResponseModel, OperationsResponseModel
from app.operation_registry import list_operations

app = FastAPI(title="Analytics Runtime Template", version="0.1.0")


@app.get("/health", response_model=HealthResponseModel)
async def health() -> HealthResponseModel:
    return HealthResponseModel()


@app.get("/operations", response_model=OperationsResponseModel)
async def operations() -> OperationsResponseModel:
    return OperationsResponseModel(operations=list_operations())


@app.post("/execute", response_model=ExecuteResponseModel)
async def execute_operation(request: ExecuteRequestModel) -> ExecuteResponseModel:
    try:
        result_json = await execute(request.operation_name, request.payload_json, request.correlation_id)
    except OperationExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ExecuteResponseModel(result_json=result_json)
