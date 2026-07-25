"""Reference implementation of the flake-rate / quarantine analyzer.

See problem.md in this directory for the full contract.
"""
from typing import Dict, List


def analyze_flake_rates(run_history: Dict[str, List[bool]], threshold: float) -> Dict[str, dict]:
    if not (0.0 <= threshold <= 1.0):
        raise ValueError("threshold must be within [0.0, 1.0]")

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
        elif pass_count == 0:
            # Consistently failing every run: a real (deterministic) bug,
            # not flakiness. Must never be recommended for quarantine.
            classification = "broken"
            flake_rate = 0.0
            quarantine = False
        else:
            classification = "flaky"
            flake_rate = fail_count / total_runs
            quarantine = flake_rate >= threshold  # inclusive boundary

        report[test_name] = {
            "total_runs": total_runs,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "flake_rate": flake_rate,
            "classification": classification,
            "quarantine": quarantine,
        }

    return report
