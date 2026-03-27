from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.runtime_service import initialize_host


def main() -> None:
    host = initialize_host()

    print("Discovered operations:", host.list_operations())

    tests = [
        (
            "EvaluateTradeScenario",
            {"value_delta": 14.2, "risk_factor": 0.25},
            "ps-eval-001",
        ),
        (
            "PredictDraftPickOutcome",
            {"pick_number": 8},
            "ps-draft-001",
        ),
    ]

    for operation_name, payload, correlation_id in tests:
        result = host.execute(operation_name, json.dumps(payload), correlation_id)
        print(f"{operation_name} => {result}")


if __name__ == "__main__":
    main()
