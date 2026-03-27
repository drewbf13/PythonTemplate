from __future__ import annotations

import logging

from analytics_runtime.discovery import discover_plugins
from analytics_runtime.dispatcher import OperationDispatcher
from analytics_runtime.errors import StartupHookError
from analytics_runtime.types import PluginRegistration

logger = logging.getLogger(__name__)


class AnalyticsHost:
    def __init__(self) -> None:
        self.dispatcher = OperationDispatcher()
        self.plugins: list[PluginRegistration] = []
        self._initialized = False

    def load_plugins(self) -> None:
        self.plugins = discover_plugins()
        for plugin in self.plugins:
            self.dispatcher.register_plugin(plugin)
            logger.info(
                "Registered plugin '%s' with operations=%s startup_hooks=%s",
                plugin.name,
                sorted(plugin.operations.keys()),
                len(plugin.startup_hooks),
            )

    def initialize(self) -> None:
        if self._initialized:
            return

        for plugin in self.plugins:
            for hook in plugin.startup_hooks:
                try:
                    hook()
                except Exception as exc:  # noqa: BLE001
                    raise StartupHookError(
                        f"Startup hook '{hook.__name__}' in plugin '{plugin.name}' failed: {exc}"
                    ) from exc

        self._initialized = True

    def list_operations(self) -> list[str]:
        return self.dispatcher.list_operations()

    def execute(self, operation_name: str, payload_json: str, correlation_id: str | None = None) -> str:
        return self.dispatcher.execute(operation_name, payload_json, correlation_id)
