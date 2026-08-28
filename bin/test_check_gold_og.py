#!/usr/bin/env python3
# Spencer Butler <dev@tcos.us>
# test_check_gold_og.py
# Real unit tests for check_gold_og.py -- known-good and known-bad
# fixtures for both the Gold-adherence checks and the OG-completeness
# checks, plus the .py embedded-template extraction path.

import unittest

import check_gold_og as cgo


GOOD_HTML = """<!DOCTYPE html>
<html><head>
<title>test</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono&family=IBM+Plex+Sans">
<meta property="og:site_name" content="Test">
<meta property="og:title" content="Test">
<meta property="og:description" content="Test">
<meta property="og:type" content="website">
<meta property="og:url" content="https://example.com/">
<meta name="twitter:card" content="summary">
<meta name="description" content="Test">
<link rel="canonical" href="https://example.com/">
<script>
(function () {
  try {
    var t = localStorage.getItem("tcos-theme") || "dark";
  } catch (e) {}
})();
</script>
<style>:root { --accent: #0d7d78; }
@media (prefers-color-scheme: dark) { :root { --accent: #3fd4c8; } }
</style>
</head><body>
<button data-theme-choice="light">Light</button>
<button data-theme-choice="dark">Dark</button>
<button data-theme-choice="auto">Auto</button>
</body></html>"""

BARE_HTML = "<html><head><title>bare</title></head><body>nothing here</body></html>"


class TestGoldTokens(unittest.TestCase):
    def test_full_pass(self):
        self.assertEqual(cgo.check_file_from_markup(GOOD_HTML), [])

    def test_missing_everything(self):
        failures = cgo.check_file_from_markup(BARE_HTML)
        self.assertTrue(any("Gold tokens" in f for f in failures))
        self.assertTrue(any("Gold theme toggle" in f for f in failures))
        self.assertTrue(any("Gold theme system" in f for f in failures))
        self.assertTrue(any("OG: missing og:site_name" in f for f in failures))

    def test_partial_font_pair_fails(self):
        # Only IBM Plex Sans, no JetBrains Mono -- the pair is the name,
        # one font alone doesn't count as Gold.
        markup = GOOD_HTML.replace("JetBrains+Mono&", "")
        failures = cgo.check_file_from_markup(markup)
        self.assertTrue(any("JetBrains Mono" in f for f in failures))

    def test_light_accent_only_fails(self):
        # Only the light-mode accent value present -- proves the dark
        # block is missing, not just a stray reference.
        markup = GOOD_HTML.replace("#3fd4c8", "")
        failures = cgo.check_file_from_markup(markup)
        self.assertTrue(any("dark accent" in f for f in failures))


class TestOGCompleteness(unittest.TestCase):
    def test_all_required_tags_flagged_when_absent(self):
        failures = cgo.check_file_from_markup(BARE_HTML)
        og_failures = [f for f in failures if f.startswith("OG:")]
        self.assertEqual(len(og_failures), len(cgo.REQUIRED_META))

    def test_none_flagged_when_all_present(self):
        failures = cgo.check_file_from_markup(GOOD_HTML)
        og_failures = [f for f in failures if f.startswith("OG:")]
        self.assertEqual(og_failures, [])


class TestPyTemplateExtraction(unittest.TestCase):
    def test_extracts_triple_quoted_page_head(self):
        py_source = (
            "PAGE_HEAD = \"\"\"" + GOOD_HTML + "\"\"\"\n"
            "PAGE_TAIL = \"\"\"</body></html>\"\"\"\n"
        )
        extracted = cgo.extract_markup_from_text(py_source, is_python=True)
        self.assertIn("og:site_name", extracted)
        self.assertIn("data-theme-choice", extracted)


if __name__ == "__main__":
    unittest.main()
