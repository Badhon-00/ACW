---
name: journey-mapper
description: Scans a codebase and generates a self-contained HTML service-design journey map in the NN/g combined customer journey + service blueprint format. Use when mapping user journeys, building service blueprints, preparing design workshops, or orienting a team on how users move through a product.
---

# Journey Mapper

Reads a codebase, thinks like a service designer, and writes a single browser-ready HTML file with all inferred user journeys and service blueprints — no manual diagram work required.

## When to Use This Skill

- You need to orient a new designer or stakeholder on how users move through a product
- You are preparing a service design workshop and need a blueprint artefact before the session
- You want to audit a codebase for gaps between the intended and actual user journey
- You need a living document that can be regenerated as the codebase evolves

## What This Skill Does

1. **Codebase scan**: Reads routes, screens, components, API handlers, error states, and email templates to reconstruct all user-facing flows
2. **NN/g structure**: Maps actors, categories, journeys, stages, and moments — covering Doing, Thinking, Feeling, Pain points, Opportunities, Frontstage, Backstage, and Support processes
3. **HTML generation**: Produces a single self-contained `.html` file with emotion curves, localStorage autosave, and JSON export — no server, no build step

Every AI-inferred value is flagged `[Assumption]` so teams know what needs validation with real user research.

## How to Use

### Basic Usage

```
/journey-mapper
```

The skill asks for the codebase path if not already in scope, then produces `journey-map.html` in the root.

### Advanced Usage

```
/journey-mapper Scan src/ and save the output to docs/journey-map.html
```

```
/journey-mapper Focus on the onboarding flow only
```

## Example

**User**: "Create a service blueprint for our product so I can share it with stakeholders before the workshop"

**Output**: A self-contained `journey-map.html` covering all user-facing flows — 4–12 journeys, each with a full NN/g grid. Open in any browser, annotate in place, share as a file.

## Tips

- The more context you feed it (design docs, README, API specs), the richer the output
- Re-run after major feature work to keep the map current
- The HTML file is fully self-contained — safe to email or attach to a Jira ticket
- Editable fields (Thinking, Feeling, Pain, Opportunity, Evidence) are separate from AI-filled fields so you can layer real research on top

## Common Use Cases

- Onboarding a new designer to an existing product without reading thousands of lines of code
- Pre-workshop artefact preparation for service design or product discovery sessions
- Auditing user flows before a redesign to surface gaps and error-state blindspots
- Generating a baseline map to annotate with Hotjar, session recording, or support ticket insights

## Installation

Full installation instructions for Claude Code, OpenCode, Codex CLI, Cursor, Windsurf, Continue.dev, Gemini CLI, and Aider are in the source repo:

**GitHub:** https://github.com/joeyvansommeren/journey-mapper

**Claude Code (plugin marketplace):**
```
/plugin marketplace add joeyvansommeren/journey-mapper
```
