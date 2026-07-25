#!/usr/bin/env python3
"""Automated judge for the wcag-contrast-ratio benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, exercises it against a
fixed, deterministic set of test cases (canonical WCAG reference values --
no randomness, no wall-clock, no network), prints a pass/fail summary per
case, and exits 0 iff every case passes, non-zero otherwise.
"""
import importlib.util
import sys
import traceback

TOL = 1e-6


def close(a: float, b: float, tol: float = TOL) -> bool:
    return abs(a - b) <= tol


def load_module(path: str):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load spec for {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_cases(module):
    """Returns a list of (case_name, passed: bool, detail: str)."""
    results = []

    def record(name, passed, detail=""):
        results.append((name, passed, detail))

    relative_luminance = getattr(module, "relative_luminance", None)
    contrast_ratio = getattr(module, "contrast_ratio", None)
    wcag_verdict = getattr(module, "wcag_verdict", None)

    if relative_luminance is None or contrast_ratio is None or wcag_verdict is None:
        record(
            "required names present",
            False,
            "module must define relative_luminance, contrast_ratio, and wcag_verdict",
        )
        return results
    record("required names present", True)

    # --- Case 1: pure black vs white -> exactly 21.0, order-independent ---
    try:
        r1 = contrast_ratio("#000000", "#FFFFFF")
        r2 = contrast_ratio("#FFFFFF", "#000000")
        ok = close(r1, 21.0) and close(r2, 21.0)
        record(
            "case1_black_on_white_is_21to1",
            ok,
            f"contrast('#000000','#FFFFFF')={r1!r} contrast('#FFFFFF','#000000')={r2!r} "
            "(expected both == 21.0)",
        )
    except Exception:
        record("case1_black_on_white_is_21to1", False, "raised: " + traceback.format_exc(limit=1))

    # --- Case 2: identical colors -> exactly 1.0 ---
    try:
        r = contrast_ratio("#336699", "#336699")
        ok = close(r, 1.0)
        record(
            "case2_identical_colors_is_1to1",
            ok,
            f"contrast('#336699','#336699')={r!r} (expected == 1.0)",
        )
    except Exception:
        record("case2_identical_colors_is_1to1", False, "raised: " + traceback.format_exc(limit=1))

    # --- Case 3: hex normalization (with/without '#', case-insensitive) ---
    try:
        r_hash_upper = contrast_ratio("#767676", "#FFFFFF")
        r_hash_lower = contrast_ratio("#767676", "#ffffff")
        r_nohash = contrast_ratio("767676", "FFFFFF")
        ok = close(r_hash_upper, r_hash_lower) and close(r_hash_upper, r_nohash)
        record(
            "case3_hex_format_normalization",
            ok,
            f"with#/upper={r_hash_upper!r} with#/lower={r_hash_lower!r} no#={r_nohash!r} "
            "(expected all equal)",
        )
    except Exception:
        record("case3_hex_format_normalization", False, "raised: " + traceback.format_exc(limit=1))

    # --- Case 4: known reference value -- WCAG's own #767676-on-white example ---
    try:
        r = contrast_ratio("#767676", "#FFFFFF")
        expected = 4.542224959605253
        ok = close(r, expected, tol=1e-4)
        record(
            "case4_known_gray_on_white_reference_value",
            ok,
            f"contrast('#767676','#FFFFFF')={r!r} (expected ~= {expected!r})",
        )
    except Exception:
        record(
            "case4_known_gray_on_white_reference_value",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 5: known reference value -- pure red on white ---
    try:
        r = contrast_ratio("#FF0000", "#FFFFFF")
        expected = 3.9984767707539985
        ok = close(r, expected, tol=1e-4)
        record(
            "case5_known_red_on_white_reference_value",
            ok,
            f"contrast('#FF0000','#FFFFFF')={r!r} (expected ~= {expected!r})",
        )
    except Exception:
        record(
            "case5_known_red_on_white_reference_value",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 6: known reference value -- arbitrary non-gray pair (catches
    #     channel-weight-swap and other per-channel bugs that grayscale /
    #     extreme cases can't surface) ---
    try:
        r = contrast_ratio("#123456", "#ABCDEF")
        expected = 7.697307588979985
        ok = close(r, expected, tol=1e-4)
        record(
            "case6_known_arbitrary_pair_reference_value",
            ok,
            f"contrast('#123456','#ABCDEF')={r!r} (expected ~= {expected!r})",
        )
    except Exception:
        record(
            "case6_known_arbitrary_pair_reference_value",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 7: wcag_verdict shape + AA/AAA pass/fail, normal text ---
    try:
        v = wcag_verdict("#767676", "#FFFFFF", large_text=False)
        ok = (
            isinstance(v, dict)
            and set(v.keys()) >= {"ratio", "aa_pass", "aaa_pass"}
            and close(v["ratio"], 4.542224959605253, tol=1e-4)
            and v["aa_pass"] is True
            and v["aaa_pass"] is False
        )
        record(
            "case7_verdict_gray_on_white_normal_text",
            ok,
            f"verdict={v!r} (expected ratio~=4.542, aa_pass=True, aaa_pass=False)",
        )
    except Exception:
        record(
            "case7_verdict_gray_on_white_normal_text",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 8: wcag_verdict, large text lowers thresholds ---
    try:
        v = wcag_verdict("#FF0000", "#FFFFFF", large_text=True)
        ok = (
            isinstance(v, dict)
            and close(v["ratio"], 3.9984767707539985, tol=1e-4)
            and v["aa_pass"] is True  # 3.998 >= 3.0 (large-text AA threshold)
            and v["aaa_pass"] is False  # 3.998 < 4.5 (large-text AAA threshold)
        )
        record(
            "case8_verdict_red_on_white_large_text",
            ok,
            f"verdict={v!r} (expected ratio~=3.998, aa_pass=True, aaa_pass=False)",
        )
    except Exception:
        record(
            "case8_verdict_red_on_white_large_text",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 9: wcag_verdict, same pair fails AA at normal-text thresholds ---
    try:
        v = wcag_verdict("#FF0000", "#FFFFFF", large_text=False)
        ok = v["aa_pass"] is False and v["aaa_pass"] is False
        record(
            "case9_verdict_red_on_white_normal_text_fails_aa",
            ok,
            f"verdict={v!r} (expected aa_pass=False, aaa_pass=False for normal text)",
        )
    except Exception:
        record(
            "case9_verdict_red_on_white_normal_text_fails_aa",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    # --- Case 10: invalid hex strings raise ValueError, not silent wrong values ---
    try:
        bad_inputs = ["abc", "#12345", "1234567", "GGGGGG", "#ZZZZZZ", ""]
        all_raised = True
        offending = None
        for bad in bad_inputs:
            try:
                relative_luminance(bad)
                all_raised = False
                offending = bad
                break
            except ValueError:
                continue
            except Exception:
                all_raised = False
                offending = bad
                break
        record(
            "case10_invalid_hex_raises_valueerror",
            all_raised,
            "all invalid inputs raised ValueError"
            if all_raised
            else f"input {offending!r} did not raise ValueError as expected",
        )
    except Exception:
        record(
            "case10_invalid_hex_raises_valueerror",
            False,
            "raised: " + traceback.format_exc(limit=1),
        )

    return results


def main():
    if len(sys.argv) != 2:
        print(f"usage: python3 {sys.argv[0]} <path-to-solution.py>")
        sys.exit(1)

    path = sys.argv[1]

    try:
        module = load_module(path)
    except Exception:
        print(f"FAIL: could not import module at {path!r}")
        print(traceback.format_exc())
        sys.exit(1)

    results = run_cases(module)

    passed = 0
    failed = 0
    for name, ok, detail in results:
        status = "PASS" if ok else "FAIL"
        line = f"[{status}] {name}"
        if detail:
            line += f" -- {detail}"
        print(line)
        if ok:
            passed += 1
        else:
            failed += 1

    print(f"\n{passed}/{passed + failed} cases passed")

    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
