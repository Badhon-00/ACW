---
name: saas-competitor-research
description: Structured competitive intelligence — analyze a competitor's landing page, pricing, positioning, and gaps from their public website. Use when researching competitors or validating market entry.
---

# SaaS Competitor Research

Extract structured competitive intelligence from any competitor's public website. Drops a URL and gets back a full report: positioning, pricing breakdown, feature comparison, social proof audit, and opportunity gaps.

## When to Use This Skill

- Evaluating a new market before building
- Preparing for a pricing or positioning change
- Competitive analysis for investor updates or board decks
- Onboarding: quickly understanding a new competitor's playbook
- Weekly competitive monitoring (run against 2-3 competitors per session)

## What This Skill Does

1. **Positioning extract**: pulls the hero headline, target audience, and core value proposition
2. **Pricing audit**: lists every plan with billing cycles, anchor plan, free tier/trial, and hidden costs
3. **Feature table**: maps what's included per plan and flags bragged-about differentiators
4. **Gap detection**: identifies missing features you'd expect — these are your opportunities
5. **Social proof audit**: counts logos, testimonials, case studies, and cited metrics
6. **CTA analysis**: maps primary and secondary calls-to-action and where they lead

## How to Use

### Basic Usage

```
/research-competitor [COMPETITOR_URL]
```

### Advanced Usage

```
I'm building a [YOUR_PRODUCT] that competes with [COMPETITOR].
Go to [COMPETITOR_URL] and extract structured intelligence. Pay special attention to their pricing strategy and any features they brag about that we don't have.
```

## Example

**User**: "Go to https://cal.com and give me a competitive intelligence report."

**Output**:
```
## Cal.com Competitive Intelligence

### Executive Summary
- Open-source scheduling infra positioning ("Scheduling infrastructure for everyone")
- Freemium model with generous free tier, enterprise upsell via self-hosting
- Primary gap: no built-in CRM integration, no team analytics dashboard

### Pricing
| Plan | Price | Key Differentiator |
|------|-------|-------------------|
| Free | $0 | Unlimited event types |
| Teams | $15/user/mo | Round-robin, collective events |
| Enterprise | Custom | SSO, SLA, self-hosted |

### Gaps & Opportunities
1. No native CRM sync (Salesforce/HubSpot) — manual Zapier only
2. No team-level analytics or utilization reports
3. Limited payment integration options beyond Stripe
```

## Tips

- Use with `/web-fetch` or browser access enabled for best results
- Combine with `/audit-seo` for a complete competitive page audit
- Run weekly against your top 3 competitors to track positioning changes
- The "Gaps & Opportunities" section is where you find your differentiation
- Add a competitor's URL to your weekly review notes for tracking

## Common Use Cases

- Solo SaaS founders doing market research before building
- Product managers preparing competitive battle cards
- Growth teams analyzing competitor landing pages for conversion patterns
- Investors doing diligence on a market
- Indie hackers choosing which niche to enter
