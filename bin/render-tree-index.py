#!/usr/bin/env python3
"""render-tree-index.py -- index pages for view.lab's generated trees.

    render-tree-index.py collect --out tree.json          # ssh pve, list /www/files and /www/diffs on the view container
    render-tree-index.py render tree.json --out DIR       # DIR/files/index.html and DIR/diffs/index.html

busybox httpd serves no directory listing, so https://view.lab.tcos.us/files/
and /diffs/ answered 404 while every page under them was reachable (hee view
--crawl, operator 2026-09-06: "let's fix these all up too"). The trees are
written by review runs (render-review.py), not by a Makefile target, so the
index is built from what the container actually holds -- never from a guess
about what a run should have produced.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import importlib
import json
import pathlib
import subprocess
import sys

VIEW_VMID = 107
TREES = ("files", "diffs")


def collect(out: pathlib.Path, pve_host: str) -> None:
    # -L: on the view container /www/files is a symlink to /www/diffs (one
    # tree, two names; measured 2026-09-06), and find does not descend a
    # symlink without it -- the first run indexed 0 files.
    cmd = " ; ".join(f"find -L /www/{t} -name '*.html' -type f 2>/dev/null | sort" for t in TREES)
    cmd += " ; readlink /www/files || true"
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", pve_host, f"pct exec {VIEW_VMID} -- sh -c \"{cmd}\""],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"CRITICAL collect: {r.stderr.strip() or 'ssh failed'}", file=sys.stderr)
        sys.exit(2)
    trees: dict[str, list[str]] = {t: [] for t in TREES}
    files_link = ""
    for line in r.stdout.splitlines():
        if line.startswith("/www/"):
            for t in TREES:
                prefix = f"/www/{t}/"
                if line.startswith(prefix):
                    trees[t].append(line[len(prefix):])
        elif line.strip():
            files_link = line.strip()  # readlink output: where /www/files really points
    out.write_text(json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "host": pve_host, "trees": trees, "files_link": files_link}, indent=1))
    print("OK collect: " + ", ".join(f"{t} {len(v)}" for t, v in trees.items()) + f" -> {out}")


def group(paths: list[str]) -> dict[str, list[str]]:
    by: dict[str, list[str]] = {}
    for p in paths:
        top = p.split("/", 1)[0] if "/" in p else "(root)"
        by.setdefault(top, []).append(p)
    return by


def render(data_path: pathlib.Path, out_dir: pathlib.Path) -> None:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    rr = importlib.import_module("render-review")
    data = json.loads(data_path.read_text())
    blurb = {
        "files": "every repo file rendered by render-review.py, as of the last review run",
        "diffs": "diff pages from past review runs; regenerated only by a review run",
    }
    same = bool(data.get("files_link"))
    for t in TREES:
        paths = data["trees"].get(t, [])
        note = (f' <b>/files/ and /diffs/ are one tree on the view container</b> '
                f'(<code>/www/files</code> is a symlink to <code>{html.escape(data["files_link"])}</code>); '
                f'the same pages answer under both names.' if same else "")
        parts = ['<style>.ti ul{list-style:none;padding-left:0}.ti li{overflow-wrap:anywhere;padding:2px 0}'
                 '.ti h2{margin-top:1.2em}.ti code{font-size:.9em}</style><div class="ti">']
        parts.append(f'<p>{html.escape(blurb[t])}. {len(paths)} page(s) on the view container '
                     f'at {html.escape(data["generated"])}.{note}</p>')
        for top, items in sorted(group(paths).items()):
            parts.append(f'<h2 id="{html.escape(top)}">{html.escape(top)} <small>({len(items)})</small></h2><ul>')
            for p in items:
                shown = p[len(top) + 1:] if p.startswith(top + "/") else p
                parts.append(f'<li><a href="/{t}/{html.escape(p)}"><code>{html.escape(shown)}</code></a></li>')
            parts.append("</ul>")
        parts.append("</div>")
        page = rr.render_file_page(
            str(pathlib.Path(__file__).resolve().parents[1]), f"{t}/index.html",
            title=("files and diffs -- one view.lab tree" if same else f"{t} -- view.lab tree index"),
            status_class="browse", status_label="tree index",
            generated_iso=data["generated"],
            og_description=f"{len(paths)} generated pages under /{t}/ on view.lab.tcos.us.",
            og_url=f"https://view.lab.tcos.us/{t}/",
            pretty_html="".join(parts), site_name="TCOS View", active_tab="pretty",
            extra_head=gtag())
        (out_dir / t).mkdir(parents=True, exist_ok=True)
        (out_dir / t / "index.html").write_text(page)
        print(f"OK {t}/index.html: {len(paths)} pages -> {out_dir / t / 'index.html'}")


def gtag() -> str:
    try:
        sys.path.insert(0, str(pathlib.Path.home() / "git/human-execution-engine/library/py"))
        import hee_gtag  # type: ignore
        return hee_gtag.snippet_or_empty()
    except Exception:
        return ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect"); c.add_argument("--out", required=True, type=pathlib.Path)
    c.add_argument("--pve-host", default="pve")
    r = sub.add_parser("render"); r.add_argument("data", type=pathlib.Path)
    r.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()
    if a.cmd == "collect":
        collect(a.out, a.pve_host)
    else:
        render(a.data, a.out)


if __name__ == "__main__":
    main()
