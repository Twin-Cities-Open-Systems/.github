#!/usr/bin/env bash
set -e

echo "🚀 Overhauling TCOS command center profiles and architecture..."

# Ensure target directories exist
mkdir -p profile
mkdir -p .github/ISSUE_TEMPLATE

# 1. Generate Organization Landing Page (profile/README.md)
cat << 'EOF' > profile/README.md
# Twin Cities Open Systems (TCOS) Command Center

Welcome to the central tracking repository for TCOS. This homepage serves as the primary onboarding node for engineers and automated continuity assistants.

## 🛠 Core Operations
*   **System Layout:** Review our [Global Architecture Blueprint](ARCHITECTURE.md) to understand our codebase relationships.
*   **Engineering Standards:** Review our [Workflow & Git Playbook](WORKFLOW.md) before contributing code.

## 🎯 Quick Navigation
*   [Active Organization Project Boards](https://github.com)
*   [Global Architecture Blueprint](ARCHITECTURE.md)
*   [Global Workflow Engineering Guide](WORKFLOW.md)
EOF

# 2. Generate Global Architecture Blueprint (profile/ARCHITECTURE.md)
cat << 'EOF' > profile/ARCHITECTURE.md
# TCOS Global Architecture Blueprint

This document defines the structural ecosystem of Twin Cities Open Systems (TCOS) and how our repositories fit together.

## 🧬 Core Paradigm: human-execution-engine
The foundational design philosophy animating TCOS is the **human-execution-engine**. All automation, tooling scripts, and repositories are engineered to augment, standardize, and clear paths for human execution and systemic continuity.

---

## 📦 Repository Mapping

Our workload is divided across specialized repositories with distinct boundaries. Do not cross-contaminate codebases.

### 1. `fleet-ops` (Internal Operations)
*   **Purpose:** Our internal hub for daily work, scheduling engines, and administrative automation.
*   **Contents:** System orchestration scripts, maintenance pipelines, and localized cron tools.
*   **Integration:** Interacts directly with cloud environments and repository management logic.

### 2. `tcos-www` (Public Web Presence)
*   **Purpose:** The public-facing entry point and brand storefront for the organization.
*   **Contents:** Production landing page assets, documentation routing, and marketing builds.

### 3. `.github` (Command Center)
*   **Purpose:** The global organizational controller repository (this repo).
*   **Contents:** Global configurations, default issue workflows, and high-visibility onboarding documentation.

---

## 🔄 Systemic Lifecycle Rules
1. **Adding a New Component:** If an automation task requires a new repository, it must first be registered in this blueprint under a dedicated subsystem boundary.
2. **Cross-Repo Dependencies:** No code repository should directly import execution scripts from `fleet-ops`. `fleet-ops` orchestrates *from above*; it does not act as a dependency library.
EOF

# 3. Generate the Workflow Playbook (profile/WORKFLOW.md)
cat << 'EOF' > profile/WORKFLOW.md
# TCOS Engineering Workflow & Continuity Guide

This document establishes how we manage issues, design project roadmaps, format history, and interact with Git to maintain clean software lifecycles.

---

## 1. Global Git Configuration (`.gitconfig`)
Every engineer and automation assistant working in the TCOS ecosystem must configure their local environment to automate branch staging and clean up stale tracking code. 

```ini
[push]
    autoSetupRemote = true
[fetch]
    prune = true
[init]
    defaultBranch = main
```

### To apply these instantly via terminal:
```bash
git config --global push.autoSetupRemote true
git config --global fetch.prune true
git config --global init.defaultBranch main
```

---

## 2. Issue Hierarchy & The Org Roadmap

We maintain **one central Organization Project Board** with custom views. Repositories host code; the Org Project hosts project execution. 

[ Epic Issue ] ───► Tracked exclusively on the Organization Roadmap (Timeline View)└── [ Feature Issue ] ───► Component Capability (Kanban Board View)└── [ Sub-Issue / Task ] ───► Micro engineering steps / PR-bound work

### Strategic Hierarchy Rules
1. **The Epic:** Abstract, multi-repository milestones spanning target quarters or months.
   * *Example:* `Epic: Internal DevEx and Workflow Automation`
2. **The Feature:** Core discrete features required to complete an Epic.
   * *Example:* `Feature: Standardize Organization Labels and Issue Nests`
3. **The Sub-Issue/Task:** Standalone tactical items bound to a Parent Issue. **Sub-issues must retain functional labels** (e.g., `type/bug`, `area/backend`) because labels do not inherit from parent issues.

---

## 3. Title & Commit Naming Conventions

We strictly use the **Conventional Commits** format for all Pull Request titles and commit targets.

### Allowed Layout Syntax
`type(scope): concise imperative description`

*   **`feat(...)`**: A brand new user or developer feature.
*   **`fix(...)`**: A localized bug fix.
*   **`chore(...)`**: Continuous integration tweaks, workflow automation scripts, or dependency bumps.
*   **`docs(...)`**: Modifying readmes, asset markdown files, or internal commentary.

---

## 4. Pull Request & Merging Execution

TCOS exclusively uses the **Squash and Merge** execution standard for standard feature work to maintain linear history records on `main` branches. 

### The Standard Command Line Flow
```bash
git commit -m "chore(merge-strat): completed script automation"
git push
gh pr create --fill
gh pr merge --squash --delete-branch
```
EOF

# 4. Generate the Automated Global Feature Issue Template (.github/ISSUE_TEMPLATE/feature.md)
cat << 'EOF' > .github/ISSUE_TEMPLATE/feature.md
---
name: 🚀 Feature Track
about: Standard template for establishing a scoped architectural capability.
title: 'Feature: '
labels: ['type/feature']
---

## 🧭 Context
*   **Parent Epic Link:** <!-- Provide issue reference link here -->
*   **Target Functional Component/Repo:** 

## 📋 High-Level Requirements
- [ ] <!-- Element task checkbox -->

## 🛠 Executable Sub-Tasks
<!-- When sub-issues are added to this issue via the GitHub UI, they will nest here automatically -->
EOF

echo "✨ All organizational assets built under exact naming schemas!"
echo "👉 Review status using: git status"
