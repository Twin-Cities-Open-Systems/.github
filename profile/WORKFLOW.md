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
