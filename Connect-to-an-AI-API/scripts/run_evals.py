import json
import sys
from pathlib import Path

import httpx


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CASES_PATH = PROJECT_ROOT / "evals" / "cases.json"
ENDPOINT_URL = "http://127.0.0.1:8000/triage"


def main() -> int:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    passed = 0
    failures = []

    with httpx.Client(timeout=35.0) as client:
        for case in cases:
            try:
                response = client.post(
                    ENDPOINT_URL,
                    json={"text": case["input"]},
                )
                response.raise_for_status()
                actual = response.json()

                expected = case["expected"]
                matched = (
                    actual.get("category") == expected["category"]
                    and actual.get("urgency") == expected["urgency"]
                )

                if matched:
                    passed += 1
                    print(f"PASS  {case['id']}")
                else:
                    failures.append(
                        {
                            "id": case["id"],
                            "expected": expected,
                            "actual": {
                                "category": actual.get("category"),
                                "urgency": actual.get("urgency"),
                            },
                        }
                    )
                    print(f"FAIL  {case['id']}")

            except httpx.HTTPError as error:
                failures.append(
                    {
                        "id": case["id"],
                        "expected": case["expected"],
                        "actual": None,
                        "error": str(error),
                    }
                )
                print(f"ERROR {case['id']}: {error}")

    total = len(cases)
    percentage = (passed / total) * 100

    print()
    print(f"Score: {passed}/{total} ({percentage:.1f}%)")

    if failures:
        print("\nFailures:")
        for failure in failures:
            print(json.dumps(failure, indent=2))

    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())