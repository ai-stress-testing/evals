"""Deliberately-broken variant of the flake-rate / quarantine analyzer.

Bug (intentional): does not distinguish a "broken" test (100% failing,
`pass_count == 0`) from a genuinely "flaky" test. It only checks whether
`fail_count > 0`, so a consistently-failing test gets classified as
"flaky" with `flake_rate = 1.0` and, at any reasonable threshold, gets
`quarantine = True` — exactly the wrong outcome per problem.md rule 3
(a 100%-failing test must be reported as "broken", flake_rate 0.0, and
must never be quarantined).
"""
from typing import Dict, List


def analyze_flake_rates(run_history: Dict[str, List[bool]], threshold: float) -> Dict[str, dict]:
    report: Dict[str, dict] = {}

    for test_name, results in run_history.items():
        total_runs = len(results)
        pass_count = sum(1 for outcome in results if outcome)
        fail_count = total_runs - pass_count

        if total_runs == 0:
            classification = "insufficient_data"
            flake_rate = 0.0
            quarantine = False
        elif fail_count == 0:
            classification = "stable"
            flake_rate = 0.0
            quarantine = False
        else:
            # BUG: missing the `pass_count == 0` ("broken") branch. Any
            # test with at least one failure is lumped in as "flaky",
            # including a test that has never once passed.
            classification = "flaky"
            flake_rate = fail_count / total_runs
            quarantine = flake_rate >= threshold

        report[test_name] = {
            "total_runs": total_runs,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "flake_rate": flake_rate,
            "classification": classification,
            "quarantine": quarantine,
        }

    return report
