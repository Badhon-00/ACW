---
name: web-security-patterns
description: Auto-detects what web feature you're building and injects the correct security patterns. Covers auth, APIs, file uploads, database queries, payments, XSS, CSRF, IDOR, and secrets management for Next.js, React, and Express.
---

# Web Security Patterns

An AI agent skill that automatically detects web features in your code and injects security patterns BEFORE you ship. Designed for vibe coders building with Next.js, React, and Express.

## When to Use This Skill

- Building a login, signup, or authentication flow
- Creating API routes or server actions
- Implementing file uploads
- Writing database queries (Prisma, Drizzle, raw SQL)
- Adding payment/checkout flows with Stripe
- Building admin panels or dashboards
- Handling user-generated content (comments, posts, reviews)
- Adding search functionality
- Setting up webhooks
- Creating contact forms or newsletter signups
- Implementing password reset flows
- Setting up OAuth/social login
- Starting a new project from scratch
- Running a security audit on existing code

## What This Skill Does

1. **Auto-Detection**: Scans your code as you write and identifies which security pattern is needed
2. **Pattern Injection**: Inserts production-ready security code directly into your files
3. **Validation**: Checks existing code for common vulnerabilities (exposed secrets, SQL injection, XSS)
4. **Audit Mode**: Runs a comprehensive security audit with critical/warning/pass results

## How to Use

### Basic Usage

```
secure my app
```

The skill scans your project and reports all security issues with severity levels.

### Feature-Specific Usage

```
fix login security
check API routes
scan for secrets
fix file upload security
add security headers
```

## Security Patterns Covered

| Pattern | What it detects | What it fixes |
|---|---|---|
| Auth Flow | `bcrypt`, `signup`, `login` | Password hashing, rate limiting, session hardening |
| API Routes | `route.ts`, `handler` | Auth guard, Zod validation, IDOR prevention |
| File Uploads | `formData`, `multer` | Type/size/path validation, safe filenames |
| Database | `$queryRawUnsafe` | Parameterized queries |
| Payment | `stripe`, `checkout` | Server-side price validation, webhook signatures |
| User Content | `dangerouslySetInnerHTML` | DOMPurify XSS sanitization |
| Admin Panels | `/admin`, `dashboard` | Role-based access control |
| Webhooks | `webhook`, `signature` | HMAC verification, idempotency |
| Secrets | `.env`, `API_KEY` | Environment variable management |
| Bootstrap | New project | .gitignore, .env.example, security headers |

## Tips

- Drop `SKILL.md` into any AI coding tool project (Cursor, Copilot, Claude Code, Windsurf) — it activates automatically
- The skill works as a behavior modifier — it watches what you code and proactively suggests security improvements
- Use `security audit` for a full project scan before deploying to production
- Each security pattern can be triggered independently for targeted fixes

## Common Use Cases

- Vibe coders who build fast but need security guardrails
- Bootstrapped startups shipping MVPs without dedicated security
- Indie developers building SaaS products solo
- Teams using AI coding agents who want security built into their workflow
- Anyone deploying Next.js/React apps who wants automated security review

**Inspired by:** Hlaing Bwar's web security research and open-source security tools
