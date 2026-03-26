from __future__ import annotations

import grpc
from grpc_reflection.v1alpha import reflection

import analytics_runtime_pb2
import analytics_runtime_pb2_grpc
from app.auth import ApiKeyInterceptor
from app.executor import OperationExecutionError, execute


class AnalyticsRuntimeServicer(analytics_runtime_pb2_grpc.AnalyticsRuntimeServicer):
    async def Execute(
        self,
        request: analytics_runtime_pb2.ExecuteRequest,
        context: grpc.aio.ServicerContext,
    ) -> analytics_runtime_pb2.ExecuteResponse:
        try:
            result_json = await execute(request.operation_name, request.payload_json, request.correlation_id)
        except OperationExecutionError as exc:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(exc))

        return analytics_runtime_pb2.ExecuteResponse(result_json=result_json)


async def serve_grpc(host: str = "0.0.0.0", port: int = 50051) -> None:
    server = grpc.aio.server(interceptors=[ApiKeyInterceptor()])
    analytics_runtime_pb2_grpc.add_AnalyticsRuntimeServicer_to_server(AnalyticsRuntimeServicer(), server)

    service_names = (
        analytics_runtime_pb2.DESCRIPTOR.services_by_name["AnalyticsRuntime"].full_name,
        reflection.SERVICE_NAME,
    )
    reflection.enable_server_reflection(service_names, server)

    server.add_insecure_port(f"{host}:{port}")
    await server.start()
    await server.wait_for_termination()
