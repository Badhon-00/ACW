# parallel-decomposer-skill Evaluation Spec

## Binary Checks

### Check 1: Subtask Count
- **Command**: `grep -c "SUBTASK" SKILL.md`
- **Expected**: >= 1 (SKILL.md references subtask cards)

### Check 2: Frontmatter Complete
- **Command**: `python3 scripts/validate.py .`
- **Expected**: exit code 0

### Check 3: No Security Issues
- **Command**: `python3 scripts/security_scan.py .`
- **Expected**: exit code 0

### Check 4: References Exist
- **Command**: `test -f references/decomposition-patterns.md && test -f references/integration-guide.md && test -f references/dependency-checker.md`
- **Expected**: exit code 0

### Check 5: Invocation Header
- **Command**: `grep -q "^# /parallel-decomposer" SKILL.md`
- **Expected**: exit code 0

## Golden Cases

### Case 1: Code Review Decomposition
**Input**: `/parallel-decomposer Review this codebase for security vulnerabilities, performance issues, and code quality`

**Expected Behavior**:
- Produces 3-4 subtask cards
- Each card has: title, complexity, context, prompt, output format
- Subtasks are independent (logic review, security review, performance review, style review)
- Includes integration template at the end
- Suggests optimal worker count

**Status**: pending-first-green

### Case 2: Report Writing Decomposition
**Input**: `/parallel-decomposer Write a comprehensive report about AI trends covering technical, business, and ethical aspects`

**Expected Behavior**:
- Produces 3 subtask cards (technical, business, ethical)
- Each card includes full context about AI trends
- Prompts are copy-paste ready
- Integration template includes deduplication instructions
- Warns if any aspect requires sequential dependency

**Status**: pending-first-green

### Case 3: PR Review Decomposition
**Input**: `/parallel-decomposer Review this pull request for logic errors, style issues, and documentation completeness`

**Expected Behavior**:
- Produces exactly 3 subtask cards
- Cards cover: logic errors, style issues, documentation
- Each prompt explicitly scopes what to check and what to ignore
- Output format specified for each
- Integration template merges findings into unified review

**Status**: pending-first-green
