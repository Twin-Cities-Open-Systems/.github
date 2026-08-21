# Corpus

**Thesis, not settled doctrine** — same framing as
[`human-execution-engine`'s `CORPUS.md`](https://github.com/Twin-Cities-Open-Systems/human-execution-engine/blob/main/CORPUS.md):
an unproven idea for whether a top-level "what actually exists here"
index is worth maintaining. If it drifts stale faster than it's
useful, remove it.

## Profile / org-facing

- `profile/README.md` — renders as the org's public GitHub profile
  page.
- `profile/GLOSSARY.md`, `profile/ARCHITECTURE.md`,
  `profile/ORGANIZATION_BOOTSTRAP.md`, `profile/WORKFLOW.md` — org
  reference docs.
- `README.md` (root) — what renders browsing this repo directly, not
  the org profile.

## Scripts (`bin/`) — see `OPERATORS.md` for the actual how-to

- **Epic/Project tooling:** `create-epic.py`, `manage-project.py`
- **External research:** `survey-github-org.py`
- **Org-wide repo sync/audit:** `manage-org-repos.sh`,
  `sync-org-repos.sh`, `audit-branch-states.sh`,
  `cron_sweep_repo.bash`
- **CODEOWNERS/README centralization:**
  `purge_all_repo_codeowners_in_favor_of_org_root.bash`,
  `bulk_org_repo_readme_update.bash` (do not run without reading
  first — see `OPERATORS.md`), `relative-link-fixer.sh`,
  `verify_commit_push_readme.bash`
- **Bootstrap:** `init-org.sh`, `init-org-foundation.sh`,
  `init-glossary.sh`
- **PR/merge:** `merge-org-prs.sh`, `merge-strategy.sh`
- **Hooks:** `bin/hooks/` (pre-commit link/secret checks)

## CI

- `.github/workflows/global-script-audit.yml` — reusable workflow
  other repos call in (header-format check, opt-in; unfilled
  template-placeholder detection).
