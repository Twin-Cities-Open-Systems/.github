# TCOS Global Architecture Blueprint

This document defines the structural ecosystem of Twin Cities Open Systems (TCOS) and how our repositories fit together.

## 🧬 Core Paradigm: human-execution-engine
The foundational design philosophy animating TCOS is the [human-execution-engine](https://github.com/Twin-Cities-Open-Systems/human-execution-engine). All automation, tooling scripts, and repositories are engineered to augment, standardize, and clear paths for human execution and systemic continuity.

---

## 📦 Repository Mapping

Our workload is divided across specialized repositories with distinct boundaries. Do not cross-contaminate codebases.

### [.github](https://github.com/Twin-Cities-Open-Systems/.github) (Public) (Command Center)
*   **Purpose:** Serves as the global organizational controller and centralized governance repository for the entire Twin Cities Open Systems (TCOS) GitHub ecosystem.
*   **Contents:** Features organization-wide repository health standards, default issue and pull request templates, automated workflow actions, security policy frameworks, and high-visibility community onboarding documentation.

### [thesis-engine](https://github.com/Twin-Cities-Open-Systems/thesis-engine) (Very Private) (Core Intellectual Property)
*   **Purpose:** Serves as the proprietary core simulation, analytical verification, and compute engine that validates all multi-agent thesis workflows across the TCOS ecosystem.
*   **Contents:** Features backend computational execution models, verification state machines, localized data ingestion pipelines, and an integrated system operations dashboard.
*   **Roadmap** Refactor the codebase to cleanly decouple the analytical visualization dashboard from the core processing engine, enabling an independent public release of the dashboard interface.

### [fleet-ops](https://github.com/Twin-Cities-Open-Systems/fleet-ops) (Private) (Internal Operations)
*   **Purpose:** Serves as the centralized command hub for daily internal operations, resource scheduling engines, and administrative workflow automation across the organization.
*   **Contents:** Features environment orchestration scripts, automated infrastructure maintenance pipelines, localized high-frequency cron utilities, and access configuration keys.
*   **Integration:** Interfaces programmatically with external cloud provider environments and organization-wide repository management logic.

### [tcos-www](https://github.com/Twin-Cities-Open-Systems/tcos-www) (Public) (Public Web Presence)
*   **Purpose:** Serves as the primary public-facing entry point, digital storefront, and official brand homepage for the organization.
*   **Contents:** Features optimized production landing page assets, client-side routing structures, embedded documentation portals, and deployment configurations for marketing builds.
*   **Roadmap:** Implement dynamic portfolio landing blocks to showcase open-source repositories, integrate real-time status telemetry from core systems, and build an open portal for community documentation.

### [human-execution-engine](https://github.com/Twin-Cities-Open-Systems/human-execution-engine) (Public) (Core Principles)
*   **Purpose:** Defines the foundational operational design, organizational philosophies, and human-centric core reasoning guidelines that govern TCOS system behavior.
*   **Contents:** Features behavioral blueprints, abstract design logic frameworks, stakeholder governance protocols, and standard operating models for vendor relationships.

### [tcos-plan-private](https://github.com/Twin-Cities-Open-Systems/tcos-plan-private) (Very Private) (Core Intellectual Property)
*   **Purpose:** Serves as the central repository for internal organizational roadmaps, strategic business planning, and high-level project governance.
*   **Contents:** Features corporate milestones, resource allocation frameworks, product pipeline schedules, budget forecasting models, and internal operational alignment strategies. 

### [mt-logo-render](https://github.com/Twin-Cities-Open-Systems/mt-logo-render) (Public) (Core Open Source Offering)
*   **Purpose:** Provides a high-performance utility that programmatically generates cryptographic hashes and localized image outputs directly from structured design recipes and configuration inputs.
*   **Contents:** Features optimized Rust source code, deterministic asset compilation scripts, mathematical rendering pipelines, image export drivers, and usage documentation for the CLI tool.

### [glass-ops](https://github.com/Twin-Cities-Open-Systems/glass-ops) (Private->Public) (Core Open Source Offering)
*   **Purpose:** Acts as a specialized display driver and user interface orchestrator that directly controls window layouts, active workspaces, and visual outputs on physical monitors.
*   **Contents:** Features bare-metal window management utilities, X11/Wayland display server configurations, hardware-level interface controllers, and shortcut optimization scripts for native operating environments.
*   **Roadmap:** Refactor the core layout scripts, optimize hardware resource usage, and establish standardized open-source installation blueprints prior to its public ecosystem release.

### [hee-epoch](https://github.com/Twin-Cities-Open-Systems/hee-epoch) (Public) (Core Open Source Offering) (squash and merge)
*   **Purpose:** Serves as the running, real-time historical narrative and foundational record documenting the genesis work, core milestones, and structural evolution of the TCOS ecosystem.
*   **Contents:** Features chronological event-logs, immutable ledger entries of organization milestones, strategic design journals, retrospective engineering reviews, and raw narrative transcripts detailing early architectural decisions.

### [tcos-audit](https://github.com/Twin-Cities-Open-Systems/tcos-audit) (Private) (Internal Custodian)
*   **Purpose:** Functions as an internal security guardrail engineered to prevent Intellectual Property (IP) exposure, personally identifiable information (PII) leakage, and accidental credential disclosures across all TCOS environments.
*   **Contents:** Features automated pre-commit scanning hooks, static application security testing (SAST) pipelines, regular expression signature scanners, secret detection configurations, and real-time alert dispatch webhooks.

### [inbound](https://github.com/Twin-Cities-Open-Systems/inbound) (NoCommits->Private->Public) (External Inputs)
*   **Purpose:** Acts as the secure edge ingestion layer designed to accept, sanitize, and route unstructured external inputs, applications, and webhook data into the TCOS ecosystem.
*   **Contents:** Features public API endpoint endpoints, webform processors, secure file upload handlers, payload validation middleware, and automated payload routers to dispatch incoming data to internal services.

### [resume](https://github.com/Twin-Cities-Open-Systems/resume) (Public) (Spencer Butler Resume)
*   **Purpose:** The resume repository highlights the professional background of our owner, Spencer Butler
*   **Contents:** Spencer Butler's resume. 
*   **Roadmap:** All members will keep (at least) a snippet resume reflecting their work with TCOS.

### [market-thesis](https://github.com/Twin-Cities-Open-Systems/market-thesis) (Public) (Core Open Source Offering)
*   **Purpose:** Acts as a centralized public repository to document, validate, and manage macro-economic research, trading frameworks, and quantitative market strategies.
*   **Contents:** Features quantitative trading thesis files, multi-agent simulation workflows, automated data integrity validation hooks, operations quickstarts, performance review templates, and comprehensive version changelogs

### [market-thesis-news](https://github.com/Twin-Cities-Open-Systems/market-thesis-news) (Private->Public) (Planned Open Source Offering)
*   **Purpose:** Automates the extraction, processing, and contextualization of financial news feeds to actively track real-time macro updates and assess narrative impacts on existing trading thesis models.
*   **Contents:** automated news scraping scripts, NLP narrative-sentiment analyzer tools, programmatic API webhooks, dynamic event-logging pipelines, and modular integration components built to stream data directly into parent evaluation workflows.

### [tick-task](https://github.com/Twin-Cities-Open-Systems/tick-task) (Public) (Core Open Source Offering)
*   **Purpose:** Orchestrates high-frequency, time-critical tasks and event-driven automation sequences calibrated to match rapid financial data ticks or system state changes.
*   **Contents:** Features precise task schedulers, sub-millisecond cron utilities, event-triggering pipelines, resource monitoring listeners, error-recovery mechanisms, and modular API endpoints for concurrent system operations.

### [dotfiles](https://github.com/Twin-Cities-Open-Systems/dotfiles) (Private->Public) (Open Source Offering)
*   **Purpose:** Provides a unified, portable environment configuration setup designed to establish and synchronize consistent system settings, keyboard shortcuts, and developer tooling layouts across multiple different shells.
*   **Contents:** Features environment variables, customized prompt configurations, alias libraries for Bash/Zsh/Fish shells, cross-platform install initialization scripts, custom terminal multiplexer schemes, tool-specific configuration profiles, and modular path managers.

### [devops](https://github.com/Twin-Cities-Open-Systems/devops) (Private->Archive) (Historical Reference)
*   **Purpose:** 
*   **Contents:** 

---

## 🔄 Systemic Lifecycle Rules
1. **Adding a New Component:** If an automation task requires a new repository, it must first be registered in this blueprint under a dedicated subsystem boundary.
2. **Cross-Repo Dependencies:** No code repository should directly import execution scripts from `fleet-ops`. `fleet-ops` orchestrates *from above*; it does not act as a dependency library.
