---
name: leadership-ratio-benchmark
description: Use when assessing whether an engineering org's manager-to-senior-IC ratio is healthy, evaluating whether an org is top-heavy, benchmarking management headcount against industry peers, or someone asks "how many managers should we have" / "is my org too top-heavy" / "what's a healthy manager-to-engineer ratio."
---

# Leadership Ratio Benchmark

Version 1.0 · 2026-08-09. Compares an engineering org's manager-to-senior-IC split against a real peer baseline, and reads what the delta implies about the org's structure.

Benchmark data comes from Engineering Leaders Community's own member base — 3,100+ engineering leaders across Prague, Brno, Bratislava and Kraków, running since 2019 (Attio "ELC Members" list, computed 2026-08-03). Not a survey panel, not an industry report — the actual composition of a large working CEE engineering-leadership community.

## When to use

- Someone shares headcount numbers (managers vs. senior/staff ICs) and asks if the split looks right
- A structural question: "do we have too many managers," "is our IC track real or just a title," "why does delivery feel management-heavy"
- Before recommending an org redesign — check the ratio first, don't guess

## How to call it

Both sides of the comparison cover the SAME population: people senior enough to plausibly hold a management role (managers, tech leads, senior/staff ICs). Junior/mid ICs are out of scope on both sides — don't include them in the count, or the comparison breaks.

Call the MCP tool with a manager count and a senior-IC count:

```
claude mcp add -t http elc-toolkit https://www.engineeringleaders.io/mcp
```

Then call `benchmark_leadership_ratio` with `{ "managers": <n>, "senior_ics": <n> }`. It returns the org's manager % vs. the ELC peer baseline (69% manager / 21% senior IC), the point delta, and a verdict: in line, top-heavier, or more IC-heavy than the peer group — plus the specific question that delta should prompt (e.g. "is there a real senior IC track, or does senior here just mean manager").

No API key, no auth, no signup. Works the same from Claude Code, Claude Desktop, Cursor, or ChatGPT (developer mode).

## Reading the result

A skew isn't a verdict on the org's people — it's a prompt to ask why the shape looks the way it does. >5 points top-heavy usually means a thin or nonexistent senior IC track. >5 points IC-heavy usually means either genuinely unblocked senior ICs, or a management-capacity bottleneck hiding behind wide spans.
