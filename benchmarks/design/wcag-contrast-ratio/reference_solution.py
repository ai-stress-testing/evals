"""Reference solution: WCAG 2.x contrast-ratio computation.

Implements the relative-luminance / contrast-ratio pipeline exactly as
specified in problem.md (and in the WCAG 2.x spec).
"""
import re

_HEX_RE = re.compile(r"^[0-9a-fA-F]{6}$")


def _parse_hex(hex_color: str):
    if not isinstance(hex_color, str):
        raise ValueError(f"hex_color must be a string, got {type(hex_color)!r}")
    s = hex_color[1:] if hex_color.startswith("#") else hex_color
    if not _HEX_RE.match(s):
        raise ValueError(f"invalid sRGB hex color: {hex_color!r}")
    r = int(s[0:2], 16)
    g = int(s[2:4], 16)
    b = int(s[4:6], 16)
    return r, g, b


def _linearize(channel_8bit: int) -> float:
    c = channel_8bit / 255.0
    if c <= 0.03928:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = _parse_hex(hex_color)
    r_lin = _linearize(r)
    g_lin = _linearize(g)
    b_lin = _linearize(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(hex_a: str, hex_b: str) -> float:
    la = relative_luminance(hex_a)
    lb = relative_luminance(hex_b)
    l1, l2 = (la, lb) if la >= lb else (lb, la)
    return (l1 + 0.05) / (l2 + 0.05)


def wcag_verdict(hex_fg: str, hex_bg: str, large_text: bool = False) -> dict:
    ratio = contrast_ratio(hex_fg, hex_bg)
    if large_text:
        aa_threshold, aaa_threshold = 3.0, 4.5
    else:
        aa_threshold, aaa_threshold = 4.5, 7.0
    return {
        "ratio": ratio,
        "aa_pass": ratio >= aa_threshold,
        "aaa_pass": ratio >= aaa_threshold,
    }
