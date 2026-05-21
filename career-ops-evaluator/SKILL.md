---
name: career-ops-evaluator
description: Structured A-F job offer evaluation across 10 weighted dimensions. Before tailoring your resume to a JD, decide whether the offer is worth your time. Filter out offers below 4.0/5 before applying. Production implementation at github.com/santifer/career-ops (46K ⭐).
---

# Career-Ops Evaluator

A structured framework for evaluating job offers **before** applying — a filter, not a spray-and-pray tool. Most candidates spend hours customizing resumes for offers they shouldn't have applied to in the first place. This skill flips the workflow: rank offers first, then tailor only the top ones.

> **Companion skill**: pair this with [tailored-resume-generator](../tailored-resume-generator) — evaluate first, then tailor only for offers scoring ≥4.0.

## When to Use This Skill

- You have 5+ job postings in your pipeline and need to decide where to spend your application effort
- You are not sure whether an offer is "good enough" relative to your other options
- A recruiter reached out and you want a structured way to assess fit before responding
- You want to track applications over time with comparable, structured data
- You suspect ATS keyword-matching is making you waste effort on poor-fit roles
- You are negotiating and need a defensible scoring rationale ("Here is why offer A is a stronger match than offer B")

## What This Skill Does

Given a job description (JD) and your background, produces a structured evaluation across 10 weighted dimensions, returning a single A-F letter grade plus a 6-block analysis you can act on.

### The 10 evaluation dimensions

| Dim | What it measures | Default weight |
|---|---|---|
| 1. Role-level match | Is the seniority above, at, or below your current level? | 15% |
| 2. Domain alignment | How close is the problem space to your strongest narrative? | 15% |
| 3. Technical fit | Skill stack overlap with your CV | 10% |
| 4. Compensation | Total comp vs your floor / market band | 15% |
| 5. Geographic fit | Remote / hybrid / on-site vs your constraints | 8% |
| 6. Company stage | Pre-seed → Series C → Public, vs your risk appetite | 7% |
| 7. Manager / team signal | What does the hiring manager's profile tell you? | 8% |
| 8. Growth trajectory | Promotion path, mentorship, IC ladder | 7% |
| 9. Cultural fit | Public artifacts: blog, OSS, principles docs | 8% |
| 10. Exit optionality | Where does this role take you in 2-3 years? | 7% |

Weights are adjustable — a founder-track candidate weights company stage higher; a senior IC weights technical fit higher.

### Scoring

- Each dimension scored 1-5
- Weighted average → 0.0-5.0 score
- Letter grade mapping: **A** ≥4.5 / **B** 4.0-4.5 / **C** 3.5-4.0 / **D** 3.0-3.5 / **F** <3.0
- **Rule of thumb**: do not apply to offers scoring below 4.0 unless they unlock a specific narrative.

### The 6-block analysis output

For every evaluation the skill produces:

1. **Role summary** — what this role is in 3 sentences, including unstated implications
2. **CV match** — which 3-5 bullets from your CV are the strongest signals; what you should down-weight or hide
3. **Level strategy** — is this a stretch role, lateral, or step-down? What language signals their level expectation?
4. **Comp research** — market band for this title + location + stage, plus a recommended ask
5. **Personalization angle** — what would make your application memorable vs the median candidate
6. **Interview prep** — the 2-3 likely behavioral questions for this role; STAR+R stories you should rehearse

## How to Use

### Basic usage

Provide a JD and your background, ask for the evaluation:

```
Evaluate this offer with career-ops-evaluator.

Job Description:
[paste full JD including company, role, location, comp band if listed]

My Background:
- 10 years backend engineering, last 4 as Staff at FinTech unicorn
- Strong Python + Go; some Rust on the side
- Led platform migration for 200-engineer org
- Located in Madrid, prefer remote-first, EU timezone
- Floor comp: €130K base
```

The skill responds with:
- Per-dimension scores with one-line rationales
- Weighted total + letter grade
- The 6-block analysis
- A clear apply / skip / negotiate-first recommendation

### Comparing multiple offers

Paste up to 5 JDs at once. The skill returns a ranked comparison table plus per-offer evaluations, plus an "if you can only apply to 2 of these, pick X and Y because…" recommendation.

### Adjusting weights

If the defaults don't match your career stage, declare custom weights:

```
Use these dimension weights:
- Role-level match: 25%
- Domain alignment: 20%
- Technical fit: 5%
- Compensation: 10%
- Geographic fit: 5%
- Company stage: 15%
- Manager/team: 10%
- Growth trajectory: 5%
- Cultural fit: 3%
- Exit optionality: 2%
```

Total must sum to 100%. The skill validates and applies the override.

### Re-evaluating after recruiter call

After a recruiter screen you usually learn comp band, team size, and growth plans. Re-run the evaluation with the new signals — frequently a C becomes a B or vice versa.

```
Re-evaluate offer #3 with these updates from the recruiter call:
- Comp band confirmed: €160-180K base + 0.15-0.30% equity
- Team is currently 4 engineers, hiring to 8 by EOY
- Manager has been there 18 months, was previously at Stripe
- They will sponsor relocation but require 2 days/week in-office in Berlin
```

## Output Format

The skill returns a structured Markdown report:

```markdown
# Evaluation — [Company] / [Role]

**Overall**: 4.2/5 (B) — Strong apply

## Dimension scores

| # | Dimension | Score | Weighted | Rationale |
|---|---|---:|---:|---|
| 1 | Role-level match | 4 | 0.60 | Senior role, you are mid-Staff. Slight downlevel. |
| 2 | Domain alignment | 5 | 0.75 | Payments infra, exact match to your last 4 years. |
| ... |

## 6-block analysis

### 1. Role summary
[3 sentences]

### 2. CV match
- Strongest bullets to surface: ...
- Bullets to hide or rephrase: ...

[etc through all 6 blocks]

## Recommendation
Apply. Personalize the cover note around the platform migration story.
Negotiate from a base of €165K — that's the upper end of the market band.
```

## Why This Approach

**The asymmetric mistake**: most candidates optimize the wrong side of the funnel. They write 50 tailored resumes and apply to 50 offers, then wonder why they got 3 interviews. The honest math says they should have applied to 8 offers and gotten 5 interviews.

A structured filter changes the optimization. You spend 15 minutes per offer scoring it, then spend 90 minutes on the top 3 — instead of 30 minutes on each of 50.

This skill encodes the methodology that produced 740+ structured evaluations across an open-source production deployment ([github.com/santifer/career-ops](https://github.com/santifer/career-ops)), with the outcome of a Head of Applied AI role landed and dozens of contributors building on the same patterns.

## Provenance

- **Production reference**: [github.com/santifer/career-ops](https://github.com/santifer/career-ops) — 46,511 stars, MIT, 9 README languages
- **Case study**: [santifer.io/career-ops-system](https://santifer.io/career-ops-system) — 740+ offers evaluated, 100+ tailored CVs, 1 dream role landed
- **License**: Apache-2.0 (same as Composio's skills)

This SKILL.md is a self-contained methodology — it does not require installing career-ops to use. The skill teaches the framework; career-ops is one production implementation among many possible ones.
