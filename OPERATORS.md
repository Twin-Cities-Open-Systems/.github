# Operators — `.github`

Shared conventions (tool-maturity ladder, general workflow) live in
[human-execution-engine's `OPERATOR_GUIDE.md`](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/blob/main/docs/guides/OPERATOR_GUIDE.md).
This doc is only what's specific to the scripts in this repo's `bin/`.

## Epic / Project tooling (the ones you'll actually use day to day)

- **`bin/create-epic.py`** — create a real Epic (issue + linked
  sub-issues + Project board entry) in one command. See the central
  guide's worked example.
- **`bin/manage-project.py`** — declarative Project config.
  `dump OWNER NUMBER` to seed a YAML file from live state, `apply
  FILE` to sync it back (idempotent).

## Org-wide repo scripts

- **`bin/manage-org-repos.sh`** — sync/report across every org repo.
  `--set 1-4,6` to sync specific indexes (by the numbered list it
  prints with no args). **Known bugs, not yet fixed** (fleet-ops#196):
  the "branch protection confirmed" check fires on every repo
  regardless of actual protection status, and it hardcodes `git add
  README.md` when re-committing a popped stash — other stashed file
  changes get silently left uncommitted. Read the script before
  trusting its output blindly.
- **`bin/sync-org-repos.sh`** — simpler multi-repo clone/pull, no
  compliance-branch logic.
- **`bin/relative-link-fixer.sh`** — converts absolute
  `github.com/ORG/...` links in local Markdown to relative
  `../reponame` form. Interactive, prompts per-change. Correct for
  most repo files; **the org profile README (`profile/README.md`) is
  a special case needing 4 `../` levels, not 1** — this tool's
  one-level default would break that specific file (see .github#21's
  fix history for why).
- **`bin/purge_all_repo_codeowners_in_favor_of_org_root.bash`** —
  deletes local `CODEOWNERS` files under `~/git/*` in favor of this
  repo's org-default one. Only deletes **local checkout** files, does
  not commit/push — a human still has to do that per-repo.

## External research

- **`bin/survey-github-org.py OWNER`** — size up an unfamiliar GitHub
  org/repo (identity/scale, governance, tooling signals, activity),
  producing a filled report instead of raw API output. Implements
  human-execution-engine's `EXTERNAL_SURVEY_METHODOLOGY.md`. `--top N`
  controls how many repos get deep-inspected (default 8);
  `--out FILE` writes the report to a file.

## Do not run without reading first

- **`bin/bulk_org_repo_readme_update.bash`** — this is the script that
  produced the org-wide README wipe fixed across 14 repos on
  2026-08-20/21 (unfilled template placeholders overwriting real
  content). Whatever version exists now has not been reviewed or
  fixed since that incident — read it in full and understand exactly
  what it will overwrite before running it again on anything.
