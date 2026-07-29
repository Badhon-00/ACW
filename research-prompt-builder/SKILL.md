---
name: research-prompt-builder
description: Builds a deep research prompt you paste into Perplexity or ChatGPT. Asks 4 clarifying questions, writes a full search plan with exact queries and fallback rules, and runs a 9.5/10 quality gate before handing it over. Can also run the research itself. Works on Claude.ai and Claude Code.
allowed-tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - AskUserQuestion
---

# Research Master Prompt

A senior research analyst skill for product intelligence, market sentiment, competitive analysis, and due diligence. Uses web search and fetch to gather real data before making any claims.

No guessing. No fabricated quotes. No assumptions dressed up as findings. Every claim must trace to a source actually found.

## When to Use This Skill

- Evaluating whether to buy, subscribe to, or adopt a tool
- Competitive analysis before building in a space
- Market entry research (what do users actually want?)
- Due diligence on a company, investment, or partnership
- Content creation that needs cited, real-world evidence
- Any research task where stale or invented information would cause real harm

## What This Skill Does

Runs in three phases:

**Phase 1, Discovery.** Asks four clarifying questions before touching a search: what are you researching, what is it for, what time window matters, and how deep should this go. No research starts until all four are answered.

**Phase 2, Execution.** Runs up to 5 rounds of targeted searches covering direct sentiment, platform-specific sources (Reddit, HN, G2, Capterra, YouTube), switching signals, feature intelligence, and industry analysis. Scales search count to the chosen depth tier.

**Phase 3, Report.** Produces a 10-section markdown report saved to file: sentiment overview, what users love, what users hate, feature analysis, user segments, competitor landscape, trends, sources and methodology, and a final verdict with recommendation.

**Bonus mode: Prompt quality gate.** When generating a research prompt for another tool (Perplexity, ChatGPT, etc.), scores the draft 1-10 across 5 dimensions and iterates until the average hits 9.5. Will not deliver below that threshold.

## How to Use

### Basic Usage

```
Research [product/company/tool] for a purchase decision. Last 6 months. Standard depth.
```

### Advanced Usage

```
Research [product] for competitive analysis. Last 12 months. Deep Dive.
```

### Generate a Research Prompt for Another Tool

```
Generate a research prompt I can run in Perplexity for [topic]. Stack context: [your tech].
```

## Example

**User**: "Research Notion for a purchase decision. Last 6 months. Standard depth."

**Output** (10-section report saved to `notion-research-2026-05.md`):

```
Section 1: Research Summary
Subject: Notion | Purpose: Purchase decision | Time Window: 6 months
Sources Reviewed: 23 | Confidence: High

Section 2: Sentiment Overview
Overall: Mixed. Positive for individuals and small teams, critical for enterprise.
Reddit: Negative lean. Key theme: performance and offline limitations.
G2/Capterra: Positive lean. Key theme: flexibility and template ecosystem.
...

Section 10: Final Verdict
Notion works well for solo users and design-oriented teams who value flexibility
over performance. Enterprise adoption is consistently frustrated by slow load
times on large databases, no native offline mode, and permission complexity.

Recommendation: Conditional. Buy if your team is under 20 and won't build
databases over 10k rows. Skip if you need fast load times, robust offline,
or granular permissions.
```

## Prompt Quality Gate

When generating a research prompt for Perplexity, ChatGPT, or similar tools:

After drafting, the skill scores across 5 dimensions (1-10 each). It will not deliver if the average is below 9.5. It iterates on the lowest-scoring dimension until the threshold is met, then delivers only the final version.

| Dimension | What it checks |
|---|---|
| Specificity | References exact tool names, versions, and known failure modes, not generic "search for X" |
| Completeness | All angles covered: GitHub, HN, Reddit, official docs, APIs, community forums |
| Enforceability | Explicit output format, required fields, and fallback rule when no results found |
| Stack-awareness | Names the exact tools in play and explains why they matter to the research |
| Edge case coverage | Handles: no results, paywalled sources, outdated info, conflicting sources |

Appended to every delivered prompt:

```
PROMPT QUALITY AUDIT (final):
Specificity:        X/10
Completeness:       X/10
Enforceability:     X/10
Stack-awareness:    X/10
Edge case coverage: X/10
Average:            X.X/10
```

## Search Strategy

5 rounds, count scales with depth tier:

**Round 1: Direct Sentiment**
- `[product] review [current year]`
- `[product] reddit honest review`
- `[product] complaints problems issues`

**Round 2: Platform-Specific**
- `site:reddit.com [product] experience`
- `site:news.ycombinator.com [product]`
- G2, Capterra, Trustpilot, YouTube reviews

**Round 3: Switching Signals**
- `[product] switched from / switched to`
- `[product] cancelled subscription why`
- `[product] pricing worth it [current year]`

**Round 4: Feature Intelligence**
- `[product] missing features request`
- `[product] roadmap upcoming features`
- `[product] [competitor] comparison [current year]`

**Round 5: Industry Analysis (Deep Dive only)**
- Market share, analyst reports, funding/revenue, outages, controversies

## Evidence Standards

- Every insight links to at least one source URL
- Claims from only one source get flagged `[single source, unverified]`
- User sentiment is paraphrased from real findings, never invented
- Community sources preferred over SEO farms and affiliate listicles
- Sparse sentiment data gets flagged explicitly, not padded with confidence it doesn't have
- Sections with no data say "Insufficient data found" plus what was searched

## Tips

- Use "Deep Dive" for due diligence or before building a competitor. Surface-level research misses the tail risks.
- Name your stack context when generating prompts for other tools. That is what separates a 7/10 prompt from a 9.5.
- Round 3 (switching signals) is where the real product intelligence lives. Do not skip it.
- If the quality gate keeps failing on "Stack-awareness", you have not named your constraints concretely enough.

## Common Use Cases

- Evaluating a SaaS tool before committing to an annual plan
- Building a competitive analysis slide for a pitch or investor update
- Researching a market before writing content, a blog post, or a course
- Due diligence on a vendor, API, or infrastructure provider
- Generating a high-quality research prompt to hand off to a deep research agent
