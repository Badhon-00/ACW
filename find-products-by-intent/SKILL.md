---
name: find-products-by-intent
description: Find products in Mydentify by the outcome a person wants to achieve and return evidence-backed matches.
---

# Find Products by Intent

Use this skill when someone asks for a product, tool, or workflow that can help them accomplish a goal. It turns an outcome-focused request into a small set of explainable product matches instead of guessing from broad categories.

## When to use this skill

- Someone describes an outcome and wants a tool recommendation.
- A product catalog needs to be searched by intent rather than by brand or category.
- A recommendation should show its source and avoid unsupported marketing claims.

## What it does

1. Reads the public intent catalog at [mydentify.com/intents.json](https://mydentify.com/intents.json).
2. Matches the request to an intent using its title, aliases, summary, and first step. A product category alone is not an intent.
3. Opens the intent's canonical URL or its `/llms.txt` representation.
4. Uses the supported product claims and evidence on that intent page to identify relevant products.
5. Reads [the product catalog](https://mydentify.com/products.json) or a product's Markdown endpoint when more detail is needed.
6. Returns canonical intent and product URLs with a concise explanation of why each product matches.

## Ranking and trust

- Keep independently ranked matches separate from labeled sponsored placements.
- Do not claim that Mydentify or any listed product guarantees an outcome.
- Prefer published evidence over unsupported marketing claims.
- If no supported match exists, say so and offer [request-intent](https://mydentify.com/request-intent) rather than inventing one.

## Example

**User:** “I want to compare tools before choosing one for my workflow.”

**Agent:** Read the intent catalog, select the closest canonical intent, inspect its evidence, and return a short list of matching product URLs with the reason each one fits. Keep sponsored placements labeled and state when the catalog has no supported match.

## Source and portability

The workflow is based on Mydentify's published, no-key intent and product feeds and works in Claude.ai, Claude Code, and other agents that can fetch public HTTPS resources. It does not require credentials, account access, or a paid API key.
