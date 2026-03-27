from __future__ import annotations


class AnalyticsRuntimeError(Exception):
    """Base exception for runtime host failures."""


class UnknownOperationError(AnalyticsRuntimeError):
    pass


class DuplicateOperationError(AnalyticsRuntimeError):
    pass


class StartupHookError(AnalyticsRuntimeError):
    pass


class MalformedPayloadError(AnalyticsRuntimeError):
    pass


class HandlerExecutionError(AnalyticsRuntimeError):
    pass
