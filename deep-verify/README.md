# 🔍 deep-verify — Adversarial Code Verification for the AI Era

> **"Almost right" is the most dangerous kind of wrong.**

AI writes code that looks perfect. It compiles. Tests pass. "LGTM" 🚢. Then it explodes
in production at 3 AM.

**deep-verify** is a Claude Code skill that catches the "almost right" bugs before they
find your users. It uses adversarial thinking across six dimensions to find the hidden
issues that pass superficial tests but fail in production.

---

## 📊 The Problem

| Stat | Source |
|------|--------|
| **66%** of developers frustrated with "almost right" AI code | Stack Overflow Survey 2025 |
| **1.7x** more bugs in AI-generated code vs human code | CodeRabbit (470 open-source PRs) |
| **154%** increase in PR size since AI adoption | Google DORA Report 2025 |
| **46%** of developers don't trust AI accuracy | Stack Overflow Survey 2025 |
| **45%** of senior engineer time spent on code review (was 25%) | 10x.pub industry survey |
| **91%** increase in code review time with 90% AI adoption | Google DORA Report 2025 |

AI made developers faster at writing code. It made code review the bottleneck. And
"almost right" AI code — which looks correct but hides subtle defects — is the #1
developer frustration.

## 🎯 What deep-verify Does

deep-verify is an **adversarial code auditor**. Unlike traditional linters or code
review tools that check style and patterns, deep-verify:

1. **Thinks like an attacker** — actively hunts for what's wrong, not what's right
2. **Targets AI-common failures** — calibrated against a catalog of real AI bug patterns
3. **Runs six dimensions** of verification, not just one
4. **Provides concrete fixes** — every issue comes with exact code corrections

### The Six Dimensions

| # | Dimension | Key Question |
|---|-----------|-------------|
| 1 | **Intent vs. Implementation** | Does the code actually do what it claims? |
| 2 | **Edge Case Discovery** | What happens with null, empty, extreme inputs? |
| 3 | **Security Audit** | SQL injection? XSS? Missing auth? Exposed secrets? |
| 4 | **Performance Analysis** | N+1 queries? O(n²)? Memory leaks? |
| 5 | **Business Logic Integrity** | Does it respect transaction boundaries, money rules, data consistency? |
| 6 | **Error Handling & Resilience** | What happens when the network fails at 3 AM? |

## 🚀 Quick Start

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/deep-verify.git

# Install to Claude Code
cp -r deep-verify ~/.claude/skills/deep-verify
```

Or install via the Claude Code skill marketplace (when available).

### Usage

Just ask Claude to verify your code:

```
/verify this PR
```

Or use natural language:

```
"Deep verify the changes in my last commit"
"Audit this diff for AI-common bugs"
"Check if this code is production-ready"
"Is there anything wrong with this implementation?"
"Review this PR with adversarial analysis"
```

### Example Output

> # Deep Verify Report
>
> ## Overall Verdict
> 🔴 **BLOCK** — 3 CRITICAL issues found. Do NOT merge.
>
> ### [CRITICAL] Missing Transaction Boundary
> - **Location:** `src/payments/processor.ts:142-158`
> - **Pattern:** Pattern 1.1 (Missing Transaction Boundaries)
> - **Failure Scenario:** Network fails between charge and save —
>   customer is charged but order is lost. $12,400 in refunds.
> - **Fix:** Wrap all operations in a database transaction with rollback.
>
> ### [CRITICAL] SQL Injection in Search Endpoint
> - **Location:** `src/api/search.ts:47`
> - **Pattern:** Pattern 3.1 (SQL Injection via String Interpolation)
> - **Failure Scenario:** Attacker extracts entire user table via
>   `'; SELECT * FROM users; --`
> - **Fix:** Use parameterized queries instead of string interpolation.
>
> ## Severity Summary
> | Severity | Count |
> |---|---|
> | CRITICAL | 3 |
> | HIGH | 2 |
> | MEDIUM | 4 |
> | LOW | 1 |
> | **TOTAL** | **10** |

## 🏗️ How It Works

deep-verify uses a three-layer architecture:

1. **SKILL.md** — the core instructions that transform Claude into an adversarial
   code auditor with specific mindset, process, and output format
2. **AI Bug Pattern Catalog** — a growing reference of real AI-generated bug patterns
   (transactions, N+1 queries, SQL injection, race conditions, etc.)
3. **Six-Dimension Framework** — comprehensive verification checklists for each
   dimension of analysis

## 📁 Project Structure

```
deep-verify/
├── SKILL.md                              # Core skill instructions
├── README.md                             # This file
├── references/
│   ├── ai-bug-patterns.md               # Catalog of AI-common bug patterns
│   ├── verification-dimensions.md       # Detailed six-dimension framework
│   └── report-template.md               # Standardized report output format
└── CLAUDE.md                            # Project documentation for contributors
```

## 🤝 Contributing

Found a new AI bug pattern? Want to improve the verification framework? PRs welcome!

See [CLAUDE.md](CLAUDE.md) for development guidelines.

## 📜 License

MIT — use it, fork it, share it, build on it.

## 🌟 Why This Matters

We're in the "almost solved" phase of AI-assisted development. Code generation is fast.
Code verification is the bottleneck. Tools that help humans catch AI's blind spots are
not just productivity boosters — they're safety infrastructure.

deep-verify is one piece of that infrastructure. The first tool purpose-built to bridge
the gap between "almost right" and "production-ready."

---

*Built with data from Stack Overflow Developer Survey 2025, Google DORA Report 2025,
CodeRabbit's analysis of 470 open-source PRs, and countless 3 AM production incidents.*
