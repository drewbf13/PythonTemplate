from __future__ import annotations

import asyncio

import uvicorn

from app.grpc_server import serve_grpc
from app.rest_api import app
from app import operations as _operations  # noqa: F401


async def serve_rest(host: str = "0.0.0.0", port: int = 8000) -> None:
    config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    await asyncio.gather(
        serve_rest(),
        serve_grpc(),
    )


if __name__ == "__main__":
    asyncio.run(main())
