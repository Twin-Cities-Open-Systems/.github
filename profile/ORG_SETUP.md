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
