# CLAUDE.md — deep-verify Project Guide

## What This Project Is

A Claude Code skill for adversarial code verification, optimized for catching bugs that
AI code generators commonly introduce. The skill transforms Claude into an adversarial
auditor that hunts for "almost right" bugs across six verification dimensions.

## Project Structure

```
deep-verify/
├── SKILL.md                         # The skill — what Claude reads when invoked
├── README.md                        # Public-facing documentation
├── CLAUDE.md                        # This file — contributor guide
└── references/
    ├── ai-bug-patterns.md           # Catalog of AI-common bug patterns (growing)
    ├── verification-dimensions.md   # Six-dimension framework details
    └── report-template.md           # Standardized output format
```

## How the Skill Works

1. User triggers the skill (e.g., "verify this PR")
2. Claude reads SKILL.md → becomes an adversarial auditor
3. Claude reads `references/ai-bug-patterns.md` to calibrate detection
4. Claude reads `references/verification-dimensions.md` for detailed checklists
5. Claude analyzes the code across all six dimensions
6. Claude outputs a structured report using `references/report-template.md`

## Key Design Decisions

### Why Six Dimensions?
Each dimension targets a category of bugs where AI generation has known weaknesses.
Combined, they cover the spectrum from "obvious" (missing null checks) to "subtle"
(business rule violations that look technically correct).

### Why Adversarial?
Traditional code review asks "does this look right?" Adversarial review asks "how could
this fail?" The adversarial mindset catches issues that pattern-matching misses.

### Why a Bug Pattern Catalog?
AI generates the SAME bug patterns repeatedly. By cataloging them, we calibrate the
auditor's detection instincts. The catalog is living documentation — add new patterns
as you discover them.

## Contributing

### Adding a New Bug Pattern
1. Find a real AI-generated bug (production incident, code review, research)
2. Document it in `references/ai-bug-patterns.md`:
   - Pattern name and category
   - Frequency and severity rating
   - Before (bad) and After (fixed) code examples
   - What to look for during verification
3. Add cross-references from the relevant dimension checklist

### Improving a Dimension
1. Review real verification runs — what did the auditor miss?
2. Add checklist items to `references/verification-dimensions.md`
3. Test against known buggy code to verify detection

### Tuning the Skill Prompt
The SKILL.md file balances:
- **Adversarial intensity** — too aggressive = false positives; too soft = misses
- **Instruction detail** — too specific = fragile; too vague = inconsistent
- **Length** — keep under 500 lines; push details to reference files

## Testing

Manual testing workflow:
1. Find or create code with known AI-generated bugs
2. Run deep-verify against it
3. Check: did it find all the bugs? Any false positives?
4. Tune SKILL.md or references as needed

## Research References

- Stack Overflow Developer Survey 2025 (49,000 developers, 177 countries)
- Google DORA Report 2025
- CodeRabbit: AI-generated code analysis (470 open-source PRs)
- Sonar 2025 State of Code Report (153M+ lines analyzed)
- GitClear: Code duplication analysis
- Ivan Turkovic: "Almost Solved Is the Most Dangerous Phase in Engineering" (March 2026)
- 10x.pub: "Code Review Is Now the Bottleneck" forum thread
- BigIdeasDB: 149,000+ user complaints analyzed
