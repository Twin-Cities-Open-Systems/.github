#!/usr/bin/env python3
"""Unit tests for lab_link_transform.py -- pure logic, no real infra
needed, so this is what CI can actually verify (the real deploy
targets need real SSH/pve access CI doesn't have -- see
.github/workflows/lab-tools-check.yml for what's honestly in scope)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lab_link_transform import transform_html


class TestTransformHtml(unittest.TestCase):

    def test_rewrites_known_pages(self):
        for page in ["people", "activity", "story", "ir", "careers", "contact", "contracts"]:
            html = f'<a href="/{page}">x</a>'
            self.assertEqual(transform_html(html), f'<a href="/{page}.html">x</a>')

    def test_leaves_root_alone(self):
        html = '<a href="/">home</a>'
        self.assertEqual(transform_html(html), html)

    def test_leaves_unknown_paths_alone(self):
        html = '<a href="/not-a-real-page">x</a>'
        self.assertEqual(transform_html(html), html)

    def test_leaves_already_html_suffixed_alone(self):
        html = '<a href="/people.html">x</a>'
        self.assertEqual(transform_html(html), html)

    def test_multiple_real_links_in_one_page(self):
        html = '<a href="/people">a</a><a href="/activity">b</a><a href="/">c</a>'
        expected = '<a href="/people.html">a</a><a href="/activity.html">b</a><a href="/">c</a>'
        self.assertEqual(transform_html(html), expected)

    def test_rewrites_links_with_query_string(self):
        # real gap, live 404 confirmed 2026-08-28:
        # careers.html's "Apply" links are href="/contact?apply=ceo&title=..."
        html = '<a href="/contact?apply=ceo&amp;title=Chief%20Executive%20Officer">Apply</a>'
        expected = '<a href="/contact.html?apply=ceo&amp;title=Chief%20Executive%20Officer">Apply</a>'
        self.assertEqual(transform_html(html), expected)

    def test_rewrites_cross_domain_person_link(self):
        # Real bug, confirmed live 2026-08-28: lab.tcos.us/people.html
        # pointed at spencer.media.tcos.us (prod) instead of the real
        # spencer.media.lab.tcos.us mirror.
        html = '<a href="https://spencer.media.tcos.us">Media</a>'
        expected = '<a href="https://spencer.media.lab.tcos.us">Media</a>'
        self.assertEqual(transform_html(html), expected)

    def test_rewrites_cross_domain_link_with_path(self):
        html = '<a href="https://spencer.blog.tcos.us/some-post">Post</a>'
        expected = '<a href="https://spencer.blog.lab.tcos.us/some-post">Post</a>'
        self.assertEqual(transform_html(html), expected)

    def test_leaves_already_lab_domain_alone(self):
        html = '<a href="https://spencer.media.lab.tcos.us">Media</a>'
        self.assertEqual(transform_html(html), html)

    def test_leaves_non_tcos_domains_alone(self):
        html = '<a href="https://github.com/Twin-Cities-Open-Systems">GitHub</a>'
        self.assertEqual(transform_html(html), html)

    def test_rewrites_multiple_cross_domain_links(self):
        html = (
            '<a href="https://spencer.blog.tcos.us">Blog</a>'
            '<a href="https://spencer.media.tcos.us">Media</a>'
        )
        expected = (
            '<a href="https://spencer.blog.lab.tcos.us">Blog</a>'
            '<a href="https://spencer.media.lab.tcos.us">Media</a>'
        )
        self.assertEqual(transform_html(html), expected)


if __name__ == "__main__":
    unittest.main()
