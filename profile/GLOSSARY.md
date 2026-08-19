---
organization: Twin-Cities-Open-Systems
version: 1.0.0
last_updated: 2026-08-19
type: Organizational-Invariant-Declaration
---

# TCOS Global Glossary & Invariant Declaration

This document serves as the immutable, single source of truth (SSoT) for terminology, acronym definitions, and systemic invariants across all Twin-Cities-Open-Systems (TCOS) codebases, documentation files, and narrative engines.

---

## 1. Core Dictionary & Invariants
*System invariants declare how terms MUST be applied. These rules are strictly enforced by our workspace linters.*

### Twin Cities Open Systems
* **Type:** Organization Name
* **Invariant Standard:** Must always be written as `Twin-Cities-Open-Systems` in configuration files or hyphenated/capitalized as `Twin Cities Open Systems` in prose. Never abbreviate to lowercase `tcos` in formal external communications.

### Pedigree
* **Type:** Organizational Paradigm
* **Invariant Standard:** Refers exclusively to the proven track record, core credentials, and structural lineage of system owners or foundational intellectual property within the `human-execution-engine`.

### Glass
* **Type:** Architectural Layer
* **Invariant Standard:** Refers strictly to bare-metal hardware monitor displays managed by `glass-ops`. Never use to describe cloud dashboards or web-based frontend browser views.

### Documentation Invariant
* **Type:** Transparency Security Gate
* **Invariant Standard:** No private structural details, operational API keys, specific vendor names, or target asset metrics may ever be written into the text descriptions of repositories marked as `(Private)` or `(Very Private)`. All private repository entries must use abstract operational language.

---

## 2. Acronym Expander
*Automated parsers use this section to expand shorthand references in system logs, documentation headers, and commit messages.*

| Shorthand | Expanded Meaning | Associated Core Repository |
| :--- | :--- | :--- |
| **TCOS** | Twin Cities Open Systems | `Twin-Cities-Open-Systems/.github` |
| **NLP** | Natural Language Processing | `market-thesis-news` |
| **HEE** | Human Execution Engine | `human-execution-engine` |
| **MT** | Market Thesis | `market-thesis` |
| **PII** | Personally Identifiable Information | `tcos-audit` |
| **IP** | Intellectual Property | `tcos-plan-private` / `thesis-engine` |
| **SSoT** | Single Source of Truth | Global Platform |

---

## 3. Systematic Thesaurus (Context Mapper)
*Maps colloquial words to our precise enterprise technical terms to prevent language ambiguity.*

* **Instead of:** `credentials`, `resume profile`, `history`
  * **Use TCOS Standard:** `Pedigree` (when referring to founder backgrounds) or `Track Record` (when referring to repository execution history).
* **Instead of:** `cron job`, `task manager`, `script loop`
  * **Use TCOS Standard:** `Tick-Task Event` (when running high-frequency sub-millisecond execution loops via `tick-task`).
* **Instead of:** `frontend`, `ui layout`, `desktop setup`
  * **Use TCOS Standard:** `Glass Operations` or `Monitor Glass Interface` (handled natively by `glass-ops`).
* **Instead of:** `secrets scan`, `leak check`
  * **Use TCOS Standard:** `Custodian Custody Review` (enforced via `tcos-audit`).

---

## 4. Scripting & Code Header Invariants
*All automation assets, utilities, and userland scripts originating within TCOS domains must enforce this standard.*

### Mandatory Execution Block (First 4 Lines)
Every script executing inside a userland shell layer must match this structural signature across its initial 4 lines without exception:

1. **Line 1:** Portable Shebang Directive (`#!/usr/bin/env <tool_name>`)
2. **Line 2:** Author Attribute & Target Domain (`# Developer Name <email@tcos.us>`)
3. **Line 3:** Exact Base Filename (`# filename.extension`)
4. **Line 4:** High-Level Functional Abstract (`# This script executes foo, bar, and baz.`)

### Library & Mixin Invariant (Non-Executable Scripts)
* **Type:** Structural Code Paradigm
* **Invariant Standard:** Code assets containing reusable function blocks, hooks, or environment wrappers (e.g., `cron_sweep_repo.bash`) that are designed exclusively to be sourced by other runtime controllers must not contain a shebang line and must remain non-executable (`chmod -x`). 

### Reference Example (`bin/cron_sweep_repo.bash`)
```bash
# Spencer Butler <dev@tcos.us>
# cron_sweep_repo.bash
# Sourced library containing non-interactive workspace synchronization blocks.
#
# This file is an operational library and cannot be executed directly.

cron_sweep_repo() {
    # Function logic lives here safely without an execution layer
    echo "[+] Sourced function routine invoked."
}
```
