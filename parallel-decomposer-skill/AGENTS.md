# parallel-decomposer-skill

## Purpose

A cross-platform agent skill for decomposing complex tasks into parallel subtasks optimized for multi-agent execution. Enables users to split work across multiple agent windows and merge results efficiently.

## Activation Triggers

This skill activates when the user expresses intent to:

- Decompose or break down a complex task into smaller pieces
- Execute work in parallel across multiple agents
- Split a project for concurrent processing
- Divide and conquer a large workload
- Run subtasks in separate agent windows simultaneously
- Parallelize task execution

Trigger phrases include:
- "decompose this task"
- "break into parallel tasks"
- "split this for multiple agents"
- "parallelize this work"
- "divide and conquer"
- "run in parallel"
- "multi-agent task split"
- "parallel subtasks"
- "concurrent execution"
- "task decomposition"

## Usage

1. User invokes `/parallel-decomposer` followed by a complex task description
2. Skill analyzes the task and identifies decomposition dimensions
3. Skill checks for dependencies between potential subtasks
4. Skill generates 3-7 structured subtask cards with copy-paste ready prompts
5. User copies each card to separate agent windows
6. After collecting results, user uses the provided integration template to merge outputs

## Input

Any complex task that:
- Has multiple independent aspects or components
- Can benefit from parallel analysis or creation
- Requires expertise in different domains
- Has sufficient context to distribute to parallel workers

## Output

- Structured subtask cards (3-7 cards)
- Complexity estimates and time projections
- Copy-paste ready prompts for each parallel agent
- Result integration template for merging outputs
- Risk warnings when parallelization is not recommended

## Cross-Platform Compatibility

This skill follows the Agent Skills Open Standard (SKILL.md) and works across:
- Claude Code, GitHub Copilot, VS Code Copilot
- Cursor, Windsurf, Cline, Trae
- OpenAI Codex CLI, Gemini CLI
- Goose, OpenCode, Roo Code, and 20+ other platforms

## Full Documentation

See `SKILL.md` for complete workflow, decomposition patterns, output rules, and examples.
