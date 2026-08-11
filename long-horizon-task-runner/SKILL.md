---
name: long-horizon-task-runner
description: Runs extended goals through LongHorizon-Harness when work needs multiple GUI or CLI rounds, fresh executor contexts, durable verified state, and an independent auditor. Use for complex tasks that cannot be completed reliably in one agent session.
---

# Long Horizon Task Runner

Use [LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness) to coordinate a Manager, fresh-context Executor, and independent Auditor around one extended goal. Only progress accepted by the Auditor should be reported as verified.

## When to Use This Skill

- A task will take many agent rounds or may outlive one context window
- Work spans terminal commands and desktop applications
- Progress must survive a failed or rejected round
- A separate role should inspect artifacts, logs, interfaces, or tests
- The user wants a durable run record and explicit remaining-work state

Do not use it for a one-step request, a cheap recurring cron job, or work whose success criteria are still unclear. Do not delegate security, authentication, payments, production infrastructure, or destructive operations without explicit human approval.

## What This Skill Does

1. Confirms the goal, workspace, boundaries, backend, and stopping conditions
2. Runs read-only environment diagnostics before making changes
3. Creates a reviewable task file and project configuration
4. Starts a bounded Manager → Executor → Auditor loop
5. Reports verified results, remaining work, and the run-record location

## How to Use

### Basic CLI Task

```text
Run this repository audit as a long-horizon task. Use Codex, cap it at 12 rounds,
and require tests or file evidence before accepting any finding.
```

### Mixed Desktop and CLI Task

```text
Use a long-horizon run to clean this spreadsheet, generate the charts, and verify
the saved workbook. Stop for approval before installing a computer-use plugin.
```

## Instructions

### 1. Confirm the Run Contract

Before starting, make these items explicit:

- **Goal**: one outcome, not a list of unrelated projects
- **Workspace**: the exact directory the agents may operate in
- **Acceptance criteria**: observable checks for completion
- **Allowed actions**: commands, applications, and external services in scope
- **Forbidden actions**: destructive or high-risk changes that require a human
- **Backend**: `claude_code` or `codex`
- **Interface**: CLI-only or GUI + CLI
- **Budget**: maximum rounds and any time or cost limit
- **Stop conditions**: blocked, repeated failure, missing permission, or budget reached

Do not interpret a request to run the harness as approval to install software, alter OS permissions, expose a remote dashboard, or perform destructive actions.

### 2. Run Read-Only Preflight Checks

Check whether the CLI is present:

```bash
command -v lh-harness
lh-harness --version
```

If it is missing, show the supported installation command and ask for permission before running it:

```bash
uv tool install lh-harness
# Alternative: pip install lh-harness
```

Then run the read-only diagnostic:

```bash
lh-harness doctor
```

Stop if the chosen agent runtime is unavailable or broken. For GUI work, explain which computer-use plugin is needed and obtain approval before `lh-harness plugin install ...`; plugin installation may change agent configuration and require manual OS permissions.

### 3. Prepare the Workspace and Task

Operate only in the confirmed workspace. For code-changing tasks, prefer a disposable worktree or sandbox because the local harness is not filesystem isolation.

If `.lh-harness/config.toml` does not exist, ask before creating it:

```bash
lh-harness init
```

Never use `lh-harness init --force` over an existing configuration without approval. Review the generated configuration, especially `workspace`, `max_rounds`, role backends, timeouts, MCP paths, and dashboard settings.

Write the goal to a task file without secrets:

```markdown
# Goal
[One measurable outcome]

## Acceptance criteria
- [Observable check 1]
- [Observable check 2]

## Allowed actions
- [Explicitly allowed tools and systems]

## Forbidden or approval-gated actions
- [Destructive, external, or high-risk action]

## Evidence required
- [Tests, screenshots, saved files, logs, or other proof]

## Stop conditions
- Stop when blocked, when approval is required, or when the round budget is reached.
```

### 4. Start a Bounded Run

Use the selected backend and agreed round cap:

```bash
lh-harness run \
  --task @task.md \
  --agent codex \
  --max-rounds 12
```

Use `--agent claude_code` when requested. Prefer the agent CLI's existing login or a protected environment variable; do not place API keys in the task file, config file, command history, or run report.

The local dashboard can provide visibility and human approval:

```bash
lh-harness run --task @task.md --agent codex --dashboard
```

Keep the dashboard bound to loopback unless the user explicitly requests remote access and provides an authentication plan. A remote bind requires an auth token.

### 5. Close With Verified State Only

At the end, use the run's final response and report path printed by the CLI. Do not turn an Executor claim into a completion claim unless the Auditor accepted it.

Return:

```markdown
## Long-horizon run
- Run ID: ...
- Workspace: ...
- Backend: ...
- Round budget: ...
- Status: complete / incomplete / blocked

## Verified results
- ...

## Remaining or rejected work
- ...

## Evidence and run record
- ...
```

Preserve the run directory under `.lh-harness/runs/<run-id>/` unless the user asks to remove it.

## Failure Handling

- **`doctor` fails**: report the failing prerequisite; do not start the run
- **GUI plugin is absent**: continue only if the task can be CLI-only, otherwise request setup approval
- **Auditor rejects a round**: keep the rejection evidence and let the Manager re-plan
- **Repeated failure**: stop at the agreed threshold instead of silently extending the budget
- **Approval required**: pause and state the exact action, target, and consequence
- **Round limit reached**: report verified progress and remaining work as incomplete

## Safety Notes

- The Auditor is an evidence gate, not a permission grant
- Use explicit allowlists and deny sensitive paths such as secrets, credentials, production infrastructure, payments, and authentication
- Never disable tests or weaken acceptance criteria to make a run pass
- Never expose the dashboard beyond localhost without authentication
- Keep task text and persistent state free of credentials and personal data

## Example Outcome

**User**: "Run a multi-round documentation migration and verify every internal link."

**Result**: The skill records the acceptance criteria, checks the environment, initializes a bounded run, and returns only link checks and migrated files accepted by the Auditor. Rejected pages and unresolved links remain listed as incomplete with their evidence paths.

**Inspired by:** [AMAP-ML/LongHorizon-Harness](https://github.com/AMAP-ML/LongHorizon-Harness)
