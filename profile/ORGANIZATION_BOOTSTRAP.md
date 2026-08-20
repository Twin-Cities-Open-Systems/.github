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

---

## [FOOTGUNS] Resolved Architecture Traps

### 1. The Git Automation Reset Trap
* **The Vulnerability:** Running clean loops (`git clean -fdx` and `git reset --hard`) immediately following a `git stash pop` inside headless multi-repo script runners. Because popped modifications sit in the uncommitted tree, a raw trailing reset treats them as noise and purges active development work completely from disk.
* **The Permanent Resolution:** Strip all destructive clean boundaries from the primary update sequence. Force the synchronization mechanism to use isolated git feature tracks or run a strict, safe `pull --rebase` process path.

### 2. Git Hook Shell Level Stack Overflow (monitor, still active TODO(@touchy-claude))
* **The Vulnerability:** Triggering core Git tracking operations (such as `git diff` or `git status`) inside localized pre-commit subshell hook scripts. This causes the localized tracking engine to continuously re-evaluate the parent `.git/hooks/pre-commit` wrapper, spinning up a self-referencing subshell loop until Bash crashes at shell level `1000`.
* **The Permanent Resolution:** Mandate an active **Recursion Guard variable condition** (`TCOS_HOOK_RUNNING`) at the apex of all automation script arrays to kill nested loops instantly before a second process block can fork.

### 3. The Absolute Path Portability Trap
* **The Vulnerability:** Hardcoding explicit folder routes containing user profile strings (e.g., `/home/spencer/`) inside shared initialization templates. This breaks environment portability instantly when the tracking playbook runs on alternate workstations, user contexts, or automated server nodes.
* **The Permanent Resolution:** Utilize the environment configuration literal string path token token (`$HOME`) to dynamically compute path contexts at runtime.

---

## [RETROSPECTIVE] Today I Learned, Tomorrow I Shall Not Repeat

* **Centralize, Don't Scatter CODEOWNERS:** Placing local, isolated `CODEOWNERS` files within individual repositories leads to maintenance drift and hidden automation lockouts when branch rulesets are armed. We learned to use exactly **one global fallback file** positioned inside `.github/.github/CODEOWNERS` to manage permissions cleanly from a single point.
* **The Bypass Module Visibility Guard:** GitHub organization management panels dynamically hide the Ruleset Bypass List container until at least one branch enforcement rule is actively checked.
* **CLI Scope Authentication Limits:** Standard read/write tokens do not inherit global organization rule management permissions. Administrative CLI checks (`gh ruleset list --org`) require an explicit `admin:org` authorization token scope update.

