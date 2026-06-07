---
name: unship
description: Compare AI agent-made UI variants locally in a real app, then keep one and clean up the rest.
---

# Unship

Unship helps AI coding assistants create temporary UI alternatives in real source code, let a human compare those alternatives in the local browser, and then remove the losing variants before shipping.

Use this skill when a user wants to compare agent-made alternatives for UI sections, page layouts, copy treatments, product states, flows, design-system directions, rendered documentation, or developer experience surfaces.

## When to Use This Skill

- The user wants several UI directions instead of one generated result.
- A coding agent is iterating on frontend work and the user needs to compare options side by side in the actual app.
- The user has picked a variant and wants the unused temporary code removed.

## What This Skill Does

1. **Creates temporary variants**: Adds the smallest useful source-level comparison using Unship's `data-unship-pick` and `data-unship-option` markup.
2. **Uses a local picker**: Installs or reuses the Unship browser picker so the user can flip between options in their running development preview.
3. **Cleans up after selection**: Keeps the chosen option, removes losing alternatives, and verifies that no temporary Unship artifacts remain before shipping.

## How to Use

Install Unship in the project:

```bash
npx -y @unship/cli@latest init
```

Create a comparison:

```text
Use Unship to compare 4 hero directions for this page.
```

After the user chooses a visible option label, settle the comparison:

```text
Keep the Proof-led option and clean up the others.
```

For a final cleanup check, run:

```bash
npx -y @unship/cli@latest check --json
```

## Example

**User**: "Use Unship to compare 3 pricing section directions."

**Assistant workflow**:

1. Inspect the existing pricing section and design system.
2. Add one `data-unship-pick="Pricing"` group with three direct `data-unship-option` children.
3. Reuse or install the local picker.
4. Tell the user the option labels to compare in the browser.
5. When the user chooses, keep that source and remove the temporary alternatives.

## Tips

- Keep variants local and temporary; Unship is not production A/B testing.
- Prefer 2-4 meaningful options with short visible labels.
- Avoid duplicate active IDs, global scripts, analytics side effects, focus traps, and submit controls inside inactive hidden variants.
- Treat cleanup as part of the workflow, not an optional afterthought.

**Inspired by:** Real frontend iteration loops where AI agents produce one design at a time and users need to compare multiple options in context.
