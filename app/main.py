from __future__ import annotations

import asyncio
import logging

import uvicorn

from app.grpc_server import serve_grpc
from app.rest_api import app
from app.runtime_service import initialize_host


async def serve_rest(host: str = "0.0.0.0", port: int = 8000) -> None:
    config = uvicorn.Config(app=app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    initialize_host()
    await asyncio.gather(
        serve_rest(),
        serve_grpc(),
    )


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
