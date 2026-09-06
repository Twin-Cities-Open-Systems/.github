---
document_type: Operational-Playbook
target_domain: Twin-Cities-Open-Systems
last_modified: 2026-08-27
status: Mandated-Standard
---

# TCOS Org Setup & Bootstrap Notes

Read this when actually bootstrapping a new repo or bringing GitHub config
back in line with org standard -- not something an agent needs loaded for a
normal coding session (that's `prompts/PROMPTING_RULES.md`, in
`human-execution-engine`). This file replaces the old `WORKFLOW.md` and
`ORGANIZATION_BOOTSTRAP.md`; their every-session content (commit format,
merge flow, hook footguns) moved to `PROMPTING_RULES.md`, and their
scripting-header rule was already duplicated here -- the canonical copy is
`GLOSSARY.md` §4, not this file.

## Repo & visibility defaults

- All repositories are `Public` by default unless they hold proprietary
  compute engines, private scheduling assets, or identity/access records.
- Default branch (`main`) requires direct force-pushes blocked and at least
  1 approved PR to merge. Apply via org-wide Rulesets, not per-repo settings,
  so one change covers every repo uniformly.
- One global fallback `CODEOWNERS` at `.github/CODEOWNERS` -- not a copy in
  every repo. Local per-repo `CODEOWNERS` files caused real maintenance
  drift and silent lockouts when rulesets were armed; centralizing fixed it.
  Measured 2026-09-06: four repos still carried a local file (thesis-engine
  and glass-ops naming an agent as owner of everything, fleet-ops naming
  the same owner as the fallback); removed by PR in each repo. The old
  purge script (`purge_all_repo_codeowners_in_favor_of_org_root.bash`, gone) did the same <!-- hee-check:refs-ok  retired file, named as history -->
  as a bare `rm -f` in every checkout with no commit, and would have
  taken the deliberate file below with it; retired. The one deliberate local file
  is human-execution-engine's, which adds a SecOps reviewer on the
  doctrine paths (contracts, blueprints, schemas, registries; hee#196).
  `require_code_owner_reviews` is off everywhere, so CODEOWNERS only
  auto-requests reviewers; it never lets an author approve their own PR.
- The OPER is a **bypass actor** for required reviews on every protected
  `main` (`bypass_pull_request_allowances.users: spencerbutler`, set
  2026-09-06). GitHub never lets an author approve their own PR, so
  without this the OPER's own one-line PRs needed an agent's approval;
  with it they merge on the OPER's say, still through a PR (rule 1).
  Agents are not bypass actors: their PRs still need the OPER.

## Local git config (once per machine)

```bash
git config --global push.autoSetupRemote true
git config --global fetch.prune true
git config --global init.defaultBranch main
```

## Issue hierarchy

One central Organization Project Board, not per-repo boards:

```
Epic          -> Org Roadmap (Timeline View), multi-repo, spans quarters
  Feature     -> Kanban Board View, one discrete capability
    Sub-issue -> PR-bound tactical work; keep its own labels --
                 labels don't inherit from the parent issue
```

## GitHub admin gotchas (hit once, worth not re-discovering)

- The Ruleset Bypass List UI stays hidden until at least one branch
  enforcement rule is actively checked -- don't assume the feature is
  missing.
- `gh ruleset list --org` and other org-rule-management calls need an
  explicit `admin:org` token scope; a standard read/write token isn't
  enough even for an org owner account.
- Never hardcode a user's home path (`/home/spencer/...`) into a shared
  init/bootstrap template -- use `$HOME` so it works on any machine or
  automated node. (The recursion-guard and destructive-git-clean footguns
  that used to live here are now in `PROMPTING_RULES.md` -- they're
  every-session hazards, not one-time setup facts.)

## Secret scanning

Staged changes are scanned against `profile/tcos-audit-rules.toml`
(Gitleaks rules) before a commit can be written -- see
`bin/hooks/pre-commit-secret-check.sh`. Wire this into a new repo via
`bin/init-org.sh`'s hook-install step, don't hand-roll it.
