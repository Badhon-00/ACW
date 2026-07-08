# Awesome Claude Code Skills [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)

> A curated list of awesome [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skills -- markdown-based instruction files that extend Claude Code's capabilities as a coding agent.

Claude Code skills are specialized folders containing a `SKILL.md` file with instructions, scripts, and resources that Claude dynamically discovers and loads when relevant. They live in `~/.claude/skills/` (personal) or `.claude/skills/` (project-level) directories and follow the open [Agent Skills](https://agentskills.io) specification.

**[Official Documentation](https://code.claude.com/docs/en/skills)** | **[Anthropic Skills Repo](https://github.com/anthropics/skills)** | **[Agent Skills Spec](https://github.com/anthropics/skills/blob/main/spec/agent-skills-spec.md)**

## Contents

- [What Are Claude Code Skills?](#what-are-claude-code-skills)
- [How to Install a Skill](#how-to-install-a-skill)
- [Official & Bundled Skills](#official--bundled-skills)
- [Development & Coding](#development--coding)
  - [Frontend](#frontend)
  - [Backend](#backend)
  - [Fullstack](#fullstack)
  - [Testing](#testing)
  - [Code Quality](#code-quality)
  - [Mobile](#mobile)
- [Data & Analysis](#data--analysis)
  - [Data Science](#data-science)
  - [Visualization](#visualization)
  - [Databases](#databases)
- [DevOps & Infrastructure](#devops--infrastructure)
  - [CI/CD](#cicd)
  - [Cloud & Deployment](#cloud--deployment)
  - [Containers & Orchestration](#containers--orchestration)
  - [Monitoring & Observability](#monitoring--observability)
- [AI & ML](#ai--ml)
  - [Prompt Engineering](#prompt-engineering)
  - [Model Integration](#model-integration)
  - [Agent Development](#agent-development)
- [Security](#security)
- [Business & Productivity](#business--productivity)
  - [Project Management](#project-management)
  - [Documentation](#documentation)
  - [Communication](#communication)
- [Design & Creative](#design--creative)
  - [UI/UX](#uiux)
  - [Content Creation](#content-creation)
  - [Diagrams & Visuals](#diagrams--visuals)
- [Research & Writing](#research--writing)
- [Workflow & Automation](#workflow--automation)
- [Language & Framework Specific](#language--framework-specific)
  - [Python](#python)
  - [JavaScript/TypeScript](#javascripttypescript)
  - [Rust](#rust)
  - [Go](#go)
  - [Other Languages](#other-languages)
- [What Makes a Good Skill](#what-makes-a-good-skill)
- [Contributing](#contributing)
- [License](#license)

## What Are Claude Code Skills?

Claude Code skills are markdown-based instruction files that teach Claude how to perform specific tasks in a repeatable way. Each skill is a directory containing:

```
my-skill/
├── SKILL.md           # Main instructions (required)
├── templates/         # Templates for output
├── examples/          # Example outputs
├── scripts/           # Helper scripts
└── references/        # Reference documentation
```

The `SKILL.md` file uses YAML frontmatter to configure behavior and markdown content for instructions:

```yaml
---
name: my-skill
description: What this skill does and when to use it
allowed-tools: Bash, Read, Write
---

Instructions for Claude go here...
```

Skills are invoked in two ways:
- **Automatically** -- Claude detects when a skill is relevant and loads it.
- **Manually** -- Type `/skill-name` in Claude Code to invoke directly.

For the full specification, see the [official skills documentation](https://code.claude.com/docs/en/skills).

## How to Install a Skill

**Personal skills** (available across all projects):

```bash
# Clone or copy a skill into your personal skills directory
mkdir -p ~/.claude/skills/
cp -r path/to/some-skill ~/.claude/skills/some-skill
```

**Project skills** (available only in that project):

```bash
# Add to your project's .claude/skills/ directory
mkdir -p .claude/skills/
cp -r path/to/some-skill .claude/skills/some-skill
# Optionally commit to version control
git add .claude/skills/some-skill
```

**From a Git repository:**

```bash
# Clone into personal skills
git clone https://github.com/user/some-skill ~/.claude/skills/some-skill
```

## Official & Bundled Skills

Skills that ship with Claude Code or are maintained by Anthropic.

- [simplify](https://github.com/anthropics/skills) - Reviews recently changed files for code reuse, quality, and efficiency issues, then fixes them. Spawns three parallel review agents.
- [batch](https://github.com/anthropics/skills) - Orchestrates large-scale changes across a codebase in parallel. Decomposes work into 5-30 independent units, each in an isolated git worktree.
- [debug](https://github.com/anthropics/skills) - Troubleshoots your current Claude Code session by reading the session debug log.
- [skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) - Meta-skill that helps you create new skills with proper structure and frontmatter.
- [pdf](https://github.com/anthropics/skills/tree/main/skills/pdf) - Creates and manipulates PDF documents from scratch using Python.
- [docx](https://github.com/anthropics/skills/tree/main/skills/docx) - Generates and edits Microsoft Word documents with formatting and styles.
- [pptx](https://github.com/anthropics/skills/tree/main/skills/pptx) - Creates PowerPoint presentations with slides, layouts, and visual elements.
- [xlsx](https://github.com/anthropics/skills/tree/main/skills/xlsx) - Builds Excel spreadsheets with formulas, charts, and data formatting.
- [frontend-design](https://github.com/anthropics/skills/tree/main/skills/frontend-design) - Builds web components, pages, artifacts, posters, or applications with modern frontend design principles.
- [brand-guidelines](https://github.com/anthropics/skills/tree/main/skills/brand-guidelines) - Applies brand guidelines to ensure consistent visual identity across outputs.
- [internal-comms](https://github.com/anthropics/skills/tree/main/skills/internal-comms) - Drafts internal communications following organizational tone and structure.

## Development & Coding

### Frontend

- [react-component-generator](https://github.com/anthropics/skills) - Scaffolds React components with TypeScript, tests, stories, and proper file structure. Follows your project's component conventions.
- [nextjs-patterns](https://github.com/anthropics/skills) - Implements Next.js App Router patterns including server components, route handlers, middleware, and metadata API.
- [tailwind-converter](https://github.com/anthropics/skills) - Converts traditional CSS to Tailwind utility classes while preserving responsive behavior and animations.
- [vue-composition-api](https://github.com/anthropics/skills) - Generates Vue 3 components using the Composition API with TypeScript, composables, and Pinia stores.
- [svelte-5-patterns](https://github.com/anthropics/skills) - Creates Svelte 5 components with runes, snippets, and the new event system.
- [css-to-styled-components](https://github.com/anthropics/skills) - Migrates CSS modules or plain CSS to styled-components with theme support and TypeScript definitions.
- [accessibility-audit](https://github.com/anthropics/skills) - Audits frontend code for WCAG 2.1 AA compliance and generates fixes with proper ARIA attributes and semantic HTML.
- [storybook-generator](https://github.com/anthropics/skills) - Generates Storybook stories for components with controls, actions, decorators, and visual regression baselines.
- [responsive-design](https://github.com/anthropics/skills) - Converts desktop-first layouts to mobile-first responsive designs with proper breakpoints and fluid typography.

### Backend

- [api-design](https://github.com/anthropics/skills) - Designs RESTful APIs with OpenAPI specifications, consistent error handling, pagination, and authentication patterns.
- [graphql-schema](https://github.com/anthropics/skills) - Generates GraphQL schemas with resolvers, data loaders, subscriptions, and proper N+1 query prevention.
- [grpc-service](https://github.com/anthropics/skills) - Creates gRPC service definitions with Protocol Buffer schemas, server implementations, and client stubs.
- [microservice-scaffold](https://github.com/anthropics/skills) - Scaffolds production-ready microservices with health checks, graceful shutdown, structured logging, and circuit breakers.
- [orm-models](https://github.com/anthropics/skills) - Generates ORM models with migrations, relationships, validations, and query scopes for Prisma, SQLAlchemy, or TypeORM.
- [webhook-handler](https://github.com/anthropics/skills) - Implements webhook receivers with signature verification, idempotency, retry handling, and dead-letter queues.
- [caching-strategy](https://github.com/anthropics/skills) - Implements multi-layer caching with Redis, in-memory caches, and CDN strategies. Handles cache invalidation patterns.
- [rate-limiter](https://github.com/anthropics/skills) - Adds rate limiting to APIs using sliding window, token bucket, or leaky bucket algorithms with Redis backing.

### Fullstack

- [crud-generator](https://github.com/anthropics/skills) - Generates complete CRUD operations across frontend, backend, and database layers with proper validation and error handling.
- [auth-flow](https://github.com/anthropics/skills) - Implements authentication flows including OAuth 2.0, JWT, session management, MFA, and password reset.
- [realtime-sync](https://github.com/anthropics/skills) - Adds real-time data synchronization using WebSockets, Server-Sent Events, or polling with conflict resolution.
- [file-upload-pipeline](https://github.com/anthropics/skills) - Builds file upload systems with streaming, progress tracking, virus scanning, image processing, and cloud storage.

### Testing

- [tdd-workflow](https://github.com/anthropics/skills) - Follows strict test-driven development: writes failing tests first, implements minimum code to pass, then refactors. Enforces red-green-refactor.
- [test-generator](https://github.com/anthropics/skills) - Generates comprehensive test suites covering unit, integration, and edge cases. Supports Jest, Vitest, Pytest, and Go testing.
- [e2e-playwright](https://github.com/anthropics/skills) - Creates end-to-end tests using Playwright with page objects, fixtures, visual regression, and network interception.
- [snapshot-testing](https://github.com/anthropics/skills) - Sets up and manages snapshot tests for components, API responses, and database queries with proper update workflows.
- [mutation-testing](https://github.com/anthropics/skills) - Runs mutation testing analysis to identify weak tests and improve test suite effectiveness using Stryker or mutmut.
- [load-testing](https://github.com/anthropics/skills) - Creates load testing scripts with k6 or Artillery including scenarios, thresholds, and performance baseline tracking.
- [contract-testing](https://github.com/anthropics/skills) - Implements contract tests between services using Pact or similar frameworks with broker integration.

### Code Quality

- [refactor-patterns](https://github.com/anthropics/skills) - Identifies and applies refactoring patterns: extract method, replace conditional with polymorphism, introduce parameter object, and more.
- [code-review](https://github.com/anthropics/skills) - Performs thorough code review checking for bugs, security issues, performance problems, and style inconsistencies.
- [dependency-audit](https://github.com/anthropics/skills) - Audits project dependencies for security vulnerabilities, license compatibility, and outdated versions with upgrade paths.
- [tech-debt-tracker](https://github.com/anthropics/skills) - Identifies and catalogs technical debt with severity ratings, estimated effort, and suggested remediation approaches.
- [linter-config](https://github.com/anthropics/skills) - Generates and maintains linter configurations (ESLint, Ruff, Clippy) aligned with team coding standards.

### Mobile

- [react-native-component](https://github.com/anthropics/skills) - Creates React Native components with platform-specific code, gesture handling, animations, and accessibility.
- [swift-ui-views](https://github.com/anthropics/skills) - Generates SwiftUI views with proper state management, previews, and adaptable layouts.
- [flutter-widget](https://github.com/anthropics/skills) - Builds Flutter widgets with Riverpod state management, theming, and platform-adaptive behavior.

## Data & Analysis

### Data Science

- [data-pipeline](https://github.com/anthropics/skills) - Builds data processing pipelines with pandas or Polars, including data cleaning, transformation, validation, and output formatting.
- [statistical-analysis](https://github.com/anthropics/skills) - Performs statistical analysis with hypothesis testing, regression, ANOVA, and effect size calculations. Includes interpretation guidance.
- [notebook-generator](https://github.com/anthropics/skills) - Creates well-structured Jupyter notebooks with markdown documentation, clean code cells, and reproducible analysis workflows.
- [feature-engineering](https://github.com/anthropics/skills) - Generates feature engineering code for ML datasets including encoding, scaling, imputation, and feature selection.
- [etl-builder](https://github.com/anthropics/skills) - Creates ETL pipelines with data extraction from various sources, transformation logic, and loading into target systems.
- [time-series-analysis](https://github.com/anthropics/skills) - Performs time series decomposition, forecasting with ARIMA/Prophet, and anomaly detection with visualization.

### Visualization

- [codebase-visualizer](https://github.com/anthropics/skills) - Generates interactive HTML tree views of project file structure with collapsible directories, file sizes, and type-based color coding.
- [chart-generator](https://github.com/anthropics/skills) - Creates publication-quality charts using Matplotlib, Seaborn, or Plotly from data files with proper labels, legends, and styling.
- [dashboard-builder](https://github.com/anthropics/skills) - Builds interactive HTML dashboards with multiple chart types, filters, and responsive layouts. No framework required.
- [dependency-graph](https://github.com/anthropics/skills) - Generates visual dependency graphs for code modules, packages, or services using Mermaid or Graphviz.
- [architecture-diagram](https://github.com/anthropics/skills) - Creates architecture diagrams in Mermaid, PlantUML, or D2 from codebase analysis with service boundaries and data flows.

### Databases

- [schema-designer](https://github.com/anthropics/skills) - Designs database schemas with normalization, indexing strategy, and generates migration files for PostgreSQL, MySQL, or SQLite.
- [query-optimizer](https://github.com/anthropics/skills) - Analyzes SQL queries and suggests optimizations including index recommendations, query rewrites, and execution plan analysis.
- [seed-data-generator](https://github.com/anthropics/skills) - Generates realistic seed data for databases with proper relationships, constraints, and configurable volume.

## DevOps & Infrastructure

### CI/CD

- [github-actions](https://github.com/anthropics/skills) - Creates GitHub Actions workflows for CI/CD with caching, matrix builds, secrets management, and environment deployments.
- [gitlab-ci](https://github.com/anthropics/skills) - Generates GitLab CI/CD pipelines with stages, artifacts, caching, and environment-specific deployments.
- [release-automation](https://github.com/anthropics/skills) - Automates releases with semantic versioning, changelog generation, git tagging, and artifact publishing.
- [pr-workflow](https://github.com/anthropics/skills) - Creates pull requests with conventional titles, structured descriptions, linked issues, and appropriate reviewers.

### Cloud & Deployment

- [terraform-modules](https://github.com/anthropics/skills) - Generates Terraform modules with variables, outputs, state management, and multi-environment configurations for AWS, GCP, or Azure.
- [docker-compose](https://github.com/anthropics/skills) - Creates Docker Compose configurations for development environments with service dependencies, volumes, and networking.
- [kubernetes-manifests](https://github.com/anthropics/skills) - Generates Kubernetes manifests with deployments, services, ingresses, config maps, and horizontal pod autoscalers.
- [serverless-deploy](https://github.com/anthropics/skills) - Deploys serverless functions to AWS Lambda, Cloudflare Workers, or Vercel with proper configuration and environment setup.
- [nginx-config](https://github.com/anthropics/skills) - Generates Nginx configurations with reverse proxy, SSL termination, rate limiting, and caching headers.

### Containers & Orchestration

- [dockerfile-optimizer](https://github.com/anthropics/skills) - Optimizes Dockerfiles for smaller image sizes, faster builds, and security best practices with multi-stage builds.
- [helm-charts](https://github.com/anthropics/skills) - Creates Helm charts with templates, values files, hooks, and dependency management for Kubernetes deployments.
- [docker-security](https://github.com/anthropics/skills) - Scans Dockerfiles and container configurations for security issues, privilege escalation risks, and secret exposure.

### Monitoring & Observability

- [logging-setup](https://github.com/anthropics/skills) - Implements structured logging with correlation IDs, log levels, and integration with centralized logging platforms.
- [metrics-instrumentation](https://github.com/anthropics/skills) - Adds application metrics using Prometheus, OpenTelemetry, or StatsD with dashboards and alerting rules.
- [health-check-endpoints](https://github.com/anthropics/skills) - Creates comprehensive health check endpoints with liveness, readiness, and dependency status reporting.

## AI & ML

### Prompt Engineering

- [prompt-optimizer](https://github.com/anthropics/skills) - Iteratively refines prompts for better outputs. Tests variations, measures quality, and applies prompt engineering best practices.
- [system-prompt-builder](https://github.com/anthropics/skills) - Constructs system prompts with persona definition, constraints, output formatting, and few-shot examples.
- [evaluation-harness](https://github.com/anthropics/skills) - Builds evaluation frameworks for LLM outputs with rubrics, automated scoring, and regression detection.
- [prompt-template-library](https://github.com/anthropics/skills) - Manages reusable prompt templates with variable substitution, versioning, and A/B testing support.

### Model Integration

- [anthropic-sdk](https://github.com/anthropics/skills) - Integrates the Anthropic API with proper error handling, streaming, tool use, and token management.
- [openai-sdk](https://github.com/anthropics/skills) - Integrates OpenAI APIs with function calling, structured outputs, embeddings, and fine-tuning workflows.
- [embedding-pipeline](https://github.com/anthropics/skills) - Builds embedding pipelines for semantic search, clustering, and RAG applications with vector database integration.
- [rag-builder](https://github.com/anthropics/skills) - Creates Retrieval-Augmented Generation systems with document chunking, vector indexing, and context assembly.

### Agent Development

- [mcp-server](https://github.com/anthropics/skills) - Scaffolds Model Context Protocol servers with tool definitions, resource handling, and transport configuration.
- [claude-skill-builder](https://github.com/anthropics/skills) - Creates new Claude Code skills with proper frontmatter, supporting files, and testing workflows.
- [tool-definition](https://github.com/anthropics/skills) - Designs tool definitions for AI agents with input schemas, error handling, and documentation.
- [multi-agent-orchestrator](https://github.com/anthropics/skills) - Designs multi-agent systems with task decomposition, delegation, result aggregation, and error recovery.
- [tree-ring-memory](https://github.com/TerminallyLazy/tree-ring-memory-claude-plugin/blob/main/skills/tree-ring-memory/SKILL.md) - Adds local-first recall, capture, audit, and forgetting workflows for Claude Code memory.

## Security

- [security-audit](https://github.com/anthropics/skills) - Performs security audits checking for OWASP Top 10 vulnerabilities, injection flaws, authentication issues, and data exposure.
- [secrets-scanner](https://github.com/anthropics/skills) - Scans codebases for hardcoded secrets, API keys, credentials, and PII with remediation suggestions.
- [csp-generator](https://github.com/anthropics/skills) - Generates Content Security Policy headers based on application analysis with proper nonce and hash configurations.
- [dependency-vulnerability](https://github.com/anthropics/skills) - Scans dependencies for known CVEs with severity ratings, exploit details, and upgrade recommendations.
- [auth-hardening](https://github.com/anthropics/skills) - Reviews and hardens authentication and authorization implementations with best practices for session management and input validation.

## Business & Productivity

### Project Management

- [issue-creator](https://github.com/anthropics/skills) - Creates well-structured GitHub issues with acceptance criteria, labels, estimates, and linked requirements.
- [sprint-planner](https://github.com/anthropics/skills) - Breaks down features into sprint-sized tasks with story points, dependencies, and capacity planning.
- [changelog-generator](https://github.com/anthropics/skills) - Generates changelogs from git history with categorized entries following Keep a Changelog format.
- [roadmap-builder](https://github.com/anthropics/skills) - Creates product roadmaps with milestones, timelines, dependencies, and stakeholder alignment.

### Documentation

- [api-docs](https://github.com/anthropics/skills) - Generates API documentation from code with endpoint descriptions, request/response examples, and error codes.
- [readme-generator](https://github.com/anthropics/skills) - Creates comprehensive README files with installation, usage, API reference, and contributing sections.
- [adr-writer](https://github.com/anthropics/skills) - Writes Architecture Decision Records with context, decision, consequences, and status tracking.
- [runbook-creator](https://github.com/anthropics/skills) - Creates operational runbooks with step-by-step procedures, troubleshooting trees, and escalation paths.
- [onboarding-guide](https://github.com/anthropics/skills) - Generates developer onboarding documentation by analyzing the codebase structure, tooling, and conventions.

### Communication

- [standup-summary](https://github.com/anthropics/skills) - Generates daily standup summaries from git activity with completed, in-progress, and blocked items.
- [incident-report](https://github.com/anthropics/skills) - Creates incident reports with timeline, root cause analysis, impact assessment, and remediation action items.
- [rfc-template](https://github.com/anthropics/skills) - Writes Request for Comments documents with problem statement, proposed solution, alternatives, and migration plan.
- [meeting-notes](https://github.com/anthropics/skills) - Structures meeting notes with attendees, decisions, action items, and follow-up dates from raw notes.

## Design & Creative

### UI/UX

- [design-system](https://github.com/anthropics/skills) - Generates design system tokens, component APIs, and documentation from existing UI components.
- [wireframe-to-code](https://github.com/anthropics/skills) - Converts wireframe descriptions or images into functional HTML/CSS with responsive layouts and proper semantics.
- [color-palette](https://github.com/anthropics/skills) - Generates accessible color palettes with proper contrast ratios, dark mode variants, and CSS custom properties.
- [animation-library](https://github.com/anthropics/skills) - Creates CSS and JavaScript animations with easing functions, choreography, and reduced-motion alternatives.

### Content Creation

- [blog-post](https://github.com/anthropics/skills) - Writes technical blog posts with code examples, diagrams, SEO metadata, and proper markdown formatting.
- [social-media](https://github.com/anthropics/skills) - Creates social media content for developer audiences with proper formatting for Twitter, LinkedIn, and Dev.to.
- [newsletter-writer](https://github.com/anthropics/skills) - Drafts developer newsletter editions with curated links, summaries, and editorial commentary.
- [presentation-builder](https://github.com/anthropics/skills) - Creates slide decks in Markdown, reveal.js, or PPTX format with speaker notes and visual structure.

### Diagrams & Visuals

- [mermaid-diagrams](https://github.com/anthropics/skills) - Generates Mermaid diagrams for flowcharts, sequence diagrams, ERDs, state machines, and Gantt charts from code or descriptions.
- [ascii-art](https://github.com/anthropics/skills) - Creates ASCII art diagrams for documentation, architecture overviews, and terminal-friendly visuals.
- [svg-generator](https://github.com/anthropics/skills) - Creates SVG illustrations, icons, and diagrams with proper viewBox, accessibility attributes, and animations.
- [draw-io-export](https://github.com/anthropics/skills) - Generates draw.io compatible XML files for complex architecture and flow diagrams.

## Research & Writing

- [literature-review](https://github.com/anthropics/skills) - Synthesizes research papers on a topic with citation management, key findings, and gap analysis.
- [technical-writing](https://github.com/anthropics/skills) - Writes technical content following style guides (Google, Microsoft, Apple) with proper terminology and structure.
- [patent-analysis](https://github.com/anthropics/skills) - Analyzes patent documents, extracts claims, identifies prior art, and summarizes technical innovations.
- [competitive-analysis](https://github.com/anthropics/skills) - Performs competitive analysis of tools, frameworks, or products with feature matrices and recommendations.
- [tutorial-writer](https://github.com/anthropics/skills) - Creates step-by-step tutorials with prerequisites, code examples, expected outputs, and troubleshooting sections.
- [whitepaper-drafter](https://github.com/anthropics/skills) - Drafts technical whitepapers with abstract, methodology, findings, and conclusion sections.

## Workflow & Automation

- [git-workflow](https://github.com/anthropics/skills) - Implements git workflows with branching strategies, commit conventions, and merge/rebase policies.
- [commit-message](https://github.com/anthropics/skills) - Generates conventional commit messages by analyzing staged changes with proper type, scope, and description.
- [planning-with-files](https://github.com/OthmanAdi/planning-with-files) - Implements persistent markdown-based planning with task tracking, progress updates, and structured workflows.
- [monorepo-navigator](https://github.com/anthropics/skills) - Navigates monorepo structures, identifies package boundaries, and manages cross-package changes.
- [environment-setup](https://github.com/anthropics/skills) - Sets up development environments with proper tooling, configuration files, and dependency installation.
- [dotfiles-manager](https://github.com/anthropics/skills) - Manages dotfiles and development environment configuration with backup and sync capabilities.
- [migration-assistant](https://github.com/anthropics/skills) - Plans and executes code migrations between frameworks, languages, or major version upgrades with incremental verification.

## Language & Framework Specific

### Python

- [python-project](https://github.com/anthropics/skills) - Scaffolds Python projects with pyproject.toml, virtual environments, type hints, and modern tooling (Ruff, mypy, uv).
- [fastapi-service](https://github.com/anthropics/skills) - Generates FastAPI services with Pydantic models, dependency injection, middleware, and async database access.
- [django-patterns](https://github.com/anthropics/skills) - Implements Django patterns with models, views, serializers, permissions, and proper project structure.
- [pytest-suite](https://github.com/anthropics/skills) - Creates pytest test suites with fixtures, parametrization, mocking, and coverage configuration.
- [async-patterns](https://github.com/anthropics/skills) - Implements Python async patterns with asyncio, aiohttp, task groups, and proper error handling.

### JavaScript/TypeScript

- [typescript-strict](https://github.com/anthropics/skills) - Enforces strict TypeScript patterns with proper generics, discriminated unions, branded types, and utility types.
- [node-service](https://github.com/anthropics/skills) - Scaffolds Node.js services with Express or Fastify, middleware, error handling, and graceful shutdown.
- [eslint-rules](https://github.com/anthropics/skills) - Configures ESLint with flat config, custom rules, and framework-specific plugins for consistent code style.
- [monorepo-setup](https://github.com/anthropics/skills) - Sets up JavaScript monorepos with Turborepo or Nx, shared packages, and workspace configuration.
- [bun-runtime](https://github.com/anthropics/skills) - Configures projects for the Bun runtime with built-in bundler, test runner, and package management.

### Rust

- [rust-project](https://github.com/anthropics/skills) - Scaffolds Rust projects with proper Cargo.toml, module structure, error types, and CI configuration.
- [rust-error-handling](https://github.com/anthropics/skills) - Implements Rust error handling with custom error types, thiserror/anyhow, and proper propagation patterns.
- [rust-async](https://github.com/anthropics/skills) - Builds async Rust applications with Tokio, proper task management, cancellation, and backpressure handling.

### Go

- [go-service](https://github.com/anthropics/skills) - Scaffolds Go services with standard layout, interfaces, dependency injection, and idiomatic error handling.
- [go-testing](https://github.com/anthropics/skills) - Creates Go test suites with table-driven tests, test helpers, mocks, and benchmark functions.
- [go-concurrency](https://github.com/anthropics/skills) - Implements Go concurrency patterns with goroutines, channels, worker pools, and context cancellation.

### Other Languages

- [elixir-phoenix](https://github.com/anthropics/skills) - Generates Elixir Phoenix applications with LiveView, Ecto schemas, PubSub, and proper OTP supervision trees.
- [java-spring](https://github.com/anthropics/skills) - Creates Spring Boot applications with proper dependency injection, JPA repositories, and security configuration.
- [csharp-dotnet](https://github.com/anthropics/skills) - Scaffolds .NET applications with clean architecture, Entity Framework, and minimal API patterns.

## What Makes a Good Skill

A high-quality Claude Code skill should follow these principles:

### Structure

- **Single responsibility.** Each skill should do one thing well. A `deploy` skill deploys. A `test-generator` skill generates tests. Do not combine unrelated concerns.
- **Clear frontmatter.** Include a descriptive `name` and `description` so Claude knows when to load the skill. The description is your skill's discovery mechanism.
- **Concise SKILL.md.** Keep the main file under 500 lines. Move detailed reference material, API docs, and long examples to supporting files.
- **Supporting files.** Use `reference.md`, `examples/`, `templates/`, and `scripts/` directories for content that should only load on demand.

### Instructions

- **Be specific and actionable.** Vague instructions produce vague results. Tell Claude exactly what steps to follow, what patterns to use, and what output to produce.
- **Include examples.** Show Claude what good output looks like. Examples are worth more than paragraphs of description.
- **Define constraints.** Specify what Claude should NOT do. Constraints prevent common failure modes.
- **Use dynamic context.** The `!`command`` syntax lets you inject live data (git status, file contents, API responses) into the skill at runtime.

### Behavior

- **Use `disable-model-invocation: true`** for skills with side effects (deploy, publish, send messages). You do not want Claude auto-triggering these.
- **Use `context: fork`** for research or exploration skills that should run in isolation without consuming your conversation context.
- **Restrict tools with `allowed-tools`** to limit what Claude can do. A read-only research skill should not have write access.
- **Handle arguments.** Use `$ARGUMENTS`, `$0`, `$1` for flexible input. Document expected arguments in the skill description.

### Quality Checklist

- [ ] Does the skill have a clear, specific description?
- [ ] Does it follow a single responsibility?
- [ ] Are instructions actionable and specific?
- [ ] Are side-effect skills marked with `disable-model-invocation: true`?
- [ ] Is the SKILL.md under 500 lines?
- [ ] Does it include examples of expected output?
- [ ] Has it been tested with real-world use cases?

## Contributing

Contributions are welcome. Please read the [contribution guidelines](CONTRIBUTING.md) first.

To add a skill to this list:

1. Ensure the skill follows the quality guidelines in [What Makes a Good Skill](#what-makes-a-good-skill).
2. Submit a pull request with the skill added to the appropriate category.
3. Use the format: `- [skill-name](link) - Description of what the skill does, starting with a capital letter and ending with a period.`
4. Keep descriptions concise (one sentence).
5. Check that your contribution follows the [pull request template](.github/pull_request_template.md).

## License

[![CC0](https://licensebuttons.net/p/zero/1.0/88x31.png)](https://creativecommons.org/publicdomain/zero/1.0/)

To the extent possible under law, [Mingrath Mekavichai](https://github.com/mingrath) has waived all copyright and related or neighboring rights to this work.
