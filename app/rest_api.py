from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException

from app.auth import require_rest_api_key
from app.executor import OperationExecutionError, execute
from app.models import ExecuteRequestModel, ExecuteResponseModel, HealthResponseModel, OperationsResponseModel
from app.runtime_service import get_host

app = FastAPI(title="Analytics Runtime Template", version="0.2.0")


@app.get("/health", response_model=HealthResponseModel)
async def health() -> HealthResponseModel:
    return HealthResponseModel()


@app.get("/operations", response_model=OperationsResponseModel, dependencies=[Depends(require_rest_api_key)])
async def operations() -> OperationsResponseModel:
    return OperationsResponseModel(operations=get_host().list_operations())


@app.post("/execute", response_model=ExecuteResponseModel, dependencies=[Depends(require_rest_api_key)])
async def execute_operation(request: ExecuteRequestModel) -> ExecuteResponseModel:
    try:
        result_json = await execute(request.operation_name, request.payload_json, request.correlation_id)
    except OperationExecutionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return ExecuteResponseModel(result_json=result_json)
