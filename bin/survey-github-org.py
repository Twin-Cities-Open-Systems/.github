#!/usr/bin/env python3
"""survey-github-org.py -- fill the External Survey Methodology template
for a GitHub org or user, from public/authenticated-visible data only.

See human-execution-engine/docs/guides/EXTERNAL_SURVEY_METHODOLOGY.md
for the five dimensions this report is structured around. This is the
GitHub-specific implementation of that methodology, not the
methodology itself.

Usage:
  survey-github-org.py OWNER [--top N] [--out FILE]

  --top N     how many repos to inspect in depth for governance/tooling
              signals (default 8, most-recently-pushed first)
  --out FILE  write the report there instead of stdout
"""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone


def gh(*args, check=True):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if check and out.returncode != 0:
        return None
    return out.stdout


def gh_json(*args):
    out = gh(*args)
    if out is None:
        return None
    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return None


def file_exists(owner: str, repo: str, path: str) -> bool:
    out = subprocess.run(
        ["gh", "api", f"repos/{owner}/{repo}/contents/{path}"],
        capture_output=True, text=True,
    )
    return out.returncode == 0


def days_ago(iso_ts: str) -> int:
    dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - dt).days


def survey(owner: str, top_n: int) -> str:
    lines = []
    lines.append(f"# External Survey: {owner}")
    lines.append(f"\nGenerated {datetime.now(timezone.utc).strftime('%Y-%m-%d')} via survey-github-org.py. "
                 f"Public/authenticated-visible GitHub data only -- unknowns are stated, not omitted.\n")

    # Is this an org or a user?
    org_info = gh_json("api", f"orgs/{owner}")
    entity_type = "organization"
    if org_info is None:
        user_info = gh_json("api", f"users/{owner}")
        entity_type = "user"
        if user_info is None:
            return f"# {owner}\n\nNot found -- neither an org nor a user at this login."
        info = user_info
    else:
        info = org_info

    # --- 1. Identity & scale ---
    lines.append("## 1. Identity & scale\n")
    lines.append(f"- **Type:** {entity_type}")
    lines.append(f"- **Name:** {info.get('name') or '(none set)'}")
    lines.append(f"- **Created:** {info.get('created_at', 'unknown')[:10]}")
    lines.append(f"- **Public repos:** {info.get('public_repos', 'unknown')}")
    if entity_type == "organization":
        lines.append(f"- **Public members visible:** "
                      f"{len(gh_json('api', f'orgs/{owner}/members', '--paginate') or []) or 'unknown (may be 0 or hidden)'}")
    lines.append(f"- **Blog/website:** {info.get('blog') or '(none set)'}")

    repos_raw = gh("api", f"{'orgs' if entity_type == 'organization' else 'users'}/{owner}/repos",
                    "--paginate", "-q", ".[] | {name, fork, archived, private, language, pushed_at, stargazers_count}")
    repo_list = []
    if repos_raw:
        for line in repos_raw.strip().split("\n"):
            if line:
                repo_list.append(json.loads(line))
    lines.append(f"- **Repos actually enumerable:** {len(repo_list)} "
                 f"(forks: {sum(1 for r in repo_list if r['fork'])}, "
                 f"archived: {sum(1 for r in repo_list if r['archived'])})")
    langs = {}
    for r in repo_list:
        if r.get("language"):
            langs[r["language"]] = langs.get(r["language"], 0) + 1
    if langs:
        top_langs = sorted(langs.items(), key=lambda x: -x[1])[:5]
        lines.append(f"- **Top languages:** {', '.join(f'{l} ({c})' for l, c in top_langs)}")

    # --- 2. Governance & documentation ---
    lines.append("\n## 2. Governance & documentation\n")
    has_dot_github = file_exists(owner, ".github", "README.md") or any(r["name"] == ".github" for r in repo_list)
    lines.append(f"- **Has a `.github` org-config repo:** {'yes' if has_dot_github else 'no / not found'}")
    if has_dot_github:
        has_profile = file_exists(owner, ".github", "profile/README.md")
        lines.append(f"  - Org profile README (`profile/README.md`): {'yes' if has_profile else 'no'}")
        has_default_codeowners = file_exists(owner, ".github", "CODEOWNERS") or file_exists(owner, ".github", ".github/CODEOWNERS")
        lines.append(f"  - Org-default CODEOWNERS: {'yes' if has_default_codeowners else 'no'}")

    # --- 3. Access & visibility ---
    lines.append("\n## 3. Access & visibility\n")
    lines.append(f"- **Visibility of this survey:** public/authenticated-visible repos only -- "
                 f"private repo count is NOT knowable from outside and is not estimated here.")
    lines.append(f"- **{len(repo_list)} public repos enumerated** via the API; if this org has private "
                 f"repos, they don't appear anywhere in this report.")

    # --- 4 & 5. Tooling/process + activity, per top-N most-recently-pushed repos ---
    lines.append(f"\n## 4. Tooling & process signals (top {top_n} repos by recent activity)\n")
    lines.append(f"\n## 5. Activity signals\n")
    top_repos = sorted([r for r in repo_list if not r["fork"] and not r["archived"]],
                        key=lambda r: r.get("pushed_at") or "", reverse=True)[:top_n]

    activity_rows = []
    tooling_rows = []
    for r in top_repos:
        name = r["name"]
        age_days = days_ago(r["pushed_at"]) if r.get("pushed_at") else None
        activity_rows.append(f"| {name} | {age_days}d ago | ★{r.get('stargazers_count', 0)} |")

        has_ci = subprocess.run(
            ["gh", "api", f"repos/{owner}/{name}/contents/.github/workflows"],
            capture_output=True, text=True,
        ).returncode == 0
        has_contributing = file_exists(owner, name, "CONTRIBUTING.md")
        has_codeowners = file_exists(owner, name, "CODEOWNERS") or file_exists(owner, name, ".github/CODEOWNERS")
        has_security = file_exists(owner, name, "SECURITY.md")
        signals = []
        if has_ci: signals.append("CI")
        if has_contributing: signals.append("CONTRIBUTING")
        if has_codeowners: signals.append("CODEOWNERS")
        if has_security: signals.append("SECURITY.md")
        tooling_rows.append(f"| {name} | {', '.join(signals) if signals else '(none found)'} |")

    lines_4 = ["| Repo | Signals found |", "|---|---|"] + tooling_rows
    lines_5 = ["| Repo | Last push | Stars |", "|---|---|---|"] + activity_rows

    # splice tables into their sections (built the headers above before we had data)
    idx4 = lines.index(f"\n## 4. Tooling & process signals (top {top_n} repos by recent activity)\n")
    idx5 = lines.index("\n## 5. Activity signals\n")
    lines[idx4] += "\n" + "\n".join(lines_4)
    lines[idx5] += "\n" + "\n".join(lines_5)

    lines.append("\n## Unknowns\n")
    lines.append("- Private repo count and content: not knowable from outside.")
    lines.append("- Org membership beyond publicly-visible members: not knowable if members have hidden membership.")
    lines.append(f"- Governance/tooling signals checked on {top_n} most-recently-active repos only, "
                 f"not the full set -- older or less-active repos may differ.")

    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("owner")
    ap.add_argument("--top", type=int, default=8)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    report = survey(args.owner, args.top)
    if args.out:
        with open(args.out, "w") as f:
            f.write(report + "\n")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
