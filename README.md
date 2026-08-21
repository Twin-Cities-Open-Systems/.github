# .github

Twin-Cities-Open-Systems' org-wide **GitHub-platform tooling** repo —
config, scripts, and CI that operate *on* the GitHub org itself.

**This is not the same kind of "central" as
[`human-execution-engine`](https://github.com/Twin-Cities-Open-Systems/human-execution-engine)**,
which is the root source of TCOS/HEE doctrine and governance content —
what's true and authoritative, independent of any hosting platform.
HEE currently lives on GitHub and uses its issue/PR/repo machinery for
real workflow, but that's a hosting choice, not a property of the
doctrine itself — moving HEE to a different git server (see
[fleet-ops#155](https://github.com/Twin-Cities-Open-Systems/fleet-ops/issues/155),
the tracked on-prem git server plan) should work the same. This repo,
by contrast, genuinely *is* GitHub-specific — its whole job is GitHub
org administration, so GitHub-coupling here isn't a smell, it's the
point.

- `profile/README.md` renders as the org's public profile page
  (github.com/Twin-Cities-Open-Systems).
- `profile/GLOSSARY.md` — the org's shared definitions/invariants.
- `bin/` — org-wide scripts (repo sync/audit, CODEOWNERS centralization,
  README maintenance, link/secret pre-commit hooks).
- `.github/workflows/global-script-audit.yml` — reusable CI workflow
  other repos can call in (header-format check, opt-in; unfilled
  template-placeholder detection).
- `.github/CODEOWNERS` — org-default fallback for repos that don't
  define their own.
