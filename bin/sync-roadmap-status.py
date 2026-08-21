#!/usr/bin/env python3
"""sync-roadmap-status.py -- derive a Project item's time-bucket Status
from its real "Target date" field, instead of a human hand-flipping a
dropdown.

Real trigger (2026-08-21): Spencer wants "shit just auto updates the
right shit" when a ticket's date/effort changes -- the ontology being
dogfooded is roadmap's "in future" bucket concept
(https://github.com/Twin-Cities-Open-Systems/roadmap), applied today
using the real wall-clock date as the epoch-0 stand-in, since HEE's own
formal heeEpoch (see human-execution-engine#245's hee-66550.mib) hasn't
been ratified/deployed anywhere real yet -- "since hee-epoch has not
yet arrived, we are simply dogfooding" (Spencer, verbatim).

Reads GitHub's real repo/org-level Issue Type custom fields (Priority,
Target date, Effort -- visible in the issue sidebar's "Fields" section,
a newer GitHub feature, NOT a Projects v2 custom field). An earlier
version of this tool created its own Date/Effort fields directly on the
Project -- wrong: Spencer was already using the real native fields, so
those were deleted rather than left as a confusing second "Date" that
nothing actually populates. This version reads `issueFieldValues`
("Target date" specifically) and writes only the Project's own `Status`
field, which is the one thing this tool should be deriving.

What it does: for every item on a Project whose issue has a real
"Target date" field value, compares that date to today + a near/far
threshold, and sets Project Status to "Near Future Todo" (within
threshold) or "In Future" (beyond it) -- but ONLY when the item's
current Status is already one of Todo/Near Future Todo/In Future.
Never touches "In Progress" or "Done" -- completion state is a human
fact, not something a date implies. Items with no Target date set are
left alone and reported separately, not silently guessed at.

Threshold default (59 days) is the candidate math from roadmap's
README (repo-creation-cadence mean+1stdev) -- flagged there as not yet
confirmed against Spencer's own "commits per period" methodology (see
tcos-www's story.html "The other timeline" section, the real precedent
this same math is meant to formalize). Override with --threshold-days
once a final methodology is picked.

Usage:
  sync-roadmap-status.py OWNER NUMBER [--threshold-days N] [--apply]

  Without --apply: reports what WOULD change, makes no writes (default,
  safe to run anytime). --apply actually updates Status fields.
"""
import argparse
import json
import subprocess
import sys
from datetime import date, datetime, timedelta

DEFAULT_THRESHOLD_DAYS = 59
TIME_BUCKET_STATUSES = {"Todo", "Near Future Todo", "In Future"}


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
          statusField: field(name: "Status") { ... on ProjectV2SingleSelectField { id options { id name } } }
          items(first: 100) {
            nodes {
              id
              content {
                ... on Issue {
                  url
                  title
                  issueFieldValues(first: 20) {
                    nodes {
                      ... on IssueFieldDateValue { value field { ... on IssueFieldDate { name } } }
                    }
                  }
                }
                ... on PullRequest { url title }
              }
              fieldValues(first: 20) {
                nodes {
                  ... on ProjectV2ItemFieldSingleSelectValue { name field { ... on ProjectV2FieldCommon { name } } }
                }
              }
            }
          }
        }
      }
    }
    """
    data = gh_graphql(q, owner=owner, number=number)
    proj = data["organization"]["projectV2"]
    if proj is None:
        raise RuntimeError(f"No project #{number} found for org {owner}")
    return proj


def set_status(project_id: str, item_id: str, status_field_id: str, option_id: str):
    q = """
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $optionId: String!) {
      updateProjectV2ItemFieldValue(input: {
        projectId: $projectId, itemId: $itemId, fieldId: $fieldId,
        value: { singleSelectOptionId: $optionId }
      }) { projectV2Item { id } }
    }
    """
    gh_graphql(q, projectId=project_id, itemId=item_id, fieldId=status_field_id, optionId=option_id)


def target_date_of(content: dict):
    """Pull 'Target date' out of an Issue's real issueFieldValues.
    PRs don't carry issueFieldValues (they're an Issue-only feature) --
    returns None for those, same as "no date set"."""
    for fv in content.get("issueFieldValues", {}).get("nodes", []):
        if fv and fv.get("field", {}).get("name") == "Target date":
            return fv.get("value")
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("owner")
    ap.add_argument("number", type=int)
    ap.add_argument("--threshold-days", type=int, default=DEFAULT_THRESHOLD_DAYS)
    ap.add_argument("--apply", action="store_true", help="actually write Status changes (default: dry-run report only)")
    args = ap.parse_args()

    proj = get_project(args.owner, args.number)
    status_field = proj["statusField"]
    if status_field is None:
        sys.exit("Project has no Status field")
    option_id = {o["name"]: o["id"] for o in status_field["options"]}
    threshold = timedelta(days=args.threshold_days)
    today = date.today()

    changes, no_date, out_of_scope = [], [], []
    for item in proj["items"]["nodes"]:
        content = item.get("content")
        if not content:
            continue
        title = content.get("title", "?")
        url = content.get("url", "?")
        current_status = None
        for fv in item["fieldValues"]["nodes"]:
            if fv and fv.get("field", {}).get("name") == "Status":
                current_status = fv.get("name")

        if current_status not in TIME_BUCKET_STATUSES:
            out_of_scope.append((url, title, current_status))
            continue

        date_val = target_date_of(content)
        if not date_val:
            no_date.append((url, title, current_status))
            continue

        item_date = datetime.fromisoformat(date_val).date()
        target = "Near Future Todo" if (item_date - today) <= threshold else "In Future"
        if target != current_status:
            changes.append((url, title, current_status, target, item["id"]))

    print(f"=== sync-roadmap-status: {args.owner}#{args.number}, threshold={args.threshold_days}d, today={today} ===\n")
    print(f"{len(changes)} item(s) need a Status change:")
    for url, title, cur, target, item_id in changes:
        print(f"  {url}  {cur or '(none)'} -> {target}  [{title[:50]}]")
        if args.apply:
            set_status(proj["id"], item_id, status_field["id"], option_id[target])
            print("    applied")

    print(f"\n{len(no_date)} item(s) in the Todo/Near/In-Future family have no Target date set (left alone, not guessed):")
    for url, title, cur in no_date:
        print(f"  {url}  status={cur}  [{title[:50]}]")

    print(f"\n{len(out_of_scope)} item(s) not in scope (In Progress/Done/other, or a PR -- Target date is Issues-only) -- untouched")

    if not args.apply and changes:
        print("\nDry run -- no writes made. Re-run with --apply to actually update Status.")


if __name__ == "__main__":
    main()
