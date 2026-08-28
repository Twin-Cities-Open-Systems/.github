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
Copies every file from src_dir to dst_dir; for .html files, rewrites:

1. href="/<page>" -> href="/<page>.html" for the known real page set,
   including a real query string if present (careers.html's "Apply"
   links are href="/contact?apply=...&title=..." -- a real gap the first
   version of this script missed, confirmed live 404 on
   lab.tcos.us/contact?apply=ceo&title=...). Root ("/") is left alone --
   index.html already answers it directly.

2. Real cross-domain person/service links (e.g.
   href="https://spencer.media.tcos.us") -> the .lab.tcos.us equivalent.
   Real gap, confirmed live 2026-08-28: lab.tcos.us/people.html pointed
   at spencer.media.tcos.us (real prod) instead of
   spencer.media.lab.tcos.us (real lab mirror), silently bouncing a lab
   visitor out to prod. Known honest limitation: this rewrites
   unconditionally, same as rule 1 -- it does NOT verify the lab mirror
   actually exists for every person/service (unlike blog-hub.html's own
   runtime IS_LAB + fetch check, which can and does mark "not yet
   mirrored to lab" live). A person with no real lab mirror yet would
   get a rewritten link that 404s, not a silent bounce to prod -- an
   honest failure mode, not a hidden one, but still real; revisit if
   this ever produces a live 404.
"""
import re
import shutil
import sys
from pathlib import Path

REAL_PAGES = ["people", "activity", "story", "ir", "careers", "contact"]

_LINK_RE = re.compile(
    r'href="/(' + "|".join(REAL_PAGES) + r')(\?[^"]*)?"'
)

_CROSS_DOMAIN_RE = re.compile(
    r'href="https://([a-z0-9][a-z0-9.-]*)\.tcos\.us([/"])'
)


def _rewrite_cross_domain(match: "re.Match") -> str:
    host, tail = match.group(1), match.group(2)
    if host.endswith(".lab"):
        return match.group(0)
    return f'href="https://{host}.lab.tcos.us{tail}'


def transform_html(text: str) -> str:
    text = _LINK_RE.sub(
        lambda m: f'href="/{m.group(1)}.html{m.group(2) or ""}"', text
    )
    return _CROSS_DOMAIN_RE.sub(_rewrite_cross_domain, text)


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
