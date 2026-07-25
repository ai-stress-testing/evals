# WCAG Contrast-Ratio Computation

## Niche

Implement the **WCAG 2.x contrast-ratio calculation** — the exact
arithmetic pipeline a design-system tool or accessibility auditor uses to
decide whether a foreground/background color pairing (e.g. text color vs.
its background) is legible enough to ship. This is not a generic color
utility: it is the specific formula defined by WCAG 2.x
(https://www.w3.org/TR/WCAG21/#dfn-relative-luminance and
`#dfn-contrast-ratio`), which every design-token contrast linter and every
`agents/testing/accessibility-auditor` / `agents/frontend/section-508-specialist`
review ultimately reduces to.

The pipeline, per channel of an sRGB color:

1. Normalize the 8-bit channel value to `[0, 1]`: `c = value / 255.0`.
2. Convert to linear light via the WCAG piecewise function:
   - if `c <= 0.03928`: `c_lin = c / 12.92`
   - else: `c_lin = ((c + 0.055) / 1.055) ** 2.4`
3. Compute **relative luminance** as the weighted sum of the linearized
   channels:
   `L = 0.2126 * R_lin + 0.7152 * G_lin + 0.0722 * B_lin`
4. Given the relative luminances `L1` (lighter color) and `L2` (darker
   color) of the two colors being compared (`L1 >= L2` after sorting),
   compute the **contrast ratio**:
   `contrast = (L1 + 0.05) / (L2 + 0.05)`

The result is always in the range `[1.0, 21.0]`.

## Required interface

Your solution file must define, at module scope, exactly these functions:

```python
def relative_luminance(hex_color: str) -> float:
    """
    hex_color: an sRGB color as a hex string, either 6 hex digits with a
        leading '#' (e.g. "#RRGGBB") or without (e.g. "RRGGBB").
        Hex digits may be upper or lower case.

    Returns the WCAG relative luminance (a float in [0.0, 1.0]) computed
    per the pipeline above.

    Raises ValueError if hex_color is not a valid 6-hex-digit sRGB color
    (wrong length, non-hex characters, etc.).
    """

def contrast_ratio(hex_a: str, hex_b: str) -> float:
    """
    hex_a, hex_b: two sRGB hex colors (same format as relative_luminance).

    Returns the WCAG contrast ratio between the two colors as a float in
    [1.0, 21.0]. Order of arguments must not matter -- contrast_ratio(a, b)
    == contrast_ratio(b, a).
    """

def wcag_verdict(hex_fg: str, hex_bg: str, large_text: bool = False) -> dict:
    """
    hex_fg: foreground (text) color.
    hex_bg: background color.
    large_text: True if the text qualifies as "large" per WCAG (>=18pt,
        or >=14pt bold) -- this lowers the required thresholds.

    Returns a dict with exactly these keys:
        {
            "ratio": float,     # the contrast ratio, as from contrast_ratio()
            "aa_pass": bool,    # True iff ratio meets the AA threshold
            "aaa_pass": bool,   # True iff ratio meets the AAA threshold
        }

    Thresholds (WCAG 2.x):
        - normal text: AA >= 4.5:1,  AAA >= 7.0:1
        - large text:  AA >= 3.0:1,  AAA >= 4.5:1

    A ratio exactly equal to a threshold counts as a pass (thresholds are
    inclusive, e.g. a ratio of exactly 4.5 passes AA for normal text).
    """
```

## Edge cases to handle

- **Pure black on pure white** (`#000000` vs `#FFFFFF`, either order) must
  yield a contrast ratio of **exactly 21.0** (within floating-point
  tolerance) -- this is the canonical WCAG reference value and the
  maximum possible ratio.
- **Identical colors** (e.g. `#336699` vs `#336699`) must yield a contrast
  ratio of **exactly 1.0** -- the minimum possible ratio.
- **Argument order must not matter**: `contrast_ratio(a, b) ==
  contrast_ratio(b, a)`.
- **Threshold boundaries are inclusive**: a ratio of exactly `4.5` passes
  AA normal text; a ratio of exactly `3.0` passes AA large text; a ratio
  of exactly `7.0` passes AAA normal text; a ratio of exactly `4.5` passes
  AAA large text.
- **Input normalization**: hex strings with or without a leading `#`, and
  in either case (`"abc123"`, `"ABC123"`, `"#ABC123"`), must all be
  accepted and treated identically.
- **Invalid input**: a hex string of the wrong length (e.g. 3-digit
  shorthand, 7 characters) or containing non-hex characters must raise
  `ValueError` from `relative_luminance` (and therefore from
  `contrast_ratio` / `wcag_verdict`, which build on it) -- not silently
  return a wrong number, and not crash with an unrelated exception type.

## What NOT to do

- Do not use any image, color-management, or third-party color library
  (e.g. no `colorsys`-based shortcuts that skip the WCAG piecewise
  linearization, no `Pillow`, no `colormath`). The linearization constants
  (`0.03928`, `12.92`, `0.055`, `1.055`, `2.4`) and luminance weights
  (`0.2126`, `0.7152`, `0.0722`) must appear in your own arithmetic.
- Do not round intermediate luminance values -- only the final reported
  `ratio` may be subject to normal floating-point display precision; the
  pass/fail booleans must be computed from the unrounded ratio.
