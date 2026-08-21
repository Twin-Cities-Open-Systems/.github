#!/usr/bin/env python3
"""create-epic.py -- one command instead of three manual steps.

Before this: creating a real tracked Epic meant (1) gh issue create,
(2) hand-written GraphQL for addSubIssue per sub-issue -- no gh CLI
subcommand exists for this, and (3) gh project item-add. Easy to get
half-done (issue created, never linked to the project; sub-issues
listed in the body as plain text instead of real linked sub-issues --
exactly the "fake sub-issue list" problem fixed in fleet-ops#188).

This wraps all three into one command, self-assigns per the org's
ticket-ownership policy, and reports each step so a human operator can
see what actually happened -- not just "done".

Usage:
  create-epic.py --repo OWNER/REPO --title "Epic: ..." --body-file FILE
                  [--label L1,L2] [--sub-issue OWNER/REPO#N ...]
                  [--project OWNER/NUMBER]

  create-epic.py --repo Twin-Cities-Open-Systems/fleet-ops \\
      --title "Epic: Board Ops" --body-file body.md \\
      --label idea \\
      --sub-issue Twin-Cities-Open-Systems/fleet-ops#200 \\
      --project Twin-Cities-Open-Systems/1
"""
import argparse
import json
import re
import subprocess
import sys


def run(*args, check=True):
    out = subprocess.run(args, capture_output=True, text=True)
    if check and out.returncode != 0:
        raise RuntimeError(f"{' '.join(args)} failed: {out.stderr.strip()}")
    return out.stdout.strip()


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


def issue_node_id(owner: str, repo: str, number: int) -> str:
    q = """
    query($owner: String!, $repo: String!, $number: Int!) {
      repository(owner: $owner, name: $repo) { issue(number: $number) { id } }
    }
    """
    data = gh_graphql(q, owner=owner, repo=repo, number=str(number))
    node = data["repository"]["issue"]
    if node is None:
        raise RuntimeError(f"{owner}/{repo}#{number}: not found")
    return node["id"]


def parse_sub_issue(ref: str):
    # OWNER/REPO#N
    m = re.match(r"^([^/]+)/([^#]+)#(\d+)$", ref)
    if not m:
        raise ValueError(f"--sub-issue must be OWNER/REPO#N, got: {ref}")
    return m.group(1), m.group(2), int(m.group(3))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, help="OWNER/REPO to create the epic issue in")
    ap.add_argument("--title", required=True)
    ap.add_argument("--body-file", required=True)
    ap.add_argument("--label", default="", help="comma-separated label list")
    ap.add_argument("--sub-issue", action="append", default=[], help="OWNER/REPO#N, repeatable")
    ap.add_argument("--project", default="", help="OWNER/NUMBER to add the epic to")
    args = ap.parse_args()

    owner, repo = args.repo.split("/", 1)

    print(f"=== 1. Creating issue in {args.repo} ===")
    create_args = ["gh", "issue", "create", "--repo", args.repo,
                    "--title", args.title, "--body-file", args.body_file,
                    "--assignee", "@me"]
    if args.label:
        create_args += ["--label", args.label]
    url = run(*create_args)
    print(f"  {url}")
    number = int(url.rstrip("/").split("/")[-1])
    parent_id = issue_node_id(owner, repo, number)

    if args.sub_issue:
        print(f"=== 2. Linking {len(args.sub_issue)} sub-issue(s) ===")
        mutation = """
        mutation($issueId: ID!, $subIssueId: ID!) {
          addSubIssue(input: {issueId: $issueId, subIssueId: $subIssueId}) { subIssue { number } }
        }
        """
        for ref in args.sub_issue:
            sub_owner, sub_repo, sub_number = parse_sub_issue(ref)
            try:
                child_id = issue_node_id(sub_owner, sub_repo, sub_number)
                gh_graphql(mutation, issueId=parent_id, subIssueId=child_id)
                print(f"  {ref}: linked")
            except RuntimeError as e:
                print(f"  {ref}: FAILED -- {e}")
    else:
        print("=== 2. No --sub-issue given, skipping ===")

    if args.project:
        proj_owner, proj_number = args.project.split("/", 1)
        print(f"=== 3. Adding to project {args.project} ===")
        out = subprocess.run(
            ["gh", "project", "item-add", proj_number, "--owner", proj_owner, "--url", url],
            capture_output=True, text=True,
        )
        if out.returncode != 0:
            print(f"  FAILED -- {out.stderr.strip()}")
        else:
            print("  added")
    else:
        print("=== 3. No --project given, skipping ===")

    print(f"\nDone: {url}")


if __name__ == "__main__":
    main()
