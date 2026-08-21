# .github

Twin-Cities-Open-Systems' org-wide governance/tooling repo — the
global organizational controller and centralized configuration for
the rest of the TCOS GitHub ecosystem.

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
