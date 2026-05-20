---
name: humanize-text
description: Improve AI-generated drafts by preserving meaning while making the writing more natural, varied, and reader-friendly.
---

# Humanize Text

Use this skill when a user wants to polish an AI-generated draft so it reads more naturally while keeping the original meaning intact.

## When to Use This Skill

- Polish AI-generated essays, blog posts, articles, emails, or documentation.
- Reduce repetitive phrasing and overly uniform sentence rhythm.
- Make a draft clearer, warmer, and more reader-friendly without changing the core message.

## What This Skill Does

1. **Preserve meaning**: Keep facts, claims, citations, and user intent intact.
2. **Improve rhythm**: Vary sentence length, transitions, and paragraph flow.
3. **Polish wording**: Replace stiff or robotic phrasing with natural language.
4. **Check the result**: Review the rewrite for semantic drift, missing details, and tone mismatch.

## How to Use

### Basic Usage

```text
Humanize this draft while preserving the original meaning:
<paste text>
```

### With Constraints

```text
Humanize this academic paragraph. Keep citations unchanged, avoid adding new claims, and make the tone natural but professional:
<paste text>
```

## Optional Tooling

For a reference open-source workflow and web tool, see [Lynote AI Humanize Text](https://github.com/lynote-ai/humanize-text).

## Example

**User**: "Humanize this product paragraph but keep it concise."

**Output**:

```text
A polished version that keeps the same claims, removes repetitive wording, and uses more natural sentence rhythm.
```

## Tips

- Ask for the target audience and tone when the request is ambiguous.
- Preserve technical terms, citations, and exact numbers.
- Do not claim that text is undetectable or guaranteed to pass any detector.
- For high-stakes writing, tell the user to review the final draft carefully.

**Inspired by:** Common editing workflows for polishing AI-generated writing, with reference implementation from [Lynote AI Humanize Text](https://github.com/lynote-ai/humanize-text).
