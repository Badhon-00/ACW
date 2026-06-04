# Result Integration Guide

## Integration Strategies

### 1. Simple Concatenation
Best for: Independent sections with no overlap

```
Combine results in order:
- Add a table of contents
- Preserve each subtask's output as a section
- Add cross-references where sections relate
```

### 2. Deduplication Merge
Best for: Overlapping analysis from multiple angles

```
Steps:
1. Identify overlapping findings across subtasks
2. Keep the most detailed version of each finding
3. Attribute unique findings to their source subtask
4. Flag any contradictions for human review
```

### 3. Hierarchical Synthesis
Best for: Different levels of detail (executive + technical)

```
Structure:
- Executive Summary (from high-level subtask)
- Detailed Analysis (from deep-dive subtasks)
- Appendices (from reference-gathering subtasks)
```

### 4. Conflict Resolution
Best for: Contradictory findings from parallel analysis

```
Process:
1. List all contradictions explicitly
2. Evaluate evidence quality for each position
3. Document the resolution with reasoning
4. Flag unresolved conflicts for human decision
```

## Integration Prompt Templates

### Standard Integration

```
I have {N} parallel analysis results below. Please:

1. Read all results
2. Remove duplicate findings
3. Organize into a coherent structure
4. Resolve any contradictions with reasoning
5. Produce a unified {output_format}

RESULTS:
{paste all subtask outputs here}
```

### Technical Integration

```
I received parallel technical reviews of the same codebase. Please merge:

1. Combine all issues into a single prioritized list
2. Group by severity (Critical/Warning/Suggestion)
3. Deduplicate overlapping findings
4. For each issue, include: location, description, fix suggestion
5. Output as a structured markdown report

REVIEWS:
{paste all reviews here}
```

### Creative Integration

```
I have parallel creative outputs for the same project. Please:

1. Identify the strongest elements from each output
2. Ensure consistent tone and voice throughout
3. Fill gaps where one output is stronger than others
4. Produce a unified draft that feels cohesive

OUTPUTS:
{paste all creative outputs here}
```

## Quality Checklist

After integration, verify:
- [ ] No duplicate content remains
- [ ] All subtask outputs are represented
- [ ] Contradictions are resolved or flagged
- [ ] Tone and style are consistent
- [ ] Cross-references between sections work
- [ ] The whole is greater than the sum of parts
