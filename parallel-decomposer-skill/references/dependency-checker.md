# Dependency Checker Guide

## Types of Dependencies

### 1. Input Dependencies
Subtask B needs Subtask A's output as input.

**Detection**: Ask "Can this subtask start with only the original task description?"

**Resolution**:
- Merge into sequential subtask
- Or create Phase 1 (A) -> Phase 2 (B+C parallel)

### 2. Resource Dependencies
Two subtasks need the same exclusive resource.

**Detection**: Ask "Do both subtasks need to modify the same file/system?"

**Resolution**:
- Split by read-only vs read-write access
- Or merge if resource contention is high

### 3. Logical Dependencies
Subtask B's correctness depends on Subtask A's decisions.

**Detection**: Ask "If A reaches a different conclusion, does B's work become invalid?"

**Resolution**:
- Merge dependent subtasks
- Or make B broader to handle multiple A outcomes

### 4. Temporal Dependencies
Subtask B must happen after Subtask A due to external constraints.

**Detection**: Ask "Is there a deadline, approval, or external event ordering these?"

**Resolution**:
- Respect the sequence
- Parallelize only the time-independent portions

## Dependency Detection Questions

Before finalizing decomposition, answer for each subtask pair (A, B):

1. Can A and B start simultaneously?
2. Do A and B produce conflicting outputs?
3. Would A's failure invalidate B's work?
4. Do A and B need to communicate during execution?
5. Is there a natural order that reduces total effort?

## Handling Hidden Dependencies

### Discovery Phase
- Ask the user: "Are there any parts of this task that must happen in order?"
- Review the task for words like "then", "after", "once", "before"
- Check for handoffs between people, systems, or stages

### Documentation Phase
If dependencies cannot be eliminated, document them:

```
DEPENDENCY ALERT:
- Subtask 3 depends on Subtask 1's output (architecture decision)
- Recommendation: Run Subtask 1 first, then run Subtasks 2-4 in parallel
- Alternative: Merge Subtasks 1 and 3 if delay is unacceptable
```

## Dependency Matrix Template

```
          | Subtask 1 | Subtask 2 | Subtask 3 | Subtask 4 |
----------|-----------|-----------|-----------|-----------|
Subtask 1 |     -     |  None     |  Output   |  None     |
Subtask 2 |  None     |     -     |  None     |  Shared   |
Subtask 3 |  Input    |  None     |     -     |  None     |
Subtask 4 |  None     |  Shared   |  None     |     -     |

Legend: None = Independent, Input/Output = Data dependency, Shared = Resource dependency
```
