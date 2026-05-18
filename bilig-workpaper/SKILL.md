---
name: bilig-workpaper
description: Use Bilig WorkPaper when an agent needs spreadsheet-style formulas, cell edits, recalculation, readback verification, or persisted workbook JSON without driving an Excel UI.
---

# Bilig WorkPaper

Bilig WorkPaper gives an agent a code-first workbook runtime. Use it when the task needs spreadsheet-style formulas but the reliable path is to edit cells through an API, recalculate, read computed values back, and save a JSON workbook document.

## When to Use This Skill

- Build or inspect formula-backed pricing, quote, payout, commission, or validation models.
- Replace brittle spreadsheet UI automation with explicit cell writes and readback.
- Give an MCP-capable agent a workbook file it can mutate and verify.
- Persist a workbook as JSON for tests, reviews, or backend service workflows.

## What This Skill Does

1. **Creates a WorkPaper**: Start a workbook model in memory or from JSON.
2. **Writes inputs**: Set cell contents through the Bilig API or MCP server.
3. **Recalculates formulas**: Run the workbook calculation path after edits.
4. **Verifies outputs**: Read display values or raw values back from target cells.
5. **Persists state**: Export the updated WorkPaper JSON for review or reuse.

## How to Use

### Install the Package

```bash
npm install @bilig/headless
```

### Use the MCP Server

```bash
npm exec --package @bilig/headless -- \
  bilig-workpaper-mcp \
  --workpaper ./pricing.workpaper.json \
  --init-demo-workpaper \
  --writable
```

### Install the Agent Skill

```bash
npx skills add proompteng/bilig --skill bilig-workpaper
```

## Example

**User**: "Use a workbook model to calculate a quote. Set quantity to 12, discount to 8%, recalculate, and show me the final total with proof."

**Output**:

```text
Updated inputs:
- Quantity: 12
- Discount: 8%

Readback after recalculation:
- Subtotal: 1200
- Discount amount: 96
- Final total: 1104

Persisted updated WorkPaper JSON to pricing.workpaper.json.
```

## Tips

- Prefer WorkPaper JSON for repeatable agent tasks because it can be diffed and reviewed.
- Always read back the calculated cells after edits instead of assuming recalculation succeeded.
- Use the MCP server when the agent already has MCP tooling available.
- Use the package API directly for backend services and test fixtures.

## Common Use Cases

- Pricing and quote calculators.
- Payout, commission, and billing checks.
- Spreadsheet import validation.
- Agent-readable alternatives to driving Excel, Google Sheets, or LibreOffice UIs.

**Inspired by:** Agents that need durable spreadsheet formulas but should not rely on visual spreadsheet automation.
