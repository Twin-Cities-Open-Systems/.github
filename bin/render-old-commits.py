#!/usr/bin/env python3
"""render-old-commits.py -- one Gold page listing every non-main branch on
origin across the org's repos, with a verdict per branch, so a laptop (or
any checkout) can be cleaned up against a record instead of from memory.

Operator, 2026-09-05: "will need a view/old-commits.html to track all of
these old commits from my laptop" / "I want to do all the laptop clean up
after the new web page for it is live."

Input is the JSON that `collect` writes (this same script, run on a machine
whose ~/git holds the org checkouts): per repo, per origin branch --
ahead/behind main, last commit, the PR that carried it, and a verdict:
  safe to delete   merged PR, or nothing ahead of main, or identical tree
  open PR          an open PR still points at it
  decide           unmerged commits and no PR -- a human looks
Laptop-local branches (no origin twin) are not visible from here; they come
from `hee repo-refresh hygiene --json` on that machine and merge in as a
second input when present.

Usage:
    render-old-commits.py collect --out old-commits.json [--git-root ~/git]
    render-old-commits.py render old-commits.json [--local hygiene.json] --out DIR
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import datetime as dt
import html
import importlib
import json
import pathlib
import subprocess
import sys

GITHUB_ORG = "Twin-Cities-Open-Systems"


def sh(*a, cwd):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True).stdout.strip()


def collect_repo(d: pathlib.Path):
    subprocess.run(["git", "fetch", "-q", "--prune", "origin"], cwd=d, capture_output=True, timeout=120)
    prs: dict[str, list] = {}
    try:
        for p in json.loads(sh("gh", "pr", "list", "--state", "all", "--limit", "300",
                               "--json", "number,headRefName,state,mergedAt", cwd=d) or "[]"):
            prs.setdefault(p["headRefName"], []).append(p)
    except Exception:
        pass
    main_tree = sh("git", "rev-parse", "origin/main^{tree}", cwd=d)
    rows = []
    for ref in sh("git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin", cwd=d).splitlines():
        if "/" not in ref:
            continue
        b = ref.split("/", 1)[1]
        if b in ("main", "HEAD"):
            continue
        ahead = int(sh("git", "rev-list", "--count", f"origin/main..{ref}", cwd=d) or 0)
        behind = int(sh("git", "rev-list", "--count", f"{ref}..origin/main", cwd=d) or 0)
        last = (sh("git", "log", "-1", "--format=%H%x00%cs%x00%s", ref, cwd=d) + "\0\0").split("\0")
        same_tree = sh("git", "rev-parse", f"{ref}^{{tree}}", cwd=d) == main_tree
        pr = sorted(prs.get(b, []), key=lambda p: p["number"])[-1] if prs.get(b) else None
        merged = bool(pr and pr["state"] == "MERGED")
        if merged or ahead == 0 or same_tree:
            verdict = "safe to delete"
        elif pr and pr["state"] == "OPEN":
            verdict = "open PR"
        else:
            verdict = "decide"
        rows.append(dict(branch=b, ahead=ahead, behind=behind, sha=last[0], date=last[1], subject=last[2],
                         pr=pr and pr["number"], pr_state=pr and pr["state"], verdict=verdict))
    rows.sort(key=lambda r: ({"decide": 0, "open PR": 1, "safe to delete": 2}[r["verdict"]], r["date"]))
    return rows


def collect(git_root: pathlib.Path, out: pathlib.Path):
    repos = sorted(p for p in git_root.iterdir()
                   if (p / ".git").exists() and GITHUB_ORG in sh("git", "remote", "get-url", "origin", cwd=p))
    data = {}
    with cf.ThreadPoolExecutor(6) as ex:
        for p, rows in zip(repos, ex.map(collect_repo, repos)):
            if rows:
                data[p.name] = rows
    out.write_text(json.dumps({"generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
                               "host": sh("hostname", cwd="/"), "repos": data}, indent=1) + "\n")
    n = sum(len(v) for v in data.values())
    print(f"OK old-commits: {len(data)} repos, {n} branches -> {out}")


VERDICT_CLASS = {"safe to delete": "ok", "open PR": "warn", "decide": "crit"}


def render(data_path: pathlib.Path, local_path: pathlib.Path | None, out_dir: pathlib.Path):
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    rr = importlib.import_module("render-review")
    data = json.loads(data_path.read_text())
    local = json.loads(local_path.read_text()) if local_path else {}
    repos = data["repos"]
    totals = {"safe to delete": 0, "open PR": 0, "decide": 0}
    parts = []
    parts.append('<style>.oc td,.oc th{padding:4px 8px;vertical-align:top}.oc .ok{color:var(--ok,#2e7d32)}'
                 '.oc .warn{color:var(--warn,#b26a00)}.oc .crit{color:var(--crit,#c62828)}.oc code{font-size:.9em}</style>')
    parts.append(f'<p>Every branch on origin other than <code>main</code>, across {len(repos)} repos, '
                 f'as fetched from <code>{html.escape(data["host"])}</code> at {html.escape(data["generated"])}. '
                 'Verdicts: <b class="ok">safe to delete</b> = merged PR, nothing ahead of main, or identical tree; '
                 '<b class="warn">open PR</b> = a PR still points at it; <b class="crit">decide</b> = unmerged commits and no PR.</p>')
    for repo, rows in repos.items():
        counts = {k: sum(1 for r in rows if r["verdict"] == k) for k in totals}
        for k in totals:
            totals[k] += counts[k]
        parts.append(f'<h2 id="{html.escape(repo)}">{html.escape(repo)} <small>({len(rows)}: '
                     f'<span class="crit">{counts["decide"]} decide</span>, <span class="warn">{counts["open PR"]} open PR</span>, '
                     f'<span class="ok">{counts["safe to delete"]} safe to delete</span>)</small></h2>')
        parts.append('<div style="overflow-x:auto"><table class="oc"><tr><th>verdict</th><th>branch</th><th>ahead/behind</th>'
                     '<th>last commit</th><th>PR</th></tr>')
        base = f"https://github.com/{GITHUB_ORG}/{repo}"
        for r in rows:
            pr = (f'<a href="{base}/pull/{r["pr"]}">#{r["pr"]}</a> {html.escape(str(r["pr_state"]).lower())}' if r["pr"] else "")
            parts.append(f'<tr><td class="{VERDICT_CLASS[r["verdict"]]}">{r["verdict"]}</td>'
                         f'<td><a href="{base}/tree/{html.escape(r["branch"])}"><code>{html.escape(r["branch"])}</code></a></td>'
                         f'<td>+{r["ahead"]} / -{r["behind"]}</td>'
                         f'<td><a href="{base}/commit/{r["sha"]}"><code>{r["sha"][:7]}</code></a> {html.escape(r["date"])} '
                         f'{html.escape(r["subject"][:90])}</td><td>{pr}</td></tr>')
        parts.append('</table></div>')
        for lb in local.get(repo, []):
            parts.append(f'<p class="crit">laptop-local only: <code>{html.escape(lb.get("branch", "?"))}</code> '
                         f'{html.escape(str(lb.get("note", "")))}</p>')
    summary = (f'<p><b>{sum(totals.values())} branches</b>: <span class="crit">{totals["decide"]} decide</span>, '
               f'<span class="warn">{totals["open PR"]} open PR</span>, <span class="ok">{totals["safe to delete"]} safe to delete</span>.</p>')
    body = parts[0] + summary + "".join(parts[1:])
    page = rr.render_file_page(
        str(pathlib.Path(__file__).resolve().parents[1]), "old-commits.html",
        title="old commits -- every non-main branch on origin",
        status_class="browse", status_label="branch audit",
        generated_iso=data["generated"],
        og_description=f'{sum(totals.values())} non-main branches across {len(repos)} TCOS repos, with a cleanup verdict each.',
        og_url="https://view.lab.tcos.us/old-commits.html",
        pretty_html=body, site_name="TCOS View", active_tab="pretty",
        extra_head=rr_gtag())
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "old-commits.html").write_text(page)
    print(f"OK old-commits.html: {sum(totals.values())} branches, {len(repos)} repos -> {out_dir / 'old-commits.html'}")


def rr_gtag() -> str:
    try:
        sys.path.insert(0, str(pathlib.Path.home() / "git/human-execution-engine/library/py"))
        import hee_gtag  # type: ignore
        return hee_gtag.snippet_or_empty()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect"); c.add_argument("--out", required=True, type=pathlib.Path)
    c.add_argument("--git-root", default=pathlib.Path.home() / "git", type=pathlib.Path)
    r = sub.add_parser("render"); r.add_argument("data", type=pathlib.Path)
    r.add_argument("--local", type=pathlib.Path); r.add_argument("--out", required=True, type=pathlib.Path)
    a = ap.parse_args()
    if a.cmd == "collect":
        collect(a.git_root, a.out)
    else:
        render(a.data, a.local, a.out)


if __name__ == "__main__":
    main()
