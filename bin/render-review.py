#!/usr/bin/env python3
"""render-review.py -- rich diff + pretty-print pages, for changes and for
browsing any real file, pretty-printed and hosted locally instead of
relying on github.com's renderer.

Two modes, combinable in one run:

**Change mode** (`--repo`): scans each repo with `git status --short`, and
for every created or modified file (deletions skipped -- nothing to view)
emits one self-contained HTML page with two tabs: a real git-diff view and
a pretty-printed view of the current file.

**Browse mode** (`--browse`): renders every real file under given
directories (or a sensible default set) in a repo, pretty-printed, mirroring
the repo's real directory structure in the output path -- so a file at
`docs/history/PILL_INDEX.md` in `human-execution-engine` lands at
`<out>/human-execution-engine/docs/history/PILL_INDEX.md.html`. The diff tab
still works (shows "no diff" for anything unchanged) -- this isn't a
different renderer, just a different set of files to point it at.

Both modes render Markdown as real HTML (`markdown` package) and everything
else -- YAML, JSON, TOML, Python, shell, and anything else Pygments
recognizes by filename -- as syntax-highlighted source (`pygments`).

Meant to be reusable, not a one-off: re-run this any time there's a batch of
uncommitted changes across one or more repos to review, or a doc tree that
needs a fresh pretty-printed pass, and push the output dir to the view.lab
container alongside the review index.

Usage:
    python3 bin/render-review.py --repo /path/to/repo [--repo ...] \
        --browse /path/to/repo[:subdir1,subdir2,...] [--browse ...] \
        --out DIR
    -> change-mode files: DIR/<repo-name>--<slug>.html (flat), manifest line
       per file (STATUS<TAB>REPO<TAB>PATH<TAB>OUTPUT_FILENAME) on stdout.
    -> browse-mode files: DIR/<repo-name>/<real/relative/path>.html (mirrors
       the repo tree), manifest line per file (browse<TAB>REPO<TAB>PATH<TAB>
       OUTPUT_RELATIVE_PATH) on stdout.
"""

from __future__ import annotations

import argparse
import html
import subprocess
import sys
from pathlib import Path

try:
    import markdown as _markdown
except ImportError:
    _markdown = None

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import get_lexer_for_filename, TextLexer
    from pygments.styles import get_style_by_name
except ImportError:
    highlight = None


# --- real Solarized (Ethan Schoonover's actual palette, via pygments'
# built-in solarized-light/solarized-dark styles -- not a hand-rolled
# approximation) -- Spencer's real complaint: the site's own teal/mono
# accent colors, reused for syntax highlighting, read as "blinding" at
# code-block scale in dark mode. Solarized's whole design point is
# calibrated low-contrast readability, so use the genuine thing instead
# of trying to tune our own. Two variants (light/dark) picked by the
# oper's own theme choice (light/dark/auto, default dark -- the
# .theme-toggle in PAGE_TEMPLATE), same selector pattern as the rest of
# this site's light/dark CSS. ---
if highlight is not None:
    def pygments_theme_css() -> str:
        light = HtmlFormatter(style=get_style_by_name("solarized-light")).get_style_defs(".highlight")
        dark_media_sel = ':root:not([data-theme="light"]) .highlight'
        dark_media = HtmlFormatter(style=get_style_by_name("solarized-dark")).get_style_defs(dark_media_sel)
        dark_explicit_sel = ':root[data-theme="dark"] .highlight'
        dark_explicit = HtmlFormatter(style=get_style_by_name("solarized-dark")).get_style_defs(dark_explicit_sel)
        return (
            light + "\n"
            + '@media (prefers-color-scheme: dark) {\n' + dark_media + "\n}\n"
            + dark_explicit
        )

    PYGMENTS_CSS = pygments_theme_css()
else:
    PYGMENTS_CSS = ""


def sh(args: list[str], cwd: str) -> str:
    return subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, check=False
    ).stdout


def git_status(repo: str) -> list[tuple[str, str]]:
    """Returns [(status, path), ...] -- status is git's 2-char porcelain code."""
    out = sh(["git", "status", "--short"], cwd=repo)
    entries = []
    for line in out.splitlines():
        if not line.strip():
            continue
        status, path = line[:2], line[3:].strip()
        if "->" in path:  # renamed: "old -> new"
            path = path.split("->")[-1].strip()
        if path.endswith("/"):
            # an untracked directory reported as one line -- not a file to
            # render; real files inside it would need their own entries
            continue
        entries.append((status, path))
    return entries


def is_deleted(status: str) -> bool:
    return "D" in status


def is_new(status: str) -> bool:
    return status.strip() == "??" or status.strip() == "A"


def get_diff_html(repo: str, path: str, new: bool) -> str:
    if new:
        raw = sh(["git", "diff", "--no-index", "--", "/dev/null", path], cwd=repo)
    else:
        raw = sh(["git", "diff", "HEAD", "--", path], cwd=repo)
    if not raw.strip():
        return '<p class="empty">No diff -- file staged/tracked with no changes against HEAD.</p>'
    lines = []
    for line in raw.splitlines():
        esc = html.escape(line)
        if line.startswith("+++") or line.startswith("---"):
            cls = "hdr"
        elif line.startswith("@@"):
            cls = "hunk"
        elif line.startswith("+"):
            cls = "add"
        elif line.startswith("-"):
            cls = "del"
        else:
            cls = "ctx"
        lines.append(f'<span class="dl {cls}">{esc}</span>')
    return '<pre class="diff">' + "\n".join(lines) + "</pre>"


# Comment prefix per real file extension -- used only to prepend a real
# source-comment (see get_pretty_html's github_url param), never guessed
# per-language beyond this simple, real mapping.
_COMMENT_PREFIX_BY_EXT = {
    ".yaml": "#", ".yml": "#", ".py": "#", ".sh": "#", ".toml": "#",
    ".js": "//", ".ts": "//", ".rs": "//", ".go": "//", ".c": "//", ".java": "//",
}


def get_pretty_html(repo: str, path: str, github_url: str | None = None) -> str:
    full = Path(repo) / path
    try:
        text = full.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError, IsADirectoryError, OSError) as e:
        return f'<p class="empty">Can\'t render: {html.escape(str(e))}</p>'

    if github_url and not path.endswith(".md"):
        ext = Path(path).suffix
        prefix = _COMMENT_PREFIX_BY_EXT.get(ext, "#")
        text = f"{prefix} source: {github_url}\n\n{text}"

    if path.endswith(".md") and _markdown is not None:
        # codehilite gives fenced code blocks the same real pygments
        # highlighting as standalone source files, not a flat <pre><code> --
        # "normal git markdown style" for a .md with real bash/etc blocks in it.
        extensions = ["fenced_code", "tables", "sane_lists"]
        extension_configs = {}
        if highlight is not None:
            extensions.append("codehilite")
            extension_configs["codehilite"] = {
                "css_class": "highlight", "guess_lang": False, "linenums": False,
            }
        body = _markdown.markdown(
            text, extensions=extensions, extension_configs=extension_configs
        )
        return f'<div class="prose">{body}</div>'

    if highlight is not None:
        try:
            lexer = get_lexer_for_filename(path, stripnl=False)
        except Exception:
            lexer = TextLexer(stripnl=False)
        # style= only matters for get_style_defs() (CSS generation, done
        # once in PYGMENTS_CSS above with both light+dark variants); the
        # token->CSS-class mapping highlight() actually emits here is the
        # same regardless of which style object is passed.
        formatter = HtmlFormatter(style=get_style_by_name("solarized-light"), cssclass="highlight", nowrap=False)
        return highlight(text, lexer, formatter)

    return f"<pre>{html.escape(text)}</pre>"


PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
{extra_head}<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<!-- Real favicon, hosted centrally -- swapping the icon means replacing
     the files at these paths, never editing page HTML. See
     /assets/favicon-manifest.json for available variants. -->
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="icon" type="image/png" sizes="16x16" href="/assets/favicon-16.png">
<link rel="apple-touch-icon" sizes="180x180" href="/assets/favicon-180.png">
<meta property="og:site_name" content="{site_name}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{og_description}">
<meta property="og:type" content="website">
<meta property="og:url" content="{og_url}">
<meta name="twitter:card" content="summary">
<meta name="description" content="{og_description}">
<link rel="canonical" href="{og_url}">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<script>
// Real oper theme choice (light/dark/auto), applied before first paint so
// there's no flash of the wrong theme. Default -- no stored choice yet --
// is dark, not "auto"/OS-preference (Spencer, real request).
(function () {{
  try {{
    var t = localStorage.getItem("tcos-theme") || "dark";
    if (t !== "auto") document.documentElement.setAttribute("data-theme", t);
  }} catch (e) {{
    document.documentElement.setAttribute("data-theme", "dark");
  }}
}})();
</script>
<style>
:root {{
  --ground: #fbfbfa; --surface: #ffffff; --surface-2: #f1f2f0; --line: #e2e4e0;
  --ink: #12181a; --ink-dim: #4c5658; --ink-faint: #7c8688;
  --accent: #0d7d78; --accent-ink: #085e5a; --accent-soft: #e3f3f1;
  --good: #0ca30c; --warning: #b8790a; --serious: #c95a2e; --critical: #d03b3b;
  --good-soft: #e4f5e0; --warning-soft: #fbeecb; --critical-soft: #fbdcdc;
}}
:root:not([data-theme="light"]) {{
  @media (prefers-color-scheme: dark) {{
    --ground: #0b0f0f; --surface: #12181a; --surface-2: #18201f; --line: #263030;
    --ink: #eef2f1; --ink-dim: #a9b6b6; --ink-faint: #6f7d7d;
    --accent: #3fd4c8; --accent-ink: #7fe6dc; --accent-soft: #12302e;
    --good: #4ade4a; --warning: #fab219; --serious: #ec835a; --critical: #ff6161;
    --good-soft: #163019; --warning-soft: #332309; --critical-soft: #3a1414;
  }}
}}
:root[data-theme="dark"] {{
  --ground: #0b0f0f; --surface: #12181a; --surface-2: #18201f; --line: #263030;
  --ink: #eef2f1; --ink-dim: #a9b6b6; --ink-faint: #6f7d7d;
  --accent: #3fd4c8; --accent-ink: #7fe6dc; --accent-soft: #12302e;
  --good: #4ade4a; --warning: #fab219; --serious: #ec835a; --critical: #ff6161;
  --good-soft: #163019; --warning-soft: #332309; --critical-soft: #3a1414;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--ground); color: var(--ink); font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif; font-size: 14.5px; line-height: 1.55; }}
.wrap {{ max-width: 1100px; margin: 0 auto; padding: 28px 22px 60px; }}
.site-bar {{ display: flex; align-items: center; justify-content: space-between; padding-bottom: 14px; margin-bottom: 20px; border-bottom: 1px solid var(--line); }}
.site-logo {{ display: flex; align-items: center; gap: 7px; font-family: "JetBrains Mono", monospace; font-size: 13px; font-weight: 700; color: var(--ink); text-decoration: none; letter-spacing: -0.01em; }}
.site-logo .mark {{ color: var(--accent); font-size: 15px; }}
.site-logo:hover {{ color: var(--accent-ink); }}
.fontsize-toggle {{ display: flex; align-items: center; gap: 6px; }}
.fontsize-toggle .fs-label {{ font-family: ui-monospace, monospace; font-size: 10px; color: var(--ink-faint); cursor: default; user-select: none; }}
.fontsize-toggle .fs-options {{ display: flex; align-items: center; gap: 4px; max-width: 0; overflow: hidden; opacity: 0; transition: max-width .18s ease, opacity .12s ease; }}
.fontsize-toggle:hover .fs-options, .fontsize-toggle:focus-within .fs-options {{ max-width: 200px; opacity: 1; }}
.fontsize-toggle.fs-force-collapsed .fs-options {{ max-width: 0 !important; opacity: 0 !important; }}
.fontsize-btn {{ background: var(--surface-2); border: 1px solid var(--line); color: var(--ink-faint); font-family: ui-monospace, monospace; font-size: 10.5px; font-weight: 700; width: 22px; height: 22px; border-radius: 5px; cursor: pointer; line-height: 1; }}
.fontsize-btn.active {{ background: var(--accent-soft); border-color: var(--accent); color: var(--accent-ink); }}
body[data-fontsize="s"] {{ zoom: 0.875; }}
body[data-fontsize="m"] {{ zoom: 1; }}
body[data-fontsize="l"] {{ zoom: 1.125; }}
body[data-fontsize="xl"] {{ zoom: 1.25; }}
body[data-fontsize="xxl"] {{ zoom: 1.375; }}
.theme-toggle {{ display: flex; align-items: center; gap: 4px; margin-right: 12px; }}
.theme-toggle span {{ font-family: ui-monospace, monospace; font-size: 10px; color: var(--ink-faint); margin-right: 2px; }}
.theme-btn {{ background: var(--surface-2); border: 1px solid var(--line); color: var(--ink-faint); font-family: ui-monospace, monospace; font-size: 9.5px; font-weight: 700; padding: 0 7px; height: 22px; border-radius: 5px; cursor: pointer; line-height: 1; text-transform: uppercase; }}
.theme-btn.active {{ background: var(--accent-soft); border-color: var(--accent); color: var(--accent-ink); }}
.toggles-row {{ display: flex; align-items: center; }}
.eyebrow {{ font-family: "JetBrains Mono", monospace; font-size: 11.5px; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); margin: 0 0 6px; }}
h1 {{ font-size: 20px; font-weight: 600; margin: 0 0 4px; font-family: "JetBrains Mono", monospace; word-break: break-all; }}
.meta {{ color: var(--ink-faint); font-size: 12.5px; margin: 0 0 10px; display: flex; align-items: center; flex-wrap: wrap; gap: 10px; row-gap: 4px; }}
.lu-row {{ display: flex; flex-wrap: wrap; gap: 4px 14px; font-family: "JetBrains Mono", monospace; font-size: 11.5px; color: var(--ink-faint); margin: 0 0 18px; }}
.lu-row b {{ color: var(--ink-dim); font-weight: 600; }}
.chip {{ display: inline-flex; padding: 2px 8px; border-radius: 20px; font-size: 11px; font-family: "JetBrains Mono", monospace; font-weight: 600; margin-right: 6px; }}
.chip.new {{ background: var(--good-soft); color: var(--good); }}
.chip.mod {{ background: var(--warning-soft); color: var(--warning); }}
.chip.browse {{ background: var(--accent-soft); color: var(--accent-ink); }}
.tabs {{ display: flex; gap: 4px; margin-bottom: 14px; border-bottom: 1px solid var(--line); }}
.tab {{ font-family: "JetBrains Mono", monospace; font-size: 12.5px; padding: 9px 16px; cursor: pointer; color: var(--ink-faint); border-bottom: 2px solid transparent; user-select: none; }}
.tab.active {{ color: var(--accent-ink); border-bottom-color: var(--accent); }}
.panel {{ display: none; }}
.panel.active {{ display: block; }}
.empty {{ color: var(--ink-faint); font-style: italic; padding: 20px; }}
pre.diff {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 0; overflow-x: auto; font-size: 12.5px; margin: 0; }}
.dl {{ display: block; padding: 1px 16px; font-family: "JetBrains Mono", monospace; white-space: pre; }}
.dl.add {{ background: var(--good-soft); color: color-mix(in srgb, var(--good) 70%, var(--ink)); }}
.dl.del {{ background: var(--critical-soft); color: color-mix(in srgb, var(--critical) 70%, var(--ink)); }}
.dl.hdr {{ color: var(--ink-faint); font-weight: 600; }}
.dl.hunk {{ color: var(--accent-ink); background: var(--accent-soft); }}
.dl.ctx {{ color: var(--ink-dim); }}
.highlight {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; overflow-x: auto; font-size: 12.5px; line-height: 1.5; }}
.highlight pre {{ margin: 0; font-family: "JetBrains Mono", monospace; }}

/* "Normal git markdown style" -- github-flavored-markdown proportions and
   spacing (headers with a bottom rule, tight list spacing, fenced code
   blocks that reuse the real pygments highlight above), themed to this
   site's own palette rather than GitHub's colors. */
.prose {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 24px 32px; max-width: 80ch; font-size: 14.5px; line-height: 1.6; }}
.prose > *:first-child {{ margin-top: 0; }}
.prose h1, .prose h2, .prose h3, .prose h4 {{ color: var(--ink); font-weight: 600; margin: 24px 0 16px; }}
.prose h1 {{ font-size: 1.7em; padding-bottom: 0.3em; border-bottom: 1px solid var(--line); }}
.prose h2 {{ font-size: 1.35em; padding-bottom: 0.3em; border-bottom: 1px solid var(--line); }}
.prose h3 {{ font-size: 1.1em; }}
.prose h4 {{ font-size: 1em; }}
.prose p, .prose ul, .prose ol {{ margin: 0 0 14px; }}
.prose li {{ margin: 3px 0; }}
.prose li > p {{ margin: 8px 0; }}
.prose a {{ color: var(--accent-ink); text-decoration: none; }}
.prose a:hover {{ text-decoration: underline; }}
.prose code {{ background: var(--surface-2); padding: 1px 6px; border-radius: 4px; font-size: 0.88em; font-family: "JetBrains Mono", monospace; }}
.prose pre {{ background: var(--surface-2); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; overflow-x: auto; margin: 0 0 16px; }}
.prose pre code {{ background: none; padding: 0; font-size: 0.85em; }}
.prose pre.highlight, .prose div.highlight {{ background: var(--surface-2); border: 1px solid var(--line); border-radius: 8px; padding: 14px 16px; overflow-x: auto; margin: 0 0 16px; }}
.prose div.highlight pre {{ background: none; border: none; padding: 0; margin: 0; }}
.prose table {{ border-collapse: collapse; margin: 0 0 16px; font-size: 0.92em; }}
.prose th {{ background: var(--surface-2); font-weight: 600; }}
.prose th, .prose td {{ border: 1px solid var(--line); padding: 6px 12px; }}
.prose blockquote {{ border-left: 3px solid var(--accent); margin: 0 0 16px; padding: 2px 16px; color: var(--ink-dim); }}
.prose blockquote > *:last-child {{ margin-bottom: 0; }}
.prose hr {{ border: none; border-top: 1px solid var(--line); margin: 24px 0; }}
.prose img {{ max-width: 100%; }}
{pygments_css}
.back {{ display: inline-block; margin-top: 20px; font-family: "JetBrains Mono", monospace; font-size: 12px; color: var(--ink-dim); text-decoration: none; }}

/* GitHub-style hover-card on owner/repo#123 references -- real data via
   a live fetch() to api.github.com on hover, not embedded at generation
   time (see bin/render-review.py's module docstring for the tradeoff:
   always-current, but capped at 60 unauthenticated requests/hr per
   client IP -- fine for one person reviewing, not for a page under
   heavy simultaneous traffic). */
.xref {{ color: var(--accent-ink); text-decoration: none; border-bottom: 1px dotted color-mix(in srgb, var(--accent) 50%, transparent); cursor: help; }}
.xref:hover {{ border-bottom-style: solid; }}
.xref-card {{
  position: fixed; z-index: 1000; display: none;
  width: 320px; max-width: calc(100vw - 24px);
  background: var(--surface); border: 1px solid var(--line); border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.18);
  padding: 12px 14px; font-size: 12.5px; color: var(--ink-dim);
}}
.xref-card.show {{ display: block; }}
.xref-card .xc-repo {{ font-family: "JetBrains Mono", monospace; font-size: 11px; color: var(--ink-faint); margin-bottom: 4px; }}
.xref-card .xc-title {{ color: var(--ink); font-weight: 600; font-size: 13.5px; margin-bottom: 6px; line-height: 1.35; }}
.xref-card .xc-state {{ display: inline-flex; align-items: center; gap: 5px; font-family: "JetBrains Mono", monospace; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 20px; margin-right: 6px; }}
.xref-card .xc-state.open {{ background: var(--good-soft); color: var(--good); }}
.xref-card .xc-state.closed {{ background: var(--critical-soft); color: var(--critical); }}
.xref-card .xc-state.merged {{ background: var(--accent-soft); color: var(--accent-ink); }}
.xref-card .xc-labels {{ margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }}
.xref-card .xc-label {{ font-size: 10.5px; font-family: "JetBrains Mono", monospace; padding: 1px 7px; border-radius: 20px; font-weight: 600; }}
.xref-card .xc-meta {{ margin-top: 8px; font-size: 11px; color: var(--ink-faint); }}
.xref-card .xc-err {{ color: var(--ink-faint); font-style: italic; }}
.back:hover {{ color: var(--accent-ink); }}
</style>
</head>
<body>
<div class="wrap">
  <div class="site-bar">
    <a href="/" class="site-logo"><span class="mark">&#9670;</span> {site_name}</a>
    <div class="toggles-row">
      <div class="theme-toggle">
        <span>Theme</span>
        <button class="theme-btn" data-theme-choice="light" type="button">Light</button>
        <button class="theme-btn" data-theme-choice="dark" type="button">Dark</button>
        <button class="theme-btn" data-theme-choice="auto" type="button">Auto</button>
      </div>
      <div class="fontsize-toggle">
        <span class="fs-label" tabindex="0">Aa</span>
        <div class="fs-options">
          <button class="fontsize-btn" data-size="s" type="button">S</button>
          <button class="fontsize-btn" data-size="m" type="button">M</button>
          <button class="fontsize-btn" data-size="l" type="button">L</button>
          <button class="fontsize-btn" data-size="xl" type="button">XL</button>
          <button class="fontsize-btn" data-size="xxl" type="button">XXL</button>
        </div>
      </div>
    </div>
  </div>
  <p class="eyebrow">{repo} &middot; {status_label}</p>
  <h1>{path}</h1>
  <p class="meta"><span class="chip {status_class}">{status_label}</span></p>
  <div class="lu-row">
    <span><b>lu:</b> <time class="lu-iso" datetime="{generated_iso}">{generated_iso}</time> &middot; <span class="lu-human"></span> &middot; <span class="lu-delta"></span></span>
    <span><b>commit:</b> {commit_info}</span>
    <span><b>license:</b> {license_info}</span>
  </div>

  <div class="tabs">
    <div class="tab{diff_active}" data-tab="diff">Diff</div>
    <div class="tab{pretty_active}" data-tab="pretty">Pretty</div>
  </div>
  <div class="panel{diff_active}" id="panel-diff">{diff_html}</div>
  <div class="panel{pretty_active}" id="panel-pretty">{pretty_html}</div>

  <a class="back" href="javascript:window.close()">&larr; close tab</a>
</div>
<div class="xref-card" id="xref-card"></div>
<script>
document.querySelectorAll(".tab").forEach(function (t) {{
  t.addEventListener("click", function () {{
    document.querySelectorAll(".tab").forEach(function (x) {{ x.classList.remove("active"); }});
    document.querySelectorAll(".panel").forEach(function (x) {{ x.classList.remove("active"); }});
    t.classList.add("active");
    document.getElementById("panel-" + t.dataset.tab).classList.add("active");
  }});
}});

(function () {{
  var FS_KEY = "tcos-fontsize";
  function applyFontsize(size) {{
    document.body.setAttribute("data-fontsize", size);
    document.querySelectorAll(".fontsize-btn").forEach(function (b) {{
      b.classList.toggle("active", b.dataset.size === size);
    }});
  }}
  var savedSize = "m";
  try {{ savedSize = localStorage.getItem(FS_KEY) || "m"; }} catch (e) {{}}
  applyFontsize(savedSize);
  document.querySelectorAll(".fontsize-btn").forEach(function (b) {{
    b.addEventListener("click", function () {{
      try {{ localStorage.setItem(FS_KEY, b.dataset.size); }} catch (e) {{}}
      applyFontsize(b.dataset.size);
      b.blur();
      // Real fix, 2026-08-30: :hover alone keeps .fs-options expanded
      // after a click, since the cursor is still sitting over the
      // widget -- force-collapse it, then let normal hover/focus-within
      // behavior resume once the cursor actually leaves.
      var toggle = b.closest(".fontsize-toggle");
      if (toggle) {{
        toggle.classList.add("fs-force-collapsed");
        toggle.addEventListener("mouseleave", function onLeave() {{
          toggle.classList.remove("fs-force-collapsed");
          toggle.removeEventListener("mouseleave", onLeave);
        }});
      }}
    }});
  }});
}})();

(function () {{
  // Theme buttons -- the actual data-theme attribute was already set (or
  // deliberately left unset for "auto") by the no-flash script in <head>;
  // this just wires up the buttons and reflects the real current choice,
  // defaulting the *displayed active button* to "dark" the same way the
  // head script defaults the real applied theme.
  var TH_KEY = "tcos-theme";
  function markActive(choice) {{
    document.querySelectorAll(".theme-btn").forEach(function (b) {{
      b.classList.toggle("active", b.dataset.themeChoice === choice);
    }});
  }}
  var saved = "dark";
  try {{ saved = localStorage.getItem(TH_KEY) || "dark"; }} catch (e) {{}}
  markActive(saved);
  document.querySelectorAll(".theme-btn").forEach(function (b) {{
    b.addEventListener("click", function () {{
      var choice = b.dataset.themeChoice;
      try {{ localStorage.setItem(TH_KEY, choice); }} catch (e) {{}}
      if (choice === "auto") {{
        document.documentElement.removeAttribute("data-theme");
      }} else {{
        document.documentElement.setAttribute("data-theme", choice);
      }}
      markActive(choice);
    }});
  }});
}})();

(function () {{
  // "lu:" (last-updated) widget -- real ISO timestamp is server-rendered
  // and always present even with JS off; this fills in the viewer's own
  // local-time rendering and a live ticking delta on top of it.
  var isoEl = document.querySelector(".lu-iso");
  if (!isoEl) return;
  var generated = new Date(isoEl.getAttribute("datetime"));
  var humanEl = document.querySelector(".lu-human");
  var deltaEl = document.querySelector(".lu-delta");
  if (humanEl) {{
    humanEl.textContent = generated.toLocaleString(undefined, {{
      dateStyle: "medium", timeStyle: "short"
    }});
  }}
  function renderDelta() {{
    if (!deltaEl) return;
    var ms = Date.now() - generated.getTime();
    var mins = Math.floor(ms / 60000);
    var label;
    if (mins < 1) label = "just now";
    else if (mins < 60) label = mins + "m ago";
    else if (mins < 60 * 24) label = Math.floor(mins / 60) + "h" + (mins % 60) + "m ago";
    else label = Math.floor(mins / (60 * 24)) + "d ago";
    deltaEl.textContent = label;
  }}
  renderDelta();
  setInterval(renderDelta, 30000);
}})();

(function () {{
  // GitHub-style hover-card on real owner/repo#N references. Text-node-only
  // DOM walk (never touches innerHTML) so it can't corrupt the pygments
  // highlight spans or markdown-rendered tags it runs alongside.
  var XREF_RE = /\b([\w.-]+\/[\w.-]+)#(\d+)\b/g;
  var SCOPE_SELECTOR = ".prose, .dl, .highlight, .meta, .empty, .note, td, li, p";
  var cache = {{}};
  var card = document.getElementById("xref-card");
  var hideTimer = null;

  function linkifyTextNode(node) {{
    var text = node.nodeValue;
    XREF_RE.lastIndex = 0;
    if (!XREF_RE.test(text)) return;
    XREF_RE.lastIndex = 0;
    var frag = document.createDocumentFragment();
    var last = 0, m;
    while ((m = XREF_RE.exec(text))) {{
      if (m.index > last) frag.appendChild(document.createTextNode(text.slice(last, m.index)));
      var span = document.createElement("span");
      span.className = "xref";
      span.dataset.repo = m[1];
      span.dataset.num = m[2];
      span.textContent = m[0];
      frag.appendChild(span);
      last = m.index + m[0].length;
    }}
    if (last < text.length) frag.appendChild(document.createTextNode(text.slice(last)));
    node.parentNode.replaceChild(frag, node);
  }}

  function walk(root) {{
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null);
    var nodes = [];
    var n;
    while ((n = walker.nextNode())) nodes.push(n);
    nodes.forEach(linkifyTextNode);
  }}

  document.querySelectorAll(SCOPE_SELECTOR).forEach(function (el) {{ walk(el); }});

  function stateInfo(issue) {{
    if (issue.pull_request) {{
      if (issue.pull_request.merged_at) return {{ cls: "merged", label: "merged" }};
      return issue.state === "open" ? {{ cls: "open", label: "open PR" }} : {{ cls: "closed", label: "closed PR" }};
    }}
    return issue.state === "open" ? {{ cls: "open", label: "open" }} : {{ cls: "closed", label: "closed" }};
  }}

  function renderCard(key, data) {{
    if (data.error) {{
      card.innerHTML = '<div class="xc-repo">' + key + '</div><div class="xc-err">' + data.error + "</div>";
      return;
    }}
    var st = stateInfo(data);
    var labels = (data.labels || []).map(function (l) {{
      var bg = "#" + l.color, fg = "#12181a";
      return '<span class="xc-label" style="background:' + bg + ";color:" + fg + '">' + l.name + "</span>";
    }}).join("");
    card.innerHTML =
      '<div class="xc-repo">' + key + '</div>' +
      '<div class="xc-title">' + data.title.replace(/</g, "&lt;") + '</div>' +
      '<span class="xc-state ' + st.cls + '">' + st.label + '</span>' +
      '<span class="xc-meta">@' + data.user.login + '</span>' +
      (labels ? '<div class="xc-labels">' + labels + '</div>' : "");
  }}

  function showCardNear(el) {{
    var r = el.getBoundingClientRect();
    var top = r.bottom + 6;
    var left = r.left;
    if (left + 320 > window.innerWidth - 12) left = window.innerWidth - 332;
    if (top + 160 > window.innerHeight) top = r.top - 6 - 160;
    card.style.top = Math.max(8, top) + "px";
    card.style.left = Math.max(8, left) + "px";
    card.classList.add("show");
  }}

  document.addEventListener("mouseover", function (e) {{
    var el = e.target.closest && e.target.closest(".xref");
    if (!el) return;
    clearTimeout(hideTimer);
    var repo = el.dataset.repo, num = el.dataset.num;
    var key = repo + "#" + num;
    showCardNear(el);
    if (cache[key]) {{
      renderCard(key, cache[key]);
      return;
    }}
    card.innerHTML = '<div class="xc-repo">' + key + '</div><div class="xc-err">loading&hellip;</div>';
    fetch("https://api.github.com/repos/" + repo + "/issues/" + num, {{ headers: {{ Accept: "application/vnd.github+json" }} }})
      .then(function (res) {{
        if (res.status === 403) throw new Error("rate-limited (60/hr unauthenticated) -- try again later");
        if (res.status === 404) throw new Error("not found");
        if (!res.ok) throw new Error("GitHub API error " + res.status);
        return res.json();
      }})
      .then(function (data) {{
        cache[key] = data;
        renderCard(key, data);
      }})
      .catch(function (err) {{
        var data = {{ error: err.message }};
        cache[key] = data;
        renderCard(key, data);
      }});
  }});

  document.addEventListener("mouseout", function (e) {{
    var el = e.target.closest && e.target.closest(".xref");
    if (!el) return;
    hideTimer = setTimeout(function () {{ card.classList.remove("show"); }}, 150);
  }});
  card.addEventListener("mouseenter", function () {{ clearTimeout(hideTimer); }});
  card.addEventListener("mouseleave", function () {{ card.classList.remove("show"); }});
}})();
</script>
</body>
</html>
"""


def slug_for(repo_name: str, path: str) -> str:
    # A leading dot (e.g. the ".github" repo) makes the output a dotfile --
    # served fine directly, but hidden from directory listings and just
    # awkward to link to. Strip it for the slug only.
    safe_repo = repo_name.lstrip(".") or repo_name
    safe = path.replace("/", "-")
    return f"{safe_repo}--{safe}.html"


def real_repo_name(repo: str) -> str:
    resolved = Path(repo).resolve()
    if ".claude/worktrees" in str(resolved):
        return Path(str(resolved).split("/.claude/worktrees/")[0]).name
    return resolved.name


def github_repo_url(repo: str) -> str:
    """https://github.com/<org>/<repo> for a checkout -- the org's own
    convention (every repo lives at github.com/GITHUB_ORG/<dirname>)."""
    name = real_repo_name(repo)
    return f"https://github.com/{GITHUB_ORG}/{name.lstrip('.') or name}"


def get_commit_info(repo: str, path: str, is_new: bool) -> str:
    """Real commit SHA this page's content reflects, or an honest
    'uncommitted' label -- never a fabricated/assumed commit. The SHA is
    a link to the commit on GitHub (operator, 2026-09-05: "commit has no
    link"); the uncommitted labels stay plain text, there is nothing to
    link to yet."""
    full_sha = sh(["git", "rev-parse", "HEAD"], cwd=repo).strip()
    head_sha = full_sha[:7]
    if not head_sha:
        return "no commits yet"
    if is_new:
        return f"new, uncommitted (HEAD {head_sha})"
    dirty = sh(["git", "status", "--porcelain", "--", path], cwd=repo).strip()
    if dirty:
        return f"uncommitted changes (HEAD {head_sha})"
    return f'<a href="{github_repo_url(repo)}/commit/{full_sha}">{head_sha}</a>'


_LICENSE_CACHE: dict[str, str] = {}

# Real signature strings from each license's own first lines -- detect by
# content, not filename alone (a LICENSE file's actual text is the only
# honest source; the name alone doesn't tell you which one). Order matters:
# check more specific/longer signatures before generic ones.
_LICENSE_SIGNATURES = [
    ("GNU GENERAL PUBLIC LICENSE\n                       Version 3", "GPL-3.0"),
    ("GNU GENERAL PUBLIC LICENSE\n                       Version 2", "GPL-2.0"),
    ("GNU AFFERO GENERAL PUBLIC LICENSE", "AGPL-3.0"),
    ("GNU LESSER GENERAL PUBLIC LICENSE", "LGPL"),
    ("Apache License\n                           Version 2.0", "Apache-2.0"),
    ("MIT License", "MIT"),
    ("BSD 3-Clause", "BSD-3-Clause"),
    ("BSD 2-Clause", "BSD-2-Clause"),
]


def detect_license(repo: str) -> str:
    """Real lookup against the repo's own LICENSE file -- not a hardcoded
    assumption, since it can genuinely change or differ per repo."""
    key = str(Path(repo).resolve())
    if key in _LICENSE_CACHE:
        return _LICENSE_CACHE[key]

    root = Path(key)
    result = "no LICENSE file found"
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        candidate = root / name
        if candidate.is_file():
            try:
                head = candidate.read_text(encoding="utf-8", errors="replace")[:2000]
            except OSError:
                head = ""
            for sig, label in _LICENSE_SIGNATURES:
                if sig in head:
                    result = label
                    break
            else:
                result = "LICENSE file present, type not recognized"
            break

    _LICENSE_CACHE[key] = result
    return result


# The org-wide license, for any repo that carries no LICENSE of its own.
# Operator, 2026-09-05: "we need to make sure there is always a link to
# our gpl in tcos/.github". The file is the canonical GPL-3.0 text.
ORG_LICENSE_REPO = ".github"
ORG_LICENSE_LABEL = "GPL-3.0"


def license_link(repo: str) -> str:
    """detect_license as footer HTML: the repo's own LICENSE, linked, when
    it has one; otherwise the org-wide LICENSE, linked and labeled as
    such -- never an unlinked "no LICENSE file found"."""
    label = detect_license(repo)
    root = Path(repo).resolve()
    for name in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING"):
        if (root / name).is_file():
            return f'<a href="{github_repo_url(repo)}/blob/main/{name}">{html.escape(label)}</a>'
    org_url = f"https://github.com/{GITHUB_ORG}/{ORG_LICENSE_REPO}/blob/main/LICENSE"
    return f'<a href="{org_url}">{ORG_LICENSE_LABEL}</a> (org-wide; this repo carries no LICENSE)'


# Skip vendored/binary/build-output dirs when walking a whole tree -- real
# doc/config content lives outside all of these in every repo checked.
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".wrangler", "dist", "build",
    "venv", ".venv", ".pytest_cache", ".claude", "upstream", "csv-archive",
    "csv-inbox", "csv-failed", "screenshot-archive", "screenshot-inbox",
}
# Skip by extension: binary/signature/compiled/generated-asset formats --
# nothing here is a real "pretty print a doc" candidate.
SKIP_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2",
    ".ttf", ".asc", ".sig", ".pyc", ".so", ".o", ".lock", ".db", ".sqlite",
    ".sqlite3", ".pdf", ".zip", ".tar", ".gz",
}
MAX_BYTES = 512_000  # a real doc/config file; past this it's not "pretty print" material


def iter_tree_files(repo: str, subdirs: list[str]):
    root = Path(repo).resolve()
    bases = [root / s for s in subdirs] if subdirs else [root]
    for base in bases:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
                continue
            if p.suffix.lower() in SKIP_EXTS:
                continue
            try:
                if p.stat().st_size > MAX_BYTES or p.stat().st_size == 0:
                    continue
            except OSError:
                continue
            yield str(p.relative_to(root))


DEFAULT_BROWSE_SUBDIRS_BY_REPO = {
    # only used when a --browse spec gives no explicit subdir list
    "human-execution-engine": [
        "docs", "hee/docs", "hee/cards", "hee/contracts", "prompts", "man",
        "blueprints", "contracts", "rfcs",
    ],
    "github": ["profile", "bin"],  # ".github"'s real_repo_name is de-dotted
    "market-thesis": ["."],
    "market-thesis-news": ["."],
}


GITHUB_ORG = "Twin-Cities-Open-Systems"  # real org name -- used to build real
# https://github.com/<org>/<repo>/blob/main/<path> source-comment links in
# pretty-printed output. All 4 repos this tool handles are confirmed on
# `main` (checked via `gh api repos/<org>/<repo> --jq .default_branch`,
# 2026-08-27) -- not assumed.



def render_file_page(repo: str, path: str, *, title: str, status_class: str, status_label: str,
                     generated_iso: str, og_description: str, og_url: str,
                     diff_html: str = "", pretty_html: str | None = None,
                     commit_info: str | None = None, license_info: str | None = None,
                     site_name: str = "TCOS View", active_tab: str = "diff",
                     github_url: str | None = None, extra_head: str = "") -> str:
    """Assemble one Gold page for a file. This is the function a downstream
    site imports instead of copying PAGE_TEMPLATE -- the GLOSSARY's Gold
    entry: "the source every other surface's Gold code should be ported
    from directly, never hand-copied and re-typed." Real first consumer:
    resume's blog posts (resume#36 item 4 -- they were served as raw
    markdown), which want the Pretty tab up front and their own site
    name; the review/browse pages keep Diff-first and "TCOS View" by
    default, so their output is unchanged."""
    if pretty_html is None:
        pretty_html = get_pretty_html(repo, path, github_url=github_url)
    if commit_info is None:
        commit_info = get_commit_info(repo, path, is_new=False)
    if license_info is None:
        license_info = license_link(repo)
    diff_active = " active" if active_tab == "diff" else ""
    pretty_active = " active" if active_tab == "pretty" else ""
    return PAGE_TEMPLATE.format(
        title=title, repo=real_repo_name(repo).lstrip(".") or real_repo_name(repo), path=path,
        status_class=status_class, status_label=status_label, generated_iso=generated_iso,
        commit_info=commit_info, license_info=license_info,
        og_description=og_description, og_url=og_url,
        diff_html=diff_html, pretty_html=pretty_html, pygments_css=PYGMENTS_CSS,
        site_name=html.escape(site_name), diff_active=diff_active, pretty_active=pretty_active,
        extra_head=(extra_head + "\n") if extra_head else "",
    )

def render_browse(repo: str, subdirs: list[str], out_dir: Path, generated_iso: str):
    repo_name = real_repo_name(repo)
    safe_repo = repo_name.lstrip(".") or repo_name
    if not subdirs:
        subdirs = DEFAULT_BROWSE_SUBDIRS_BY_REPO.get(safe_repo, ["docs"])
    license_info = license_link(repo)
    for path in iter_tree_files(repo, subdirs):
        diff_html = get_diff_html(repo, path, new=False)
        github_url = f"https://github.com/{GITHUB_ORG}/{safe_repo}/blob/main/{path}"
        pretty_html = get_pretty_html(repo, path, github_url=github_url)
        commit_info = get_commit_info(repo, path, is_new=False)
        og_url = f"https://view.lab.tcos.us/files/{safe_repo}/{path}.html"
        page = PAGE_TEMPLATE.format(
            title=f"{path} -- {safe_repo}",
            repo=safe_repo,
            path=path,
            status_class="browse",
            status_label="browse",
            generated_iso=generated_iso,
            commit_info=commit_info,
            license_info=license_info,
            og_description=f"{path} in {safe_repo} -- pretty-printed and diffed by TCOS View.",
            og_url=og_url,
            diff_html=diff_html,
            pretty_html=pretty_html,
            pygments_css=PYGMENTS_CSS,
            site_name="TCOS View", diff_active=" active", pretty_active="", extra_head="",
        )
        out_path = out_dir / safe_repo / path
        out_path = out_path.with_name(out_path.name + ".html")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(page, encoding="utf-8")
        rel_out = str(out_path.relative_to(out_dir))
        print(f"browse\t{safe_repo}\t{path}\t{rel_out}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", action="append", default=[], dest="repos",
                     help="repo to scan for uncommitted changes (change mode)")
    ap.add_argument("--browse", action="append", default=[],
                     help="repo_path[:subdir1,subdir2,...] -- render every real "
                          "file under these dirs, mirroring the repo tree "
                          "(default subdirs per repo if omitted)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if not args.repos and not args.browse:
        ap.error("give at least one --repo or --browse")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    import datetime
    generated_iso = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

    for repo in args.repos:
        repo_name = real_repo_name(repo)
        license_info = license_link(repo)

        for status, path in git_status(repo):
            if is_deleted(status):
                continue
            new = is_new(status)
            diff_html = get_diff_html(repo, path, new)
            pretty_html = get_pretty_html(repo, path)
            commit_info = get_commit_info(repo, path, new)
            slug = slug_for(repo_name, path)
            og_url = f"https://view.lab.tcos.us/diffs/{slug}"
            page = PAGE_TEMPLATE.format(
                title=f"{path} -- {repo_name}",
                repo=repo_name,
                path=path,
                status_class="new" if new else "mod",
                status_label="new" if new else "modified",
                generated_iso=generated_iso,
                commit_info=commit_info,
                license_info=license_info,
                og_description=f"{'New' if new else 'Modified'} file: {path} in {repo_name} -- reviewed via TCOS View.",
                og_url=og_url,
                diff_html=diff_html,
                pretty_html=pretty_html,
                pygments_css=PYGMENTS_CSS,
                site_name="TCOS View", diff_active=" active", pretty_active="", extra_head="",
            )
            (out_dir / slug).write_text(page, encoding="utf-8")
            print(f"{'new' if new else 'mod'}\t{repo_name}\t{path}\t{slug}")

    for spec in args.browse:
        if ":" in spec:
            repo, subdir_str = spec.split(":", 1)
            subdirs = [s for s in subdir_str.split(",") if s]
        else:
            repo, subdirs = spec, []
        render_browse(repo, subdirs, out_dir, generated_iso)

    return 0


if __name__ == "__main__":
    sys.exit(main())
