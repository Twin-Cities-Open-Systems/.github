#!/usr/bin/env python3
"""lab_link_transform.py -- rewrite clean-URL internal links to real
.html-suffixed paths for the lab.tcos.us mirror.

Real trigger (2026-08-28): tcos.us's real nav (index.html etc.) uses
clean URLs (/people, /activity, ...) via Cloudflare Pages' automatic
extension-stripping. lab.tcos.us's busybox-httpd has no such feature
-- confirmed live, "make sure all links work and point to lab, not
live. none work yet." Spencer's own call: ".html suffix in lab is
fine" -- so the real fix is rewriting links for the lab copy, not
building clean-URL support on busybox-httpd.

Usage: lab_link_transform.py <src_dir> <dst_dir>
Copies every file from src_dir to dst_dir; for .html files, rewrites
href="/<page>" -> href="/<page>.html" for the known real page set,
including a real query string if present (careers.html's "Apply"
links are href="/contact?apply=...&title=..." -- a real gap the first
version of this script missed, confirmed live 404 on
lab.tcos.us/contact?apply=ceo&title=...). Root ("/") is left alone --
index.html already answers it directly.
"""
import re
import shutil
import sys
from pathlib import Path

REAL_PAGES = ["people", "activity", "story", "ir", "careers", "contact"]

_LINK_RE = re.compile(
    r'href="/(' + "|".join(REAL_PAGES) + r')(\?[^"]*)?"'
)


def transform_html(text: str) -> str:
    return _LINK_RE.sub(
        lambda m: f'href="/{m.group(1)}.html{m.group(2) or ""}"', text
    )


def main():
    if len(sys.argv) != 3:
        sys.exit("Usage: lab_link_transform.py <src_dir> <dst_dir>")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    changed = 0
    for f in dst.rglob("*.html"):
        original = f.read_text()
        rewritten = transform_html(original)
        if rewritten != original:
            f.write_text(rewritten)
            changed += 1
    print(f"lab_link_transform: rewrote real internal links in {changed} file(s)")


if __name__ == "__main__":
    main()
