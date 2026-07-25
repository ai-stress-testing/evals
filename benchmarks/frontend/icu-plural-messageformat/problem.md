# ICU MessageFormat: CLDR plural/select resolution

**Niche**: internationalization (i18n) — CLDR plural-rule resolution inside
an ICU MessageFormat renderer. This is the exact skill described for
`frontend/i18n-engineer`: "Externalize strings into complete ICU
MessageFormat messages" and "Implement plural ... formatting through
Intl/CLDR APIs, never hand-rolled patterns." Here you *are* the CLDR/ICU
engine — implement it correctly.

You must implement two functions in a single Python module, stdlib only:

```python
def plural_category(locale: str, n: int) -> str:
    ...

def format_icu_message(pattern: str, locale: str, args: dict) -> str:
    ...
```

## Part 1 — `plural_category(locale: str, n: int) -> str`

Given a non-negative integer `n` and a locale, return the CLDR plural
category it resolves to: one of `"zero"`, `"one"`, `"two"`, `"few"`,
`"many"`, `"other"`.

This problem restricts inputs to non-negative integers (no fractional
CLDR operands like `v`/`f`/`t`). Support exactly these five locales, with
the plural rule for each given verbatim below (`i` and `n` are the same
thing here since `n` is always an integer: `mod10 = n % 10`,
`mod100 = n % 100`):

- **`en`** (English)
  - `one`: `n == 1`
  - `other`: everything else

- **`fr`** (French)
  - `one`: `n == 0 or n == 1`
  - `other`: everything else

- **`ru`** (Russian)
  - `one`: `mod10 == 1 and mod100 != 11`
  - `few`: `mod10 in (2, 3, 4) and mod100 not in (12, 13, 14)`
  - `many`: `mod10 == 0 or mod10 in (5, 6, 7, 8, 9) or mod100 in (11, 12, 13, 14)`
  - `other`: everything else

- **`pl`** (Polish)
  - `one`: `n == 1`
  - `few`: `mod10 in (2, 3, 4) and mod100 not in (12, 13, 14)`
  - `many`: `(n != 1 and mod10 in (0, 1)) or mod10 in (5, 6, 7, 8, 9) or mod100 in (12, 13, 14)`
  - `other`: everything else

- **`ar`** (Arabic)
  - `zero`: `n == 0`
  - `one`: `n == 1`
  - `two`: `n == 2`
  - `few`: `3 <= mod100 <= 10`
  - `many`: `11 <= mod100 <= 99`
  - `other`: everything else

Rules are checked in the order listed per locale; the first matching rule
wins.

**Errors**: raise `ValueError` if `locale` is not one of the five above,
or if `n` is not a non-negative `int` (reject `bool`, negative ints, and
non-int types).

## Part 2 — `format_icu_message(pattern: str, locale: str, args: dict) -> str`

Render an ICU-MessageFormat-style `pattern` string, substituting from
`args`, using `plural_category` (from Part 1, for the given `locale`) to
resolve `plural` clauses. Support this subset of ICU MessageFormat syntax:

- **Literal text** is copied through unchanged, except:
  - `''` is a literal single quote.
  - A `'` that is not part of `''` starts a quoted-literal span that runs
    to the next `'` (exclusive); everything inside — including `{`, `}`,
    `#` — is copied through literally and the quotes themselves are
    dropped. (This is how you escape a literal brace or `#`.)
- **Simple substitution**: `{name}` → `str(args["name"])`.
- **Plural**: `{name, plural, [offset:N] selectors}` where `selectors` is
  one or more whitespace-separated entries, each either:
  - `=K {submessage}` — an exact-match selector (`K` a literal integer,
    matched against the *raw* value of `args[name]`, unaffected by
    `offset`), or
  - `keyword {submessage}` — `keyword` is one of
    `zero|one|two|few|many|other`, matched against
    `plural_category(locale, value - offset)`.
  There must be an `other` selector; if none of the other selectors match,
  `other` is used. `offset` defaults to `0` if not given. Inside the
  chosen submessage, `#` is replaced with `str(value - offset)`.
  Exact-match selectors are checked before keyword selectors.
- **Select**: `{name, select, selectors}` where `selectors` is one or
  more whitespace-separated `keyword {submessage}` entries (arbitrary
  string keywords, compared to `str(args[name])` by exact string
  equality). There must be an `other` selector, used when no keyword
  matches.
- Submessages may themselves contain any of the above constructs
  (arbitrary nesting depth), including nested nesting of `plural`/`select`
  inside a `plural`/`select` branch. `#` always refers to the *nearest
  enclosing* `plural`'s `value - offset`.

**Errors**:
- Raise `KeyError` if a placeholder references a name that is not a key
  of `args`.
- Raise `ValueError` for any structurally malformed pattern: unbalanced
  `{`/`}` or unterminated `'`, a `plural`/`select` block missing an
  `other` selector, an unknown clause type (i.e. the second segment after
  the arg name is neither `plural` nor `select` when there is a comma),
  or a `plural` value in `args` that is not a non-negative `int`.
- Locale-resolution errors from `plural_category` (unsupported locale)
  propagate as `ValueError`.

### Worked examples

```python
format_icu_message("Hello, {name}!", "en", {"name": "World"})
# -> "Hello, World!"

format_icu_message(
    "{count, plural, one {# item} other {# items}}", "en", {"count": 1}
)
# -> "1 item"

format_icu_message(
    "{count, plural, offset:1 =0 {No one} =1 {Just you}"
    " one {You and # other} other {You and # others}}",
    "en", {"count": 0},
)
# -> "No one"   (exact match on raw value 0, offset not applied to it)

format_icu_message(
    "{count, plural, offset:1 =0 {No one} =1 {Just you}"
    " one {You and # other} other {You and # others}}",
    "en", {"count": 2},
)
# -> "You and 1 other"   (no exact match; category from 2-1=1 -> "one"; # = 2-1 = 1)

format_icu_message(
    "{gender, select, male {He} female {She} other {They}} liked this.",
    "en", {"gender": "male"},
)
# -> "He liked this."

format_icu_message(
    "{count, plural, one {# файл} few {# файла} many {# файлов} other {# файла}}",
    "ru", {"count": 21},
)
# -> "21 файл"   (21 -> mod10=1, mod100=21 -> "one")
```

## Files in this directory

- `reference_solution.py` — a correct implementation.
- `broken_solution.py` — a deliberately-wrong variant (one bug) that the
  checker must catch.
- `check.py` — the automated judge. Run as:
  `python3 check.py <path-to-solution.py>`. Prints a pass/fail summary
  per test case, exits `0` iff every case passes, else exits `1`.
