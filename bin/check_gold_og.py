#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# check_gold_og.py
# Verifies real page assets adhere to Gold (profile/GLOSSARY.md) and
# carry a full Open Graph tag set. Checks HTML files directly and
# extracts embedded HTML templates from Python source (e.g. gopher2html's
# PAGE_HEAD string) via a real triple-quoted-string scan, not a full
# Python parse -- this only needs the literal markup, not the runtime
# f-string interpolation around it.

import os
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


LOCAL_STYLESHEET_RE = re.compile(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"[^>]*>')

# Linked local <script> files -- checked separately from inline markup
# (see check_linked_theme_js) because the exact bug this catches lives
# in JS behavior, not HTML presence: tcos-www's shell/tc-theme.js had
# the right data-theme-choice buttons in markup (already passed every
# check above) but read the wrong JS property (dataset.theme instead
# of dataset.themeChoice), so every click was a silent no-op. Found
# 2026-08-28 by diffing against the real reference implementation
# (.github/bin/render-review.py, this same file) directly -- a
# markup-only checker structurally cannot catch this class of bug.
LOCAL_SCRIPT_RE = re.compile(r'<script[^>]+src="([^"]+)"[^>]*>')
THEME_BTN_RE = re.compile(r'\.theme-btn\b')
DATASET_THEME_CHOICE_RE = re.compile(r'dataset\.themeChoice\b')
DATASET_THEME_WRONG_RE = re.compile(r'dataset\.theme\b(?!Choice)')


def inline_local_stylesheets(markup: str, base_dir: str) -> str:
    """Some real Gold ports (tcos-www) use one external css/site.css for
    every page rather than an inline <style> block per page -- real,
    legitimate architecture, not a mistake. Append any local (non-http)
    linked stylesheet's content so token/font checks still see it,
    instead of permanently missing tokens that are real but off-page."""
    extra = []
    for href in LOCAL_STYLESHEET_RE.findall(markup):
        if href.startswith("http://") or href.startswith("https://"):
            continue
        css_path = os.path.join(base_dir, href)
        if os.path.isfile(css_path):
            with open(css_path, encoding="utf-8", errors="replace") as f:
                extra.append(f.read())
    return markup + "\n".join(extra)


def extract_markup(path: str) -> str:
    """Path-reading wrapper around extract_markup_from_text, also pulling
    in any local linked stylesheet's content (see inline_local_stylesheets)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        text = f.read()
    markup = extract_markup_from_text(text, is_python=path.endswith(".py"))
    if not path.endswith(".py"):
        markup = inline_local_stylesheets(markup, os.path.dirname(os.path.abspath(path)))
    return markup


def check_linked_theme_js(markup: str, base_dir: str) -> list:
    """Real, separate check (not folded into check_file_from_markup's
    markup-only checks): any locally-linked <script> that implements the
    theme toggle (has a real .theme-btn handler) must read
    dataset.themeChoice, matching render-review.py's reference
    implementation -- not dataset.theme, the exact hand-copy bug found
    2026-08-28 in tcos-www's shell/tc-theme.js. A page can correctly
    show data-theme-choice="light/dark/auto" buttons (passing every
    check above) while the JS wired to them is silently broken -- this
    is the only check in this file that can catch that."""
    failures = []
    for href in LOCAL_SCRIPT_RE.findall(markup):
        if href.startswith("http://") or href.startswith("https://"):
            continue
        js_path = os.path.join(base_dir, href)
        if not os.path.isfile(js_path):
            continue
        with open(js_path, encoding="utf-8", errors="replace") as f:
            js = f.read()
        if not THEME_BTN_RE.search(js):
            continue  # this script doesn't implement the theme toggle at all
        if DATASET_THEME_WRONG_RE.search(js):
            failures.append(
                f"Gold theme JS ({href}): reads dataset.theme instead of "
                "dataset.themeChoice -- matches tcos-www's exact 2026-08-28 "
                "hand-copy bug, theme clicks would be a silent no-op"
            )
        elif not DATASET_THEME_CHOICE_RE.search(js):
            failures.append(
                f"Gold theme JS ({href}): has .theme-btn handling but never "
                "reads dataset.themeChoice -- doesn't match the reference "
                "implementation, verify by hand"
            )
    return failures


def component_score(markup: str) -> tuple:
    """Simple math: (present, total) across every individual Gold/OG
    check -- a quick completeness score alongside the pass/fail detail."""
    checks = [
        GOLD_ACCENT_LIGHT_RE, GOLD_ACCENT_DARK_RE, GOLD_SANS_RE, GOLD_MONO_RE,
        GOLD_PREPAINT_RE, GOLD_LU_ROW_RE, GOLD_LU_ISO_RE,
    ]
    checks += list(GOLD_THEME_TOGGLE_RES.values())
    checks += list(GOLD_FONTSIZE_TOGGLE_RES.values())
    checks += [pattern for _, pattern in REQUIRED_META]
    present = sum(1 for pattern in checks if pattern.search(markup))
    return present, len(checks)


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
    """Path-reading wrapper around check_file_from_markup, plus the
    linked-theme-JS check (needs base_dir, so it can't live in the
    markup-only path -- see check_linked_theme_js)."""
    failures = check_file_from_markup(extract_markup(path))
    if not path.endswith(".py"):
        with open(path, encoding="utf-8", errors="replace") as f:
            raw_markup = f.read()
        failures += check_linked_theme_js(raw_markup, os.path.dirname(os.path.abspath(path)))
    return failures


def main(argv: list) -> int:
    if not argv:
        print("usage: check_gold_og.py <file> [file...]", file=sys.stderr)
        return 2

    any_failed = False
    for path in argv:
        markup = extract_markup(path)
        failures = check_file_from_markup(markup)
        present, total = component_score(markup)
        status = "FAIL" if failures else "PASS"
        if failures:
            any_failed = True
        print(f"{status} {path} ({present}/{total} components)")
        for f in failures:
            print(f"  - {f}")

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
