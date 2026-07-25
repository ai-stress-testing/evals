#!/usr/bin/env python3
"""Automated judge for the ICU MessageFormat / CLDR plural-rule benchmark.

Usage:
    python3 check.py <path-to-solution.py>

Dynamically imports the given module by path, exercises it against a fixed
set of deterministic test cases (both `plural_category` and
`format_icu_message`), prints a pass/fail summary, and exits 0 iff every
case passes, else exits 1. Stdlib only.
"""
import importlib.util
import sys


def load_module(path):
    spec = importlib.util.spec_from_file_location("solution_under_test", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load module from {path!r}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --- Part 1: plural_category test cases -----------------------------------
# (locale, n) -> expected category
PLURAL_CATEGORY_CASES = [
    (("en", 0), "other"),
    (("en", 1), "one"),
    (("en", 2), "other"),
    (("en", 21), "other"),
    (("fr", 0), "one"),
    (("fr", 1), "one"),
    (("fr", 2), "other"),
    (("fr", 21), "other"),
    (("ru", 1), "one"),
    (("ru", 2), "few"),
    (("ru", 4), "few"),
    (("ru", 5), "many"),
    (("ru", 10), "many"),
    (("ru", 11), "many"),
    (("ru", 12), "many"),
    (("ru", 14), "many"),
    (("ru", 21), "one"),
    (("ru", 22), "few"),
    (("ru", 25), "many"),
    (("ru", 100), "many"),
    (("ru", 101), "one"),
    (("ru", 114), "many"),
    (("pl", 1), "one"),
    (("pl", 2), "few"),
    (("pl", 5), "many"),
    (("pl", 12), "many"),
    (("pl", 22), "few"),
    (("pl", 0), "many"),
    (("ar", 0), "zero"),
    (("ar", 1), "one"),
    (("ar", 2), "two"),
    (("ar", 3), "few"),
    (("ar", 10), "few"),
    (("ar", 11), "many"),
    (("ar", 99), "many"),
    (("ar", 100), "other"),
    (("ar", 101), "other"),
]

PLURAL_CATEGORY_ERROR_CASES = [
    ("de", 1),      # unsupported locale
    ("en", -1),     # negative
    ("en", 1.5),    # not an int
    ("en", True),   # bool is not a valid int here
]

# --- Part 2: format_icu_message test cases ---------------------------------
# (pattern, locale, args) -> expected string
FORMAT_CASES = [
    ("Hello, {name}!", "en", {"name": "World"}, "Hello, World!"),
    (
        "{count, plural, one {# item} other {# items}}",
        "en", {"count": 1}, "1 item",
    ),
    (
        "{count, plural, one {# item} other {# items}}",
        "en", {"count": 0}, "0 items",
    ),
    (
        "{count, plural, one {# item} other {# items}}",
        "en", {"count": 5}, "5 items",
    ),
    (
        "{count, plural, =0 {No items} one {One item} other {# items}}",
        "en", {"count": 0}, "No items",
    ),
    (
        "{count, plural, =0 {No items} one {One item} other {# items}}",
        "en", {"count": 1}, "One item",
    ),
    (
        "{count, plural, =0 {No items} one {One item} other {# items}}",
        "en", {"count": 3}, "3 items",
    ),
    (
        "{count, plural, offset:1 =0 {No one} =1 {Just you}"
        " one {You and # other} other {You and # others}}",
        "en", {"count": 0}, "No one",
    ),
    (
        "{count, plural, offset:1 =0 {No one} =1 {Just you}"
        " one {You and # other} other {You and # others}}",
        "en", {"count": 1}, "Just you",
    ),
    (
        "{count, plural, offset:1 =0 {No one} =1 {Just you}"
        " one {You and # other} other {You and # others}}",
        "en", {"count": 2}, "You and 1 other",
    ),
    (
        "{count, plural, offset:1 =0 {No one} =1 {Just you}"
        " one {You and # other} other {You and # others}}",
        "en", {"count": 3}, "You and 2 others",
    ),
    (
        "{gender, select, male {He} female {She} other {They}} liked this.",
        "en", {"gender": "male"}, "He liked this.",
    ),
    (
        "{gender, select, male {He} female {She} other {They}} liked this.",
        "en", {"gender": "female"}, "She liked this.",
    ),
    (
        "{gender, select, male {He} female {She} other {They}} liked this.",
        "en", {"gender": "nonbinary"}, "They liked this.",
    ),
    (
        "{count, plural, one {# файл} few {# файла} many {# файлов} other {# файла}}",
        "ru", {"count": 1}, "1 файл",
    ),
    (
        "{count, plural, one {# файл} few {# файла} many {# файлов} other {# файла}}",
        "ru", {"count": 2}, "2 файла",
    ),
    (
        "{count, plural, one {# файл} few {# файла} many {# файлов} other {# файла}}",
        "ru", {"count": 5}, "5 файлов",
    ),
    (
        "{count, plural, one {# файл} few {# файла} many {# файлов} other {# файла}}",
        "ru", {"count": 11}, "11 файлов",
    ),
    (
        "{count, plural, one {# файл} few {# файла} many {# файлов} other {# файла}}",
        "ru", {"count": 21}, "21 файл",
    ),
    (
        # nested select+plural
        "{gender, select, "
        "male {{count, plural, one {He has # item} other {He has # items}}} "
        "other {{count, plural, one {They have # item} other {They have # items}}}}",
        "en", {"gender": "male", "count": 1}, "He has 1 item",
    ),
    (
        "{gender, select, "
        "male {{count, plural, one {He has # item} other {He has # items}}} "
        "other {{count, plural, one {They have # item} other {They have # items}}}}",
        "en", {"gender": "unspecified", "count": 3}, "They have 3 items",
    ),
    (
        # quote-escaping: '' -> literal apostrophe; '{' / '}' -> literal braces
        "Roger''s items: {count} '{'not a placeholder'}'",
        "en", {"count": 5}, "Roger's items: 5 {not a placeholder}",
    ),
]

# (pattern, locale, args, expected_exception_type)
FORMAT_ERROR_CASES = [
    ("{count, plural, one {# item}}", "en", {"count": 1}, ValueError),  # missing 'other'
    ("{name}", "en", {}, KeyError),  # missing arg
    ("{count, plural, one {# item} other {# items}}", "de", {"count": 1}, ValueError),  # bad locale
    ("{count, frobnicate, one {x} other {y}}", "en", {"count": 1}, ValueError),  # unknown clause type
    ("{count, plural, one {# item} other {# items}}", "en", {"count": -1}, ValueError),  # negative value
    ("{count, plural, one {# item} other {# items}}", "en", {"count": 1.5}, ValueError),  # non-int value
]


def main():
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <path-to-solution.py>")
        sys.exit(1)

    path = sys.argv[1]
    failures = []
    passed = 0

    try:
        mod = load_module(path)
    except Exception as e:
        print(f"FAIL: could not import module {path!r}: {e!r}")
        sys.exit(1)

    for fn_name in ("plural_category", "format_icu_message"):
        if not hasattr(mod, fn_name):
            failures.append(f"module is missing required function {fn_name!r}")

    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        sys.exit(1)

    # Part 1: plural_category, expected-value cases
    for (locale, n), expected in PLURAL_CATEGORY_CASES:
        try:
            got = mod.plural_category(locale, n)
        except Exception as e:
            failures.append(
                f"plural_category({locale!r}, {n!r}) raised {e!r}, expected {expected!r}"
            )
            continue
        if got != expected:
            failures.append(
                f"plural_category({locale!r}, {n!r}) == {got!r}, expected {expected!r}"
            )
        else:
            passed += 1

    # Part 1: plural_category, error cases
    for locale, n in PLURAL_CATEGORY_ERROR_CASES:
        try:
            got = mod.plural_category(locale, n)
        except ValueError:
            passed += 1
        except Exception as e:
            failures.append(
                f"plural_category({locale!r}, {n!r}) raised {type(e).__name__}, expected ValueError"
            )
        else:
            failures.append(
                f"plural_category({locale!r}, {n!r}) == {got!r}, expected a ValueError"
            )

    # Part 2: format_icu_message, expected-value cases
    for pattern, locale, args, expected in FORMAT_CASES:
        try:
            got = mod.format_icu_message(pattern, locale, args)
        except Exception as e:
            failures.append(
                f"format_icu_message({pattern!r}, {locale!r}, {args!r}) raised "
                f"{type(e).__name__}: {e}, expected {expected!r}"
            )
            continue
        if got != expected:
            failures.append(
                f"format_icu_message({pattern!r}, {locale!r}, {args!r}) == {got!r}, "
                f"expected {expected!r}"
            )
        else:
            passed += 1

    # Part 2: format_icu_message, error cases
    for pattern, locale, args, exc_type in FORMAT_ERROR_CASES:
        try:
            got = mod.format_icu_message(pattern, locale, args)
        except exc_type:
            passed += 1
        except Exception as e:
            failures.append(
                f"format_icu_message({pattern!r}, {locale!r}, {args!r}) raised "
                f"{type(e).__name__}, expected {exc_type.__name__}"
            )
        else:
            failures.append(
                f"format_icu_message({pattern!r}, {locale!r}, {args!r}) == {got!r}, "
                f"expected a {exc_type.__name__}"
            )

    total = len(PLURAL_CATEGORY_CASES) + len(PLURAL_CATEGORY_ERROR_CASES) \
        + len(FORMAT_CASES) + len(FORMAT_ERROR_CASES)

    print(f"{passed}/{total} cases passed")
    if failures:
        print(f"{len(failures)} FAILURE(S):")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("PASS: all cases passed")
    sys.exit(0)


if __name__ == "__main__":
    main()
