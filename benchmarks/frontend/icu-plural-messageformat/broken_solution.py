"""Deliberately-broken solution for the ICU MessageFormat / CLDR plural-rule
benchmark (used to verify check.py actually catches failures).

Bug: the plural `=N` exact-match selector is checked against
`value - offset` instead of the raw `value`, per the ICU spec (see
problem.md worked example with offset:1 and count=0/1).
"""

_SUPPORTED_LOCALES = ("en", "fr", "ru", "pl", "ar")


def plural_category(locale: str, n: int) -> str:
    if locale not in _SUPPORTED_LOCALES:
        raise ValueError(f"unsupported locale: {locale!r}")
    if isinstance(n, bool) or not isinstance(n, int):
        raise ValueError(f"n must be a non-negative int, got {n!r}")
    if n < 0:
        raise ValueError(f"n must be non-negative, got {n!r}")

    mod10 = n % 10
    mod100 = n % 100

    if locale == "en":
        return "one" if n == 1 else "other"

    if locale == "fr":
        return "one" if (n == 0 or n == 1) else "other"

    if locale == "ru":
        if mod10 == 1 and mod100 != 11:
            return "one"
        if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
            return "few"
        if mod10 == 0 or mod10 in (5, 6, 7, 8, 9) or mod100 in (11, 12, 13, 14):
            return "many"
        return "other"

    if locale == "pl":
        if n == 1:
            return "one"
        if mod10 in (2, 3, 4) and mod100 not in (12, 13, 14):
            return "few"
        if (n != 1 and mod10 in (0, 1)) or mod10 in (5, 6, 7, 8, 9) or mod100 in (12, 13, 14):
            return "many"
        return "other"

    if locale == "ar":
        if n == 0:
            return "zero"
        if n == 1:
            return "one"
        if n == 2:
            return "two"
        if 3 <= mod100 <= 10:
            return "few"
        if 11 <= mod100 <= 99:
            return "many"
        return "other"

    raise ValueError(f"unsupported locale: {locale!r}")  # unreachable


_KEYWORDS = ("zero", "one", "two", "few", "many", "other")


def _find_matching_brace(s: str, i: int) -> int:
    """s[i] must be '{'. Return the index of the matching '}', skipping
    over quoted spans so braces inside a quoted literal don't count."""
    assert s[i] == "{"
    depth = 0
    k = i
    n = len(s)
    while k < n:
        c = s[k]
        if c == "'":
            if k + 1 < n and s[k + 1] == "'":
                k += 2
                continue
            j = s.find("'", k + 1)
            if j == -1:
                raise ValueError("unterminated quote in pattern")
            k = j + 1
            continue
        if c == "{":
            depth += 1
            k += 1
            continue
        if c == "}":
            depth -= 1
            k += 1
            if depth == 0:
                return k - 1
            continue
        k += 1
    raise ValueError("unbalanced braces in pattern")


def _parse_selectors(s: str) -> dict:
    """Parse a whitespace-separated sequence of `key {submessage}` entries."""
    result = {}
    i = 0
    n = len(s)
    while i < n:
        while i < n and s[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n and s[i] not in " \t\n\r{":
            i += 1
        key = s[start:i]
        if not key:
            raise ValueError("malformed selector list")
        while i < n and s[i].isspace():
            i += 1
        if i >= n or s[i] != "{":
            raise ValueError(f"expected '{{' after selector key {key!r}")
        j = _find_matching_brace(s, i)
        result[key] = s[i + 1 : j]
        i = j + 1
    return result


def _render(s: str, args: dict, locale: str, hash_value):
    out = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if c == "'":
            if i + 1 < n and s[i + 1] == "'":
                out.append("'")
                i += 2
                continue
            j = s.find("'", i + 1)
            if j == -1:
                raise ValueError("unterminated quote in pattern")
            out.append(s[i + 1 : j])
            i = j + 1
            continue
        if c == "#":
            if hash_value is None:
                raise ValueError("'#' used outside of a plural context")
            out.append(hash_value)
            i += 1
            continue
        if c == "{":
            j = _find_matching_brace(s, i)
            inner = s[i + 1 : j]
            out.append(_handle_placeholder(inner, args, locale))
            i = j + 1
            continue
        if c == "}":
            raise ValueError("unbalanced braces in pattern")
        out.append(c)
        i += 1
    return "".join(out)


def _handle_placeholder(inner: str, args: dict, locale: str) -> str:
    if "," not in inner:
        name = inner.strip()
        if name not in args:
            raise KeyError(name)
        return str(args[name])

    name, rest = inner.split(",", 1)
    name = name.strip()
    rest = rest.strip()

    type_str, _, selector_str = rest.partition(",")
    type_str = type_str.strip()
    selector_str = selector_str.strip()

    if type_str not in ("plural", "select"):
        raise ValueError(f"unknown clause type: {type_str!r}")

    if name not in args:
        raise KeyError(name)
    value = args[name]

    if type_str == "select":
        selectors = _parse_selectors(selector_str)
        if "other" not in selectors:
            raise ValueError("select clause missing 'other' selector")
        key = str(value)
        chosen = selectors.get(key, selectors["other"])
        return _render(chosen, args, locale, hash_value=None)

    # plural
    offset = 0
    s2 = selector_str
    stripped = s2.lstrip()
    if stripped.startswith("offset:"):
        rest2 = stripped[len("offset:"):]
        j = 0
        if j < len(rest2) and rest2[j] in "+-":
            j += 1
        start_digits = j
        while j < len(rest2) and rest2[j].isdigit():
            j += 1
        if j == start_digits:
            raise ValueError("malformed offset")
        offset = int(rest2[:j])
        s2 = rest2[j:]

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"plural value must be a non-negative int, got {value!r}")

    selectors = _parse_selectors(s2)
    if "other" not in selectors:
        raise ValueError("plural clause missing 'other' selector")

    exact_key = f"={value - offset}"  # BUG: offset must not apply to exact-match (=N) selectors
    if exact_key in selectors:
        chosen = selectors[exact_key]
    else:
        cat = plural_category(locale, value - offset)
        chosen = selectors.get(cat, selectors["other"])

    hash_value = str(value - offset)
    return _render(chosen, args, locale, hash_value=hash_value)


def format_icu_message(pattern: str, locale: str, args: dict) -> str:
    return _render(pattern, args, locale, hash_value=None)
