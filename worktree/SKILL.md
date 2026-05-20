---
name: worktree
description: Set up a git worktree for scoped development work — isolated branch without losing your current working state.
---

# Worktree

Use git worktrees to work on a feature or fix in isolation without stashing, switching branches, or losing context. A worktree is a second checkout of the same repo at a different path.

## When to Use This Skill

- Starting non-trivial feature work that should stay off the main branch
- Working on two things simultaneously without stashing
- Any bounded task that deserves its own branch

## Setup

```bash
# Convention: feat/<short-slug>
git worktree add worktrees/<slug> -b feat/<slug>
```

Worktrees live **inside** the repo at `<repo>/worktrees/<slug>`. Add `worktrees/` to `.gitignore` so they don't appear as untracked. The `-b` flag creates the branch.

## Work

Open the worktree path in a new editor window or terminal. It's a full checkout — all repo tools work normally. Changes stay isolated to `feat/<slug>`.

## Teardown (after merge)

```bash
git worktree remove worktrees/<slug>
git branch -d feat/<slug>
```

Only merge to the main branch on explicit approval. Don't pile unrelated commits onto the task branch.

## Rules

- Create the worktree at the **start** of scope, not midway through.
- Work only in that tree until merge.
- Merge on explicit OK — not when you think it's ready.
- After merge: remove the worktree and delete the branch.

## Tips

- The worktree path convention (`<repo>/worktrees/<slug>`) keeps everything under one root and makes `worktrees/` easy to gitignore.
- If you forget to add `worktrees/` to `.gitignore`, git will show every worktree as an untracked directory.
- Worktrees share the git object store — switching branches in one doesn't affect the other.
