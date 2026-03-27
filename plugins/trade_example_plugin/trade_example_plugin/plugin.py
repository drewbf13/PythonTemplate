from __future__ import annotations

from typing import Any

from analytics_runtime import PluginBuilder, operation, startup

builder = PluginBuilder("trade-example-plugin")
_PLUGIN_STATE = {"initialized": False}


@startup
def load_models() -> None:
    _PLUGIN_STATE["initialized"] = True
    print("[trade-example-plugin] startup complete: mock models loaded")


@operation("EvaluateTradeScenario")
def evaluate_trade_scenario(payload: dict[str, Any], context) -> dict[str, Any]:
    value_delta = float(payload.get("value_delta", 12.5))
    risk_factor = float(payload.get("risk_factor", 0.3))
    score = max(0.0, min(100.0, 70 + value_delta - (risk_factor * 20)))
    return {
        "operation": "EvaluateTradeScenario",
        "correlation_id": context.correlation_id,
        "plugin_initialized": _PLUGIN_STATE["initialized"],
        "score": round(score, 2),
        "confidence": 0.87,
        "explanation": "Positive surplus value." if score >= 65 else "Borderline scenario.",
    }


@operation("PredictDraftPickOutcome")
def predict_draft_pick_outcome(payload: dict[str, Any], context) -> dict[str, Any]:
    pick_number = int(payload.get("pick_number", 12))
    expected_value = max(1.0, 12.0 - (pick_number * 0.35))
    probability = max(0.05, 0.65 - (pick_number * 0.02))
    return {
        "operation": "PredictDraftPickOutcome",
        "correlation_id": context.correlation_id,
        "plugin_initialized": _PLUGIN_STATE["initialized"],
        "pick_number": pick_number,
        "probability": round(probability, 2),
        "expected_value": round(expected_value, 2),
    }


def get_plugin():
    return builder.build(globals())
