# TCOS Engineering Workflow & Continuity Guide

This document establishes how we manage issues, design project roadmaps, format history, and interact with Git to maintain clean software lifecycles.

---

## 1. Global Git Configuration (`.gitconfig`)
Every engineer and automation assistant working in the TCOS ecosystem must configure their local environment to automate branch staging and clean up stale tracking code. 

Add the following blocks to your global `~/.gitconfig` or apply them directly via terminal:

```ini
[push]
    # Automatically setup remote tracking branches on simple 'git push'
    autoSetupRemote = true

[fetch]
    # Automatically drop remote tracking branches locally if deleted from GitHub
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

We maintain **one central Organization Project Board** with custom views. Repositories host code; the Org Project hosts project execution. Never scatter "master issues" across individual code repositories.

[ Epic Issue ] ───► Tracked exclusively on the Organization Roadmap (Timeline View)└── [ Feature Issue ] ───► Component Capability (Kanban Board View)└── [ Sub-Issue / Task ] ───► Micro engineering steps / PR-bound work

### Strategic Hierarchy Rules
1. **The Epic (Why & What High-Level Outcome):** Abstract, multi-repository milestones spanning target quarters or months.
   * *Example:* `Epic: Internal DevEx and Workflow Automation`
2. **The Feature (Component Boundary):** Core discrete features required to complete an Epic.
   * *Example:* `Feature: Standardize Organization Labels and Issue Nests`
3. **The Sub-Issue/Task (Granular Steps):** Standalone tactical items bound to a Parent Issue. **Sub-issues must retain functional labels** (e.g., `type/bug`, `area/backend`) because labels do not inherit from parent issues.

---

## 3. Title & Commit Naming Conventions

We strictly use the **Conventional Commits** format for all Pull Request titles and commit targets.

### Allowed Layout Syntax
`type(scope): concise imperative description`

*   **`feat(...)`**: A brand new user or developer feature.
*   **`fix(...)`**: A localized bug fix.
*   **`chore(...)`**: Continuous integration tweaks, workflow automation scripts, or dependency bumps.
*   **`docs(...)`**: Modifying readmes, asset markdown files, or internal commentary.

### Concrete Execution Trace
*   **Epic Issue:** `Epic: Public Web Presence Overhaul`
*   **Feature Issue:** `Feature: Migrate Landing Page to Tailwind CSS`
*   **Sub-Issue / Task:** `Task: Install Tailwind dependencies and setup config`
*   **Pull Request Title:** `feat(styles): implement tailwind css framework core layout`
*   **Commit Message:** `feat(css): inject tailwind directives to main entrypoint`

---

## 4. Pull Request & Merging Execution

TCOS exclusively uses the **Squash and Merge** execution standard for standard feature work to maintain linear history records on `main` branches. 

### The Standard Command Line Flow
Do not jump out of your terminal context or execute manual UI steps inside web browsers. Use this precise sequence:

1. **Stash and commit changes locally:**
   ```bash
   git commit -m "chore(merge-strat): completed script automation"
   ```
2. **Push securely to GitHub:**
   ```bash
   git push
   ```
3. **Generate an automated Pull Request:**
   ```bash
   gh pr create --fill
   ```
4. **Bypass interactive prompts and merge cleanly:**
   ```bash
   gh pr merge --squash --delete-branch
   ```
