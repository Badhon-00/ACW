---
name: automotive-ve-ai-skills-kit
description: Helps automotive value engineering teams convert VE/VAVE workflows, BOM and quotation reviews, opportunity registers, SOPs, adoption feedback, and evidence-backed claims into reusable AI Skills with human-review and overclaim guardrails.
---

# Automotive VE AI Skills Kit

Use this skill when working with automotive value engineering, VAVE, cost analysis, BOM review, quotation review, supplier collaboration, process documentation, or AI productivity pilots for engineering and procurement teams.

## When to Use This Skill

- A value engineering team needs to identify high-frequency tasks that are suitable for AI Skill automation.
- Cost analysts need to structure BOM, quotation, benchmarking, and meeting-note inputs into a VAVE opportunity register draft.
- Project managers need to convert VE review notes into action items, SOPs, FAQs, or weekly summaries.
- A team has piloted AI Skills and needs to analyze adoption, feedback, productivity impact, and iteration priorities.
- A candidate, consultant, or internal AI enablement lead needs a safe demo workflow for automotive VE AI productivity without proprietary data.
- A resume, release note, portfolio, or internal report needs claims checked against evidence links, PR status, CI status, and safe wording boundaries.

## What This Skill Does

1. **Mines VE workflows**: Extracts scenarios, repeated tasks, inputs, outputs, rework points, and human-judgment boundaries from interviews or meeting notes.
2. **Scores Skill candidates**: Ranks candidate workflows by frequency, time cost, standardization, risk control, data availability, visible benefit, and user willingness.
3. **Structures VAVE opportunities**: Converts BOM, quotation, benchmarking, and meeting evidence into opportunity-register drafts.
4. **Separates evidence types**: Labels conclusions as `Fact`, `Calculation`, `Hypothesis`, or `Needs confirmation`.
5. **Builds operating documents**: Turns workflow notes into SOPs, FAQs, checklists, version records, and best-practice examples.
6. **Tracks adoption**: Summarizes usage, time savings, rework, field completeness, satisfaction, and iteration backlog.
7. **Audits public claims**: Classifies project or resume claims as `resume-ready`, `boundary-only`, or `do-not-claim` based on evidence status and wording risk.

## How to Use

### Scenario Mining

```text
Use automotive-ve-ai-skills-kit to analyze these value engineering interview notes.
Extract high-frequency tasks, current pain points, Skill candidates, human-review steps,
and questions for business validation.
```

### VAVE Opportunity Register

```text
Use automotive-ve-ai-skills-kit to structure this BOM, quotation summary, benchmarking note,
and VAVE meeting note into an opportunity register draft. Do not fabricate missing cost,
supplier, quality, or engineering feasibility data.
```

### Adoption Review

```text
Use automotive-ve-ai-skills-kit to summarize this two-week AI Skill pilot.
Classify feedback, identify quality issues, calculate adoption metrics, and propose the next iteration backlog.
```

### Evidence Claim Audit

```text
Use automotive-ve-ai-skills-kit to audit these resume and portfolio claims.
For each claim, identify evidence status, source strength, safe wording, and claims that should not be made yet.
```

## Output Patterns

### Skill Candidate Map

```markdown
| Scenario | Role | Frequency | Pain | Input | Output | Skill Potential |
|---|---|---:|---|---|---|---|
```

### VAVE Opportunity Register

```markdown
| ID | Opportunity | Evidence Type | Potential Impact | Risk | Required Review | Next Action | Owner |
|---|---|---|---|---|---|---|---|
```

### Adoption Report

```markdown
| Metric | Before | After | Change | Status | Notes |
|---|---:|---:|---:|---|---|
```

### Evidence Claim Matrix

```markdown
| Claim | Source | Evidence Level | Verdict | Status | Claim Level | Evidence | Safe Wording | Boundary |
|---|---|---|---|---|---|---|---|---|
```

## Guardrails

- Do not invent costs, supplier quotes, material specs, engineering feasibility, quality risk, or confirmed savings.
- Mark uncertain items as assumptions or questions for human review.
- Route safety, quality, regulatory, warranty, supplier, and financial conclusions to the relevant human owner.
- Use redacted or synthetic data unless the user confirms an approved enterprise environment for proprietary data.
- Prefer small, frequent, low-risk workflows for first pilots instead of broad "AI assistant" concepts.
- Do not describe open PRs as merged, accepted, or contributor status.
- Treat self-reported or marketing-only evidence as weak until backed by a platform record, repository artifact, or independent source.

## Example

**User**:

```text
We have a bracket BOM, a supplier quotation summary, and VAVE meeting notes.
Create an opportunity register draft for review.
```

**Output**:

```markdown
# VAVE Opportunity Register Draft

## Data Completeness

| Required Field | Status | Notes |
|---|---|---|
| BOM | Provided | Simplified part list |
| Quotation breakdown | Partial | Supplier margin not split |
| Engineering validation | Missing | Needs R&D review |

## Opportunity Register

| ID | Opportunity | Evidence Type | Potential Impact | Risk | Required Review | Next Action | Owner |
|---|---|---|---|---|---|---|---|
| OPP-001 | Evaluate part-count reduction | Hypothesis | May reduce welding and handling | Strength, tooling, validation lead time | R&D, Quality, Manufacturing | Run structural review | VAVE/R&D |
```

## Tips

- Start with interviews and meeting notes before writing Skills.
- Convert repeated work into small Skills with clear trigger conditions.
- Keep expert judgment explicit instead of hiding it inside the AI output.
- Track adoption with both productivity and quality metrics.
- Keep examples synthetic when sharing publicly.

## Common Use Cases

- Automotive VAVE workshop preparation
- BOM and quotation review support
- Cost-opportunity register drafting
- VE meeting action-item extraction
- SOP and best-practice documentation
- AI Skill adoption reporting
- Resume, portfolio, release-note, and management-summary claim auditing

**Inspired by:** The open-source [Automotive VE AI Skills Kit](https://github.com/onyx679/automotive-ve-ai-skills-kit) portfolio project, currently published as v0.3.0 with five standalone Skills, four Python workflow scripts, generated examples, and CI-backed tests.
