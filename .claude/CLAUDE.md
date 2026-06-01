# Claude Instructions — awesome-claude-skills

Read `AGENTS.md` and `WARP.md` at the repo root for full project context before starting any work.

## Key Rules

- Every new skill requires: a lowercase hyphenated folder + `SKILL.md` with valid frontmatter
- README listings must be alphabetical, no emojis, format: `- [Name](./folder/) - Description. Inspired by [Source].`
- Never edit `composio-skills/` manually, never add crypto/web3 skills, never commit secrets
- Run `cat .github/workflows/label-ready-skill.yml` before touching `README.md`

## New Skill Workflow

```bash
cp -r template-skill/ <skill-name>/
# edit <skill-name>/SKILL.md
git checkout -b add-<skill-name>
git commit -m "Add [Skill Name] skill"
```

## Listing-Only PR Checklist

1. `git --no-pager diff --name-only origin/main...HEAD` → must show only `README.md`
2. Entry is in the correct category and alphabetical order
3. Links to an external URL (not a local folder)
