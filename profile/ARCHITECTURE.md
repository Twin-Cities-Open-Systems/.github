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
