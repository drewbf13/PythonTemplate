from __future__ import annotations

from analytics_runtime.host import AnalyticsHost

_host: AnalyticsHost | None = None


def get_host() -> AnalyticsHost:
    global _host
    if _host is None:
        _host = AnalyticsHost()
        _host.load_plugins()
    return _host


def initialize_host() -> AnalyticsHost:
    host = get_host()
    host.initialize()
    return host
