#!/usr/bin/env python3
"""manage-project.py -- declarative GitHub Projects v2 config.

GitHub has no native "define your Project in a file" mechanism -- this
wraps the real GraphQL API (ProjectV2, views, items) so a YAML file can
be the source of truth instead of clicking through the UI. Idempotent:
running it twice with the same file does nothing the second time.

Requires: `gh` CLI, authenticated, PyYAML.

Usage:
  manage-project.py apply <config.yaml>   # create what's missing, skip what exists
  manage-project.py dump <owner> <number> # print current live state as YAML,
                                           # to seed a config file from reality

Config schema:
  project:
    owner: Org-Name
    number: 1
  views:
    - name: Kanban
      layout: BOARD_LAYOUT   # TABLE_LAYOUT | BOARD_LAYOUT | ROADMAP_LAYOUT
  items:
    - https://github.com/OWNER/REPO/issues/N
    - https://github.com/OWNER/REPO/pull/N
"""
import json
import subprocess
import sys

try:
    import yaml
except ImportError:
    print("Needs PyYAML: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def gh_graphql(query: str, **variables) -> dict:
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for k, v in variables.items():
        args += ["-F", f"{k}={v}"]
    out = subprocess.run(args, capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(f"gh api graphql failed: {out.stderr.strip()}")
    data = json.loads(out.stdout)
    if "errors" in data:
        raise RuntimeError(f"GraphQL errors: {data['errors']}")
    return data["data"]


def get_project(owner: str, number: int) -> dict:
    q = """
    query($owner: String!, $number: Int!) {
      organization(login: $owner) {
        projectV2(number: $number) {
          id
          title
          views(first: 20) { nodes { id name layout } }
          items(first: 100) { nodes { id content { ... on Issue { url } ... on PullRequest { url } } } }
        }
      }
    }
    """
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={q}", "-f", f"owner={owner}", "-F", f"number={number}"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip())
    data = json.loads(out.stdout)
    if "errors" in data:
        raise RuntimeError(str(data["errors"]))
    proj = data["data"]["organization"]["projectV2"]
    if proj is None:
        raise RuntimeError(f"No project #{number} found for org {owner}")
    return proj


def apply_config(path: str):
    cfg = yaml.safe_load(open(path))
    owner = cfg["project"]["owner"]
    number = cfg["project"]["number"]

    live = get_project(owner, number)
    project_id = live["id"]
    print(f"=== {live['title']} (owner={owner} #{number}) ===")

    existing_view_names = {v["name"] for v in live["views"]["nodes"]}
    for view in cfg.get("views", []):
        if view["name"] in existing_view_names:
            print(f"  view '{view['name']}': already exists, skipping")
            continue
        q = """
        mutation($projectId: ID!, $name: String!, $layout: ProjectV2ViewLayout!) {
          createProjectV2View(input: {projectId: $projectId, name: $name, layout: $layout}) {
            projectV2View { name layout }
          }
        }
        """
        gh_graphql(q, projectId=project_id, name=view["name"], layout=view["layout"])
        print(f"  view '{view['name']}' ({view['layout']}): created")

    existing_urls = {
        n["content"]["url"] for n in live["items"]["nodes"] if n.get("content") and n["content"].get("url")
    }
    for url in cfg.get("items", []):
        if url in existing_urls:
            print(f"  item {url}: already present, skipping")
            continue
        out = subprocess.run(
            ["gh", "project", "item-add", str(number), "--owner", owner, "--url", url],
            capture_output=True, text=True,
        )
        if out.returncode != 0:
            print(f"  item {url}: FAILED -- {out.stderr.strip()}")
        else:
            print(f"  item {url}: added")


def dump_config(owner: str, number: int):
    live = get_project(owner, number)
    cfg = {
        "project": {"owner": owner, "number": number, "title": live["title"]},
        "views": [{"name": v["name"], "layout": v["layout"]} for v in live["views"]["nodes"]],
        "items": sorted(
            n["content"]["url"] for n in live["items"]["nodes"] if n.get("content") and n["content"].get("url")
        ),
    }
    print(yaml.safe_dump(cfg, sort_keys=False, width=100))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "apply" and len(sys.argv) == 3:
        apply_config(sys.argv[2])
    elif cmd == "dump" and len(sys.argv) == 4:
        dump_config(sys.argv[2], int(sys.argv[3]))
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
