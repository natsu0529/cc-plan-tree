---
description: Verify the design tree matches the implemented code, then optionally embed it in the PR body (cc-plan-tree)
---

Verify that the design tree in `.cc-plan-tree/plan.json` matches the code that was actually implemented.

1. **Load the tree.** Read `.cc-plan-tree/plan.json`. If it does not exist, tell the user to run `/plan-tree` first and stop.

2. **Collect the real changes.** Diff this branch against the merge base with the default branch (try `git diff $(git merge-base HEAD origin/HEAD) --stat` and the full diff; fall back to `main`/`master`), and list untracked files with `git status --short`.

3. **Compare.** For every `step` node and every chosen `option` node, check whether the code actually reflects it. Report a table:

   | Node | Verdict | Evidence |
   |---|---|---|
   | <label> | ✅ matches / ⚠️ diverges / ❌ missing | file:line, one line |

   Also flag the reverse direction: significant implemented changes that appear nowhere in the tree.

4. **Resolve divergences.** If anything diverges, ask the user with AskUserQuestion: fix the **code** to match the tree, or update the **tree** to match the code. Apply their choice, then re-run the comparison until everything matches.

5. **Mark completion.** Once consistent, set `"status": "done"` on all completed steps in `.cc-plan-tree/plan.json`.

6. **Embed in the PR (only with explicit confirmation).** Ask the user whether to embed the design tree into the PR body. Only if they say yes:
   - Check a PR exists for this branch with `gh pr view --json number,url,body`. If none exists, say so and stop (do not create one).
   - Run `cc-plan-tree render .cc-plan-tree/plan.json --format mermaid`.
   - Update the PR body, preserving ALL existing content. If the body already contains a `<!-- cc-plan-tree:start -->` ... `<!-- cc-plan-tree:end -->` section, replace only that section; otherwise append:

     ```
     <!-- cc-plan-tree:start -->
     ## 🌳 Design tree

     ```mermaid
     <mermaid output here>
     ```
     <!-- cc-plan-tree:end -->
     ```

   - Write the new body to a temp file and apply it with `gh pr edit --body-file <file>`. Show the user the PR URL when done. GitHub renders the mermaid block as a diagram natively.
