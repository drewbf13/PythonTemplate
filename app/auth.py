from __future__ import annotations

from fastapi import Header, HTTPException
import grpc

from app.config import get_settings

API_KEY_HEADER_NAME = "x-api-key"


def _is_api_key_valid(api_key: str | None) -> bool:
    configured_key = get_settings().api_key
    return bool(configured_key) and api_key == configured_key


async def require_rest_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not _is_api_key_valid(x_api_key):
        raise HTTPException(status_code=401, detail="Unauthorized")


class ApiKeyInterceptor(grpc.aio.ServerInterceptor):
    async def intercept_service(self, continuation, handler_call_details):
        metadata = handler_call_details.invocation_metadata or ()
        metadata_dict = {item.key.lower(): item.value for item in metadata}
        if not _is_api_key_valid(metadata_dict.get(API_KEY_HEADER_NAME)):
            async def abort_handler(request, context):
                await context.abort(grpc.StatusCode.UNAUTHENTICATED, "Unauthorized")

            return grpc.unary_unary_rpc_method_handler(abort_handler)

        return await continuation(handler_call_details)
