# Code Analyzer Suite — Evaluation Specification

## Binary Checks

### Structure Validation
- [ ] Skill directory contains SKILL.md, AGENTS.md, README.md, install.sh
- [ ] scripts/, references/, assets/ directories exist
- [ ] evals/ directory exists with eval spec

### Content Validation
- [ ] SKILL.md starts with "# /code-analyzer" trigger header
- [ ] SKILL.md frontmatter contains name: code-analyzer-skill
- [ ] AGENTS.md contains activation triggers and usage instructions
- [ ] All 5 dimension templates exist in assets/
- [ ] All reference documents exist in references/

### Script Validation
- [ ] All Python scripts compile without syntax errors
- [ ] generate_tasks.py accepts --request, --code, --file arguments
- [ ] consolidate_report.py accepts result files and --output
- [ ] check_pipeline.py validates all components
- [ ] run_evals.py supports --validate flag

### Functional Validation
- [ ] generate_tasks.py produces valid JSON output
- [ ] Dimension identification works for all 5 dimensions
- [ ] Language detection works for Python, JS, TS, Java, Go, Rust
- [ ] consolidate_report.py generates markdown report
- [ ] Severity ratings use Critical/High/Medium/Low consistently

## Golden Cases

### Case 1: Python SQL Injection
**Input:**
```python
def get_user(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query)
```

**Expected:**
- Security dimension identifies SQL injection (Critical)
- Performance dimension may note query efficiency
- Logic dimension checks input validation
- All dimensions produce structured output

### Case 2: JavaScript Async Issue
**Input:**
```javascript
async function processUsers() {
    const users = await getUsers();
    users.forEach(async user => {
        await sendEmail(user);
    });
    console.log("All emails sent");
}
```

**Expected:**
- Logic dimension identifies incorrect async sequencing
- Performance dimension notes blocking patterns
- Quality dimension checks error handling

### Case 3: Full Dimension Coverage
**Input:**
```
/code-analyzer Review this authentication module for all issues
```

**Expected:**
- All 5 dimensions are selected
- Each dimension generates a parallel task
- Consolidated report template is provided

### Case 4: File Path Input
**Input:**
```
/code-analyzer Analyze src/auth/login.ts for security vulnerabilities
```

**Expected:**
- TypeScript language detected
- Security dimension selected
- File path included in task context

### Case 5: Multi-Dimension Request
**Input:**
```
/code-analyzer Check this API for performance and code quality
```

**Expected:**
- Performance and Quality dimensions selected
- Other dimensions excluded
- Tasks formatted for parallel execution
