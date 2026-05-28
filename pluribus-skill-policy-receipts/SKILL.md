---
name: pluribus-skill-policy-receipts
description: Emit privacy-safe policy receipts when Claude Skills contain hard rules such as forbidden targets, preview-before-apply, or post-write guards.
---

# Pluribus Skill Policy Receipts

Use this skill when a Claude Skill, project rule, or coding-agent workflow contains a hard rule that must be proven, not merely stated. Examples: do not test internal services, do not edit generated files, do not cross from dry-run to apply without approval, or do not introduce imports from forbidden packages.

This skill is based on the Pluribus `skill.policy.v1` receipt recipe. It turns natural-language Skill constraints into small, inspectable receipts that show what target was considered, whether it was allowed or refused, why, and whether a post-write guard passed.

## When to Use This Skill

- A Skill says something is forbidden, but the agent may still attempt it.
- A workflow needs to prove preview/dry-run stayed read-only before mutating files or services.
- A repository has banned imports, generated files, internal services, or protected paths.
- You want a handoff artifact showing what policy decision stopped or allowed a run without exposing prompts, transcripts, secrets, or raw code.

## What This Skill Does

1. **Lists intended targets**: Identify files, services, commands, imports, or operations the agent is about to touch.
2. **Classifies each target**: Mark each target as `allowed` or `refused` with a short reason.
3. **Stops before unsafe writes**: If any required target is forbidden or ambiguous, stop before generating code or running a mutating command.
4. **Runs a post-write guard**: After permitted edits, run the smallest deterministic check available, such as a grep for forbidden imports or a generated-file diff check.
5. **Emits a privacy-safe receipt**: Record only metadata and decisions. Do not include raw prompts, transcripts, credentials, customer data, source code, stack traces, or raw tool output.

## How to Use

### Basic Usage

Ask Claude to apply the receipt before touching protected areas:

```text
Use the Pluribus skill policy receipt pattern before editing. The hard rule is: do not import from internal-services/* and do not modify generated files. List intended targets, mark allowed/refused with reasons, and stop before writing if any target is forbidden.
```

### Receipt Shape

```json
{
  "schema": "skill.policy.v1",
  "skill": "example-hard-rule-skill",
  "policy_source": "project-skill",
  "targets": [
    {
      "target": "src/orders/checkout.ts",
      "kind": "file",
      "decision": "allowed",
      "reason": "application source file"
    },
    {
      "target": "internal-services/payments",
      "kind": "import_prefix",
      "decision": "refused",
      "reason": "hard rule forbids internal service imports"
    }
  ],
  "write_started": false,
  "stopped_at": "policy_decision_refused",
  "next_safe_action": "ask for an approved public API or adapter boundary"
}
```

### Post-Write Guard Example

After an allowed edit, run the smallest check that proves the boundary still holds:

```bash
grep -R "from ['\"]internal-services/\|require(['\"]internal-services/" src/ || true
```

Then emit a second receipt field such as:

```json
{
  "post_write_guard": {
    "check": "forbidden-internal-service-imports",
    "result": "passed",
    "matches": 0
  }
}
```

## Example

**User**: "Update the checkout validation, but this Skill says never call internal payment services from UI code."

**Output**:

```text
Policy receipt before edits:
- src/checkout/CheckoutForm.tsx: allowed — UI source file.
- internal-services/payments: refused — hard rule forbids direct internal service imports.
- generated/api-client.ts: refused — generated file.

Stopped before writing because the requested implementation would cross a forbidden import boundary. Next safe action: expose or use an approved public payment adapter instead.
```

## Tips

- Prefer refusal before writes over fixing dangerous edits afterward.
- Keep receipts small and metadata-only.
- Treat ambiguous targets as refused until the user or project policy resolves them.
- Pair this with hooks where available, but do not rely on natural-language instructions alone for hard safety boundaries.

## Common Use Cases

- Preventing internal service imports from frontend code.
- Refusing edits to generated files.
- Proving dry-run/preview mode did not mutate state.
- Recording why an agent stopped instead of bypassing a policy.
- Handing off a safe next action after a refused target.

**Inspired by:** Pluribus skill policy receipts: https://github.com/caioribeiroclw-pixel/pluribus/blob/main/docs/skill-policy-receipts.md
