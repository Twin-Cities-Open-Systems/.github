---
document_type: Operational-Playbook
target_domain: Twin-Cities-Open-Systems
last_modified: 2026-08-19
status: Mandated-Standard
---

# TCOS New Organization Blueprint & Best Practices

This playbook defines the required architecture and configuration sequence for building and initializing an enterprise workspace organization matching current TCOS structural standards.

---

## [POLICIES] Global Governance & Visibility Settings
* **Default Visibility State:** All repositories must be configured as `Public` by default unless explicitly containing proprietary compute engines, private scheduling assets, or identity access records.
* **Fallback Link Masking:** All documentation cross-references must use relative file-system paths (`../repo-name`) to automatically hide broken links from external viewers while preserving functional links for internal team members.

## [RULESETS] Enterprise Branch Protections
* **Policy Target Scope:** Include all repositories uniformly using root-level Organization Rulesets.
* **Mainline Lockdowns:** Default tracking branches (`main` or `master`) must have direct force-pushes completely blocked and mandate a minimum of 1 approved Pull Request before code can be merged.
* **Session Controls:** Account sessions containing top-tier organization owner roles will bypass constraints by default to prevent administrative lockouts during maintenance runs.

## [HOOKS] Local Workspace Guardrails
* **Linter Invariants:** Staged markdown modifications must be run through an absolute URL tracker to prevent hardcoded absolute paths from breaking permission masking rules.
* **Secret Interception:** Staged repository changes must be scanned against Gitleaks rule files before a commit hash can be written to disk to intercept accidental key disclosures.

## [LIBS] Scripting & Automation Standards
* **Userland Tools:** Any script running inside a user shell must use a portable shebang directive (`#!/usr/bin/env <tool>`) and a mandatory 4-line tracking metadata header block.
* **Function Libraries:** Reusable modules or script wrappers meant strictly to be sourced must omit the execution bit (`chmod -x`) and contain no shebang line.

