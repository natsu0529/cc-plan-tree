---
description: Export the design tree as a PNG image (cc-plan-tree)
argument-hint: [output path (default ./plan-tree.png)]
---

Export the current design tree to a PNG image.

1. Confirm `.cc-plan-tree/plan.json` exists. If not, tell the user to run `/plan-tree` first and stop.
2. Determine the output path: use `$ARGUMENTS` if provided, otherwise `./plan-tree.png` in the project root.
3. Run `cc-plan-tree render .cc-plan-tree/plan.json --format png --out <path>` and report the saved file path to the user. If the `cc-plan-tree` command is not found, tell the user to run `pip install cc-plan-tree`.
