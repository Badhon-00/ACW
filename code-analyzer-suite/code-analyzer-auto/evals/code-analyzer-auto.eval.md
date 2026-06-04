# Code Analyzer Auto Evaluation Spec

## Binary Checks

### Structure Validation
- [ ] Skill directory contains `SKILL.md`, `AGENTS.md`, `agents/openai.yaml`, `assets/`, `references/`, and `evals/`
- [ ] `assets/orchestration-brief-template.md` exists
- [ ] `references/orchestration-guide.md` exists

### Content Validation
- [ ] `SKILL.md` frontmatter contains `name: code-analyzer-auto`
- [ ] `SKILL.md` describes automatic dispatch first and manual fallback second
- [ ] `SKILL.md` limits auto triggering to orchestration, sub-agent, concurrent worker, or multi-agent review contexts
- [ ] `SKILL.md` says ordinary single-agent or manual reviews should use the parent skill
- [ ] `AGENTS.md` mentions orchestration brief, worker dispatch, and fallback prompts
- [ ] `agents/openai.yaml` matches the skill name and intent

## Golden Cases

### Case 1: Pull Request With Auto Dispatch
**Input**
```text
Use $code-analyzer-auto to review this pull request by dispatching Security, Performance, and Logic workers.
```

**Expected**
- Produces one orchestration brief
- Produces three worker specs
- Emphasizes automatic worker dispatch
- Includes one consolidated report format
- Does not tell the user to manually copy prompts as the primary path

### Case 2: Manual Fallback
**Input**
```text
Use $code-analyzer-auto to analyze src/auth/login.ts, but assume sub-agents are unavailable.
```

**Expected**
- Keeps the orchestration brief
- Emits copy-paste-ready worker prompts as fallback
- Preserves the same output format and merge expectations

### Case 3: Narrow Review
**Input**
```text
Use $code-analyzer-auto to review this function for security and logic issues.
```

**Expected**
- Selects Security and Logic only
- Does not force all five dimensions
- Produces a findings-first consolidated output shape

### Case 4: Trigger Boundary
**Input**
```text
Review src/auth/login.ts for security issues.
```

**Expected**
- Does not require the auto skill unless the user requested orchestration or sub-agents
- Routes ordinary single-agent review intent to the parent `code-analyzer-suite`
- Keeps manual worker prompts out of the main path
