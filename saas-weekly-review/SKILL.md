---
name: saas-weekly-review
description: Structured Friday founder review — prompts you through metrics, wins, blockers, learnings, and next week's ONE thing. Use at end of week for consistent reflection and momentum tracking.
---

# SaaS Weekly Review

A structured end-of-week reflection for solo founders and small teams. Prompts you through the key questions that keep a SaaS business on track: what shipped, what moved the needle, what's blocked, what you learned, and what the single most important thing is for next week.

## When to Use This Skill

- Every Friday (or your end-of-week day)
- Before sending a weekly investor or stakeholder update
- When you feel like "nothing happened this week" (you'll surprise yourself)
- As a team standup template for small remote teams
- Before quarterly planning — review the last 4 weeks of notes

## What This Skill Does

1. **Shipping review**: what went live, what moved from "in progress" to "done"
2. **Metrics pulse**: the 3-5 numbers that actually matter this week
3. **Win of the week**: the single biggest positive signal
4. **Blocker audit**: what's stuck and who/what can unblock it
5. **Learning capture**: one thing you know now that you didn't know Monday
6. **Next week's ONE thing**: the constraint-based priority (if you only ship one thing, what is it?)

## How to Use

### Basic Usage

```
/weekly-review
```

Claude will prompt you through each section. Answer naturally — no need to have data prepared.

### Advanced Usage

```
/weekly-review
Use my project context to fill in what you know. Flag anything you need me to complete.
Focus extra attention on the blocker audit — I want a concrete unblocking plan for each.
```

## Example

**User**: "/weekly-review"

**Output**:
```
## Weekly Review — Week of May 26

### Shipped
- New onboarding flow (3 steps → 1 step) — live Tuesday
- Pricing page redesign — live Thursday
- Fixed checkout bug affecting 12% of users

### Metrics
| Metric | This Week | Last Week | Change |
|--------|-----------|-----------|--------|
| Signups | 142 | 128 | +11% |
| Trial → Paid | 8.3% | 7.1% | +1.2pp |
| Churn | 4.1% | 4.8% | -0.7pp |

### Win of the Week
Onboarding simplification already showing impact — trial completion up 23% in 3 days.

### Blockers
1. **Stripe tax integration** — waiting on accountant for tax codes (ETA: Tuesday)
2. **Mobile nav bug** — iOS Safari only, can't reproduce consistently

### What I Learned
Users who complete onboarding within 24 hours convert at 3x the rate of those who take 3+ days. Speed matters more than feature education.

### Next Week's ONE Thing
Ship the Stripe tax integration. Unblocks EU expansion and cleans up accounting.
```

## Tips

- Write the review in a markdown file and commit it to your repo — build a personal archive
- If you skip a week, do a combined review — it's better than losing the habit
- Share the "Win of the Week" with your team or social media — it builds momentum
- The "ONE thing" rule: if you list more than one priority, you haven't prioritized
- Use the metrics section to build intuition about which numbers actually drive your business

## Common Use Cases

- Solo SaaS founders maintaining accountability with themselves
- Indie hackers tracking weekly progress in public (build-in-public posts)
- Small teams using this as a lightweight async standup
- Pre-investor-update: run this first, then distill into the update
- Quarterly planning: review 12 weeks of weekly reviews for patterns
