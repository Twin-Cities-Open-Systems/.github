# Operators — `.github`

Shared conventions (tool-maturity ladder, general workflow) live in
[human-execution-engine's `OPERATOR_GUIDE.md`](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/blob/main/docs/guides/OPERATOR_GUIDE.md).
This doc is only what's specific to the scripts in this repo's `bin/`.

## Epic / Project tooling (the ones you'll actually use day to day)

- **`bin/create-epic.py`** — create a real Epic (issue + linked
  sub-issues + Project board entry) in one command. See the central
  guide's worked example, or the real run in
  [`examples/create-epic-operator-docs.md`](examples/create-epic-operator-docs.md).
- **`bin/manage-project.py`** — declarative Project config.
  `dump OWNER NUMBER` to seed a YAML file from live state, `apply
  FILE` to sync it back (idempotent). Real run:
  [`examples/manage-project-roadmap.md`](examples/manage-project-roadmap.md).
  Also manages custom **`fields:`** now (`DATE`/`NUMBER`/`TEXT` —
  `SINGLE_SELECT` not supported yet, different mutation shape, add if
  actually needed) — real run creating `Date`/`Effort` on the org's
  `TCOS Roadmap` project in
  [`examples/roadmap-fields-and-sync.md`](examples/roadmap-fields-and-sync.md).
- **`bin/sync-roadmap-status.py OWNER NUMBER [--apply]`** — derives a
  Project item's time-bucket `Status` (`Near Future Todo` / `In
  Future`) from its `Date` field instead of a human hand-flipping a
  dropdown. Dry-run by default (reports what would change); `--apply`
  writes it. Never touches `In Progress`/`Done` — completion state is a
  human fact, a date doesn't imply it. Items with no `Date` set are
  reported, not guessed at. `--threshold-days` (default 59) is a real
  but **not yet confirmed** candidate — see
  [`roadmap`](https://github.com/Twin-Cities-Open-Systems/roadmap)'s
  README for the open near/far-boundary question this default is
  standing in for. Real run, including a disposable write-path proof
  that was cleaned up after itself:
  [`examples/roadmap-fields-and-sync.md`](examples/roadmap-fields-and-sync.md).

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
  `--out FILE` writes the report to a file. Real run, surveying
  `pallets` (Flask's maintainers):
  [`examples/survey-github-org-pallets.md`](examples/survey-github-org-pallets.md).

## Bulk PR review

- **`bin/pr-review-console.sh [OWNER]`** — tmux console for reviewing
  PRs across the whole org from a terminal instead of the GitHub
  Android app. Two vertical panes: left lists every open PR needing
  your review (falls back to all open PRs org-wide if none are
  pending on `@me`); typing a number writes it to a shared state file,
  which the right pane polls and re-renders full detail for
  (title/state/+adds/-dels/body/diff). No `fzf` dependency — plain
  numbered-list + `read`, works anywhere `tmux` + `gh` exist.
  Pulls detail via `gh api repos/OWNER/REPO/pulls/NUM` (REST), not `gh
  pr view`/`gh pr diff` — both of those `gh` subcommands hit a broken
  GraphQL path (a deprecated Projects-Classic field,
  `repository.pullRequest.projectCards`) that fails on most repos in
  this org; REST doesn't touch that field. Per the central guide's
  gh-first-then-fallback policy, this is the documented fallback, not
  a permanent workaround — a `gh` CLI fix upstream would obsolete it.
  Real run: [`examples/pr-review-console-output.md`](examples/pr-review-console-output.md).

## Contract governance

- **`bin/audit-contracts.py [--repo OWNER/REPO ...]`** — scans every real
  `apiVersion: hee/v1`, `kind: Contract` file across the org (default:
  `human-execution-engine` + `fleet-ops`) and reports which ones are
  actually ratified vs. still need a vote. "Ratified" is verified, not
  trusted: for anything claiming `status: ratified`, this checks that
  the `.asc` GPG-signature file it names actually exists in the repo,
  live via the API, not just that the pointer text reads correctly.
  Classifies each into `RATIFIED_VERIFIED`, `RATIFIED_UNVERIFIED` (claims
  ratified but the evidence file is missing — a real inconsistency),
  `NEEDS_VOTE` (proposed), `NO_STATUS_FIELD` (not even declared
  proposed), `OTHER_STATUS` (a different vocabulary, e.g. `completed` —
  flagged for a human call rather than guessed at), and lists the older,
  schema-different `contracts/*.contract.yaml` family (GPT/Oper/Relay
  lane governance, no ratification concept) separately rather than
  scoring them against a standard that was never theirs. First real run
  immediately surfaced a genuine unratified `financial-authority`
  contract that needed a vote — see
  [`examples/audit-contracts-output.md`](examples/audit-contracts-output.md)
  for the real output.

## Do not run without reading first

- **`bin/bulk_org_repo_readme_update.bash`** — this is the script that
  produced the org-wide README wipe fixed across 14 repos on
  2026-08-20/21 (unfilled template placeholders overwriting real
  content). Whatever version exists now has not been reviewed or
  fixed since that incident — read it in full and understand exactly
  what it will overwrite before running it again on anything.
