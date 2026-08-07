---
name: resume-job-fit-checker
description: Compares a resume against a single job posting and produces an honest, evidence-based fit assessment - what clearly matches, what's a hidden match in different wording, and what's a real gap.
---

# Resume Job Fit Checker

Before spending an hour tailoring a resume or writing a cover letter, most people just want an honest answer to one question: am I actually qualified for this, or am I wasting my time? This skill answers that using only the requirements actually stated in the job posting and the experience actually present in the resume - no guessing, no invented experience.

## When to Use This Skill

- Deciding whether a job posting is worth applying to before spending time tailoring a resume
- Getting an honest read on how well a resume matches a specific role
- Screening multiple postings to prioritize which to apply to first

## What This Skill Does

1. **Extracts requirements**: Reads the job posting and separates must-haves, nice-to-haves, and implied priorities (what the posting emphasizes most).
2. **Maps the resume**: Classifies every requirement as a Clear match, Hidden match (same experience, different wording), or Gap.
3. **Delivers an honest verdict**: Produces a short Fit Summary and a Keyword Gap Analysis table - no flattery, no invented experience.

## How to Use

### Basic Usage

Paste a job posting and your resume, then ask: "Does my resume match this job?"

### Advanced Usage

Paste the full job posting text (including the "nice to have" section) alongside your resume, and ask Claude to flag any hard requirement gaps before you spend time tailoring the rest of the application.

## Example

**User**: "I'm applying for this Senior Project Manager role at a payments company. Here's the job posting and my resume - does my resume actually match this role?"

**Output**:

```
# Fit Check: Senior Project Manager at [Company]

## Fit Summary
Worth applying with tailoring. Core PM experience is close but slightly under the stated 5-year bar, cross-functional leadership is a clear match, and payments/fintech background is a real gap (listed as preferred, not required).

## Keyword Gap Analysis
| Requirement | Status | Evidence |
|---|---|---|
| 5+ years PM experience | Hidden match | 4 years, close but under the stated bar |
| Cross-functional leadership | Clear match | Coordinated engineering, design, and sales |
| Payments/fintech background | Gap | Not present in resume |
```

**Inspired by:** the pre-application gap-check most job seekers do manually before tailoring a resume.

## Tips

- Always require both the job posting and the resume before starting - the skill doesn't work from a URL or a partial resume.
- Keep the tone honest, not encouraging. A fit check that flatters every resume isn't useful.
- Don't extend into resume rewrites, cover letters, or interview prep - that's intentionally out of scope for this skill.

## Common Use Cases

- Deciding whether a job posting is worth the time to apply to
- A quick first pass before spending an hour tailoring a resume
- Screening multiple postings to prioritize which to apply to first
