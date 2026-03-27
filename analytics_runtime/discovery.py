from __future__ import annotations

import logging
from importlib.metadata import entry_points

from analytics_runtime.types import PluginRegistration

logger = logging.getLogger(__name__)

ENTRYPOINT_GROUP = "analytics.plugins"


def discover_plugins() -> list[PluginRegistration]:
    registrations: list[PluginRegistration] = []
    for ep in entry_points(group=ENTRYPOINT_GROUP):
        logger.info("Loading analytics plugin entry point: %s", ep.name)
        factory = ep.load()
        registration = factory()
        registrations.append(registration)

    return registrations
