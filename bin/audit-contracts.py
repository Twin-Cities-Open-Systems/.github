#!/usr/bin/env python3
"""audit-contracts.py -- find every real hee/v1 Contract across the org,
and report which ones are actually ratified vs. still need a vote.

Real trigger (2026-08-21): Spencer's P1 ask -- "scan for contracts that
are not ratified/verified ... so we can vote on them." A manual pass
over the 9 kind:Contract files that existed at the time already found:
3 with no status field at all, 1 using a different status vocabulary
("completed") than ratified/proposed, and the rest split between
verified-ratified and proposed. This tool makes that a rerunnable
check instead of a one-off manual grep.

Scope: only files with apiVersion: hee/v1 and kind: Contract -- the
schema that actually carries spec.status/spec.ratification_evidence.
The older contracts/*.contract.yaml family (no apiVersion/kind header,
governs GPT/Oper/Relay lanes -- see human-execution-engine/contracts/README.md)
is a genuinely different schema with no ratification concept; this tool
lists those separately, unclassified, rather than forcing them into
ratified/proposed buckets they were never designed for.

"Verified" means more than trusting the ratification_evidence string:
for anything claiming status: ratified, this checks that the .asc file
it names actually exists in the repo, live, via the GitHub API -- not
just that the pointer text looks right.

Usage:
  audit-contracts.py [--repo OWNER/REPO ...]  (default: HEE + fleet-ops)
  audit-contracts.py --out FILE
"""
import argparse
import base64
import json
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("Requires pyyaml: pip install pyyaml")

DEFAULT_REPOS = [
    "Twin-Cities-Open-Systems/human-execution-engine",
    "Twin-Cities-Open-Systems/fleet-ops",
]


def gh(*args):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
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


def list_dir(repo: str, path: str):
    """Real directory listing via the API -- returns [] if the path
    doesn't exist in this repo (not every repo has hee/contracts/)."""
    entries = gh_json("api", f"repos/{repo}/contents/{path}")
    if entries is None:
        return []
    return entries


def fetch_text(repo: str, path: str) -> str | None:
    entries = gh_json("api", f"repos/{repo}/contents/{path}")
    if entries is None or "content" not in entries:
        return None
    return base64.b64decode(entries["content"]).decode("utf-8", errors="replace")


def file_exists(repo: str, path: str) -> bool:
    out = subprocess.run(
        ["gh", "api", f"repos/{repo}/contents/{path}"],
        capture_output=True, text=True,
    )
    return out.returncode == 0


def classify(repo: str, dirpath: str, fname: str, text: str) -> dict:
    row = {"repo": repo, "path": f"{dirpath}/{fname}", "class": None, "detail": ""}
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as e:
        row["class"] = "PARSE_ERROR"
        row["detail"] = str(e).splitlines()[0]
        return row

    if not isinstance(doc, dict) or doc.get("kind") != "Contract" or not str(doc.get("apiVersion", "")).startswith("hee/"):
        row["class"] = "NOT_KIND_CONTRACT"
        row["detail"] = f"kind={doc.get('kind') if isinstance(doc, dict) else '?'} -- different schema, not scored here"
        return row

    spec = doc.get("spec", {}) if isinstance(doc.get("spec"), dict) else {}
    status = spec.get("status")
    evidence = spec.get("ratification_evidence")

    if status is None:
        row["class"] = "NO_STATUS_FIELD"
        row["detail"] = "spec.status is entirely absent -- not even declared proposed"
        return row

    if status == "ratified":
        if not evidence or not isinstance(evidence, str):
            row["class"] = "RATIFIED_UNVERIFIED"
            row["detail"] = "status: ratified but no ratification_evidence string present"
            return row
        m = re.match(r"^([^\s]+\.asc)\b", evidence)
        if not m:
            row["class"] = "RATIFIED_UNVERIFIED"
            row["detail"] = f"ratification_evidence doesn't start with a <file>.asc token: {evidence[:80]!r}"
            return row
        evidence_file = m.group(1)
        evidence_path = f"{dirpath}/{evidence_file}"
        if file_exists(repo, evidence_path):
            row["class"] = "RATIFIED_VERIFIED"
            row["detail"] = f"evidence file confirmed live: {evidence_path}"
        else:
            row["class"] = "RATIFIED_UNVERIFIED"
            row["detail"] = f"claims ratified but {evidence_path} does not actually exist -- real inconsistency"
        return row

    if status == "proposed":
        row["class"] = "NEEDS_VOTE"
        req = spec.get("ratification_required_from")
        row["detail"] = f"awaiting: {req}" if req else "awaiting ratification (no ratification_required_from listed)"
        return row

    row["class"] = "OTHER_STATUS"
    row["detail"] = f"status: {status!r} -- different vocabulary than ratified/proposed, needs a human call on how to classify it"
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", action="append", dest="repos", help="OWNER/REPO, repeatable (default: HEE + fleet-ops)")
    ap.add_argument("--out", help="write report here instead of stdout")
    args = ap.parse_args()
    repos = args.repos or DEFAULT_REPOS

    rows = []
    legacy_notes = []
    for repo in repos:
        entries = list_dir(repo, "hee/contracts")
        for e in entries:
            if e.get("type") != "file" or not (e["name"].endswith(".yaml") or e["name"].endswith(".yml")):
                continue
            if e["name"].endswith(".asc"):
                continue
            text = fetch_text(repo, e["path"])
            if text is None:
                rows.append({"repo": repo, "path": e["path"], "class": "FETCH_ERROR", "detail": "could not fetch content"})
                continue
            rows.append(classify(repo, "hee/contracts", e["name"], text))

        # Legacy family: root contracts/*.contract.yaml -- different schema
        # (see human-execution-engine/contracts/README.md), listed but not
        # scored, so it isn't silently invisible to this audit either.
        legacy = list_dir(repo, "contracts")
        for e in legacy:
            if e.get("type") == "file" and ".contract." in e["name"]:
                legacy_notes.append(f"{repo}/{e['path']}")

    order = ["NO_STATUS_FIELD", "RATIFIED_UNVERIFIED", "OTHER_STATUS", "NEEDS_VOTE", "PARSE_ERROR", "FETCH_ERROR", "RATIFIED_VERIFIED", "NOT_KIND_CONTRACT"]
    rows.sort(key=lambda r: (order.index(r["class"]) if r["class"] in order else 99, r["repo"], r["path"]))

    lines = []
    lines.append(f"# Contract ratification audit -- {len(rows)} kind:Contract file(s) across {len(repos)} repo(s)")
    lines.append("")
    counts = {}
    for r in rows:
        counts[r["class"]] = counts.get(r["class"], 0) + 1
    for c in order:
        if c in counts:
            lines.append(f"- {c}: {counts[c]}")
    lines.append("")

    needs_attention = [r for r in rows if r["class"] in ("NO_STATUS_FIELD", "RATIFIED_UNVERIFIED", "OTHER_STATUS", "NEEDS_VOTE", "PARSE_ERROR", "FETCH_ERROR")]
    if needs_attention:
        lines.append("## Needs a vote / a human call")
        lines.append("")
        for r in needs_attention:
            lines.append(f"- **{r['class']}** `{r['repo']}/{r['path']}` -- {r['detail']}")
        lines.append("")

    verified = [r for r in rows if r["class"] == "RATIFIED_VERIFIED"]
    if verified:
        lines.append("## Ratified and verified (evidence file confirmed live)")
        lines.append("")
        for r in verified:
            lines.append(f"- `{r['repo']}/{r['path']}`")
        lines.append("")

    if legacy_notes:
        lines.append("## Legacy contracts/ family (different schema, not scored)")
        lines.append("")
        lines.append("See `contracts/README.md` in human-execution-engine -- these govern GPT/Oper/Relay lanes, not authority/ratification. Listed for visibility only:")
        lines.append("")
        for n in legacy_notes:
            lines.append(f"- `{n}`")
        lines.append("")

    report = "\n".join(lines)
    if args.out:
        with open(args.out, "w") as f:
            f.write(report + "\n")
        print(f"Written to {args.out}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    main()
