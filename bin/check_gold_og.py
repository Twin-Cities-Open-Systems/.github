#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# check_gold_og.py
# Verifies real page assets adhere to Gold (profile/GLOSSARY.md) and
# carry a full Open Graph tag set. Checks HTML files directly and
# extracts embedded HTML templates from Python source (e.g. gopher2html's
# PAGE_HEAD string) via a real triple-quoted-string scan, not a full
# Python parse -- this only needs the literal markup, not the runtime
# f-string interpolation around it.

import re
import sys

# Real Gold components (profile/GLOSSARY.md -- "Gold" entry), checked by
# VALUE/text rather than CSS variable name -- every real port so far
# (resume#32, fleet-ops#330) kept its own pre-existing variable names
# (--bg/--pane-bg/--text) and just swapped the values, rather than
# renaming to Gold's own canonical names (--ground/--surface/--ink).
# Checking literal values is what's actually portable across that; a
# name-based check would false-fail every real port that exists today.

# Both light AND dark accent values must be present -- proves the full
# light/dark token block exists, not just one stray color reference.
GOLD_ACCENT_LIGHT_RE = re.compile(r"#0d7d78", re.IGNORECASE)
GOLD_ACCENT_DARK_RE = re.compile(r"#3fd4c8", re.IGNORECASE)

# Gold's own name (Spencer, direct, 2026-08-28: "this is the name...
# IBM Plex Sans - JetBrains Mono") -- both fonts required, not just one.
GOLD_SANS_RE = re.compile(r"IBM\s*\+?Plex\s*\+?Sans", re.IGNORECASE)
GOLD_MONO_RE = re.compile(r"JetBrains\s*\+?Mono", re.IGNORECASE)

# Theme toggle: the three data-theme-choice buttons, copied verbatim
# (values, not just markup shape) across every real port so far.
GOLD_THEME_TOGGLE_RES = {
    "light": re.compile(r'data-theme-choice="light"'),
    "dark": re.compile(r'data-theme-choice="dark"'),
    "auto": re.compile(r'data-theme-choice="auto"'),
}

# Pre-paint theme script -- the localStorage key + no-flash pattern,
# copied verbatim across every real port so far.
GOLD_PREPAINT_RE = re.compile(r'localStorage\.getItem\("tcos-theme"\)')

# Font-size toggle (S/M/L/XL/XXL) and the lu: freshness row -- real,
# required Gold components, not optional extras. Missed on the first 4
# real ports (resume#32, fleet-ops#330); caught live, 2026-08-28:
# "should all be together, how miss? make not happen again." Gold is a
# bundle of interchangeable components (Spencer, direct) -- every
# component gets its own check here so a partial port fails loudly
# instead of silently shipping "close enough."
GOLD_FONTSIZE_TOGGLE_RES = {
    "s": re.compile(r'data-size="s"'),
    "m": re.compile(r'data-size="m"'),
    "l": re.compile(r'data-size="l"'),
    "xl": re.compile(r'data-size="xl"'),
    "xxl": re.compile(r'data-size="xxl"'),
}
GOLD_LU_ROW_RE = re.compile(r'class="lu-row"')
GOLD_LU_ISO_RE = re.compile(r'class="lu-iso"')

# Full OG set, per view.lab.tcos.us's own <head> (the reference instance).
# canonical + meta description travel with OG in practice even though
# they're not technically part of the OG spec -- real precedent is to
# check them together, they're always added/removed as a set.
REQUIRED_META = [
    ("og:site_name", re.compile(r'property="og:site_name"')),
    ("og:title", re.compile(r'property="og:title"')),
    ("og:description", re.compile(r'property="og:description"')),
    ("og:type", re.compile(r'property="og:type"')),
    ("og:url", re.compile(r'property="og:url"')),
    ("twitter:card", re.compile(r'name="twitter:card"')),
    ("meta description", re.compile(r'name="description"')),
    ("canonical link", re.compile(r'rel="canonical"')),
]

TRIPLE_QUOTED_RE = re.compile(r'"""(.*?)"""', re.DOTALL)


def extract_markup_from_text(text: str, is_python: bool) -> str:
    """Return the real markup to scan: the text itself for .html, or
    every triple-quoted string literal for .py (covers PAGE_HEAD-style
    embedded templates without a full Python parse)."""
    if is_python:
        return "\n".join(TRIPLE_QUOTED_RE.findall(text))
    return text


def extract_markup(path: str) -> str:
    """Path-reading wrapper around extract_markup_from_text."""
    text = open(path, encoding="utf-8", errors="replace").read()
    return extract_markup_from_text(text, is_python=path.endswith(".py"))


def check_file_from_markup(markup: str) -> list:
    """Returns a list of plain-text failure strings for this markup --
    empty list means it passed. Never encodes pass/fail as color alone
    (PROMPTING_RULES.md rule #11) -- callers print these as labeled text."""
    failures = []

    missing_tokens = []
    if not GOLD_ACCENT_LIGHT_RE.search(markup):
        missing_tokens.append("light accent (#0d7d78)")
    if not GOLD_ACCENT_DARK_RE.search(markup):
        missing_tokens.append("dark accent (#3fd4c8)")
    if not GOLD_SANS_RE.search(markup):
        missing_tokens.append("IBM Plex Sans")
    if not GOLD_MONO_RE.search(markup):
        missing_tokens.append("JetBrains Mono")
    if missing_tokens:
        failures.append("Gold tokens: missing " + ", ".join(missing_tokens))

    missing_toggle = [
        choice for choice, pattern in GOLD_THEME_TOGGLE_RES.items()
        if not pattern.search(markup)
    ]
    if missing_toggle:
        failures.append(
            "Gold theme toggle: missing button(s) for " + ", ".join(missing_toggle)
        )
    if not GOLD_PREPAINT_RE.search(markup):
        failures.append("Gold theme system: missing pre-paint script (no-flash localStorage read)")

    missing_fontsize = [
        size for size, pattern in GOLD_FONTSIZE_TOGGLE_RES.items()
        if not pattern.search(markup)
    ]
    if missing_fontsize:
        failures.append(
            "Gold font-size toggle: missing size(s) " + ", ".join(missing_fontsize)
        )

    if not GOLD_LU_ROW_RE.search(markup):
        failures.append("Gold lu: row: missing (class=\"lu-row\")")
    if not GOLD_LU_ISO_RE.search(markup):
        failures.append("Gold lu: row: missing timestamp (class=\"lu-iso\")")

    for label, pattern in REQUIRED_META:
        if not pattern.search(markup):
            failures.append(f"OG: missing {label}")

    return failures


def check_file(path: str) -> list:
    """Path-reading wrapper around check_file_from_markup."""
    return check_file_from_markup(extract_markup(path))


def main(argv: list) -> int:
    if not argv:
        print("usage: check_gold_og.py <file> [file...]", file=sys.stderr)
        return 2

    any_failed = False
    for path in argv:
        failures = check_file(path)
        if failures:
            any_failed = True
            print(f"FAIL {path}")
            for f in failures:
                print(f"  - {f}")
        else:
            print(f"PASS {path}")

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
