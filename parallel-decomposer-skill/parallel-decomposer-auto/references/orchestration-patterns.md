# Orchestration Patterns

Prefer automatic dispatch when:
- workers can run independently
- the runtime supports sub-agents or concurrent tasks
- the merge cost is lower than the execution speedup

Prefer sequential phases when:
- workers would need to edit the same files without clear ownership
- later work depends on unresolved design or API decisions
- correctness depends on one worker's output before another can start

Prefer manual fallback when:
- workers cannot be started automatically
- the user wants to inspect worker prompts first
- the runtime does not preserve shared context reliably

When automatic dispatch is available, keep manual copy-paste prompts out of the primary workflow and mention them only as a fallback.
