---
description: Plan a task as a visual design tree (cc-plan-tree)
argument-hint: [task description]
---

Plan the following task and record the plan as a structured design tree: $ARGUMENTS

Follow these steps exactly:

1. **Explore & clarify.** Investigate the relevant code first. When a real design decision arises (approach A vs B, library choice, scope trade-off), ask the user with the AskUserQuestion tool. Every question you ask MUST later appear in the tree as a `decision` node whose children are `option` nodes — mark the selected one `"chosen": true` and the others `"chosen": false` (add a short `"reason"` for rejected options).

2. **Write the plan tree.** Create `.cc-plan-tree/plan.json` in the project root. If the file already exists from a previous plan, Read it first (the Write tool refuses to overwrite unread files), then overwrite it. Schema:

   ```json
   {
     "version": 1,
     "title": "<short task title>",
     "root": {
       "id": "root", "type": "goal", "label": "<what we are building>",
       "children": [
         {"id": "p1", "type": "phase", "label": "<phase>", "children": [
           {"id": "s1", "type": "step", "label": "<concrete step>", "status": "pending"}
         ]},
         {"id": "d1", "type": "decision", "label": "<question you asked the user>", "children": [
           {"id": "o1", "type": "option", "label": "<chosen option>", "chosen": true, "children": [
             {"id": "s2", "type": "step", "label": "<step implementing this option>", "status": "pending"}
           ]},
           {"id": "o2", "type": "option", "label": "<rejected option>", "chosen": false, "reason": "<why not>"}
         ]}
       ]
     }
   }
   ```

   Rules:
   - `id` values are unique, lowercase `[a-z0-9_]`.
   - Node types: `goal` (root only), `phase`, `step`, `decision`, `option`, `note`.
   - Labels are concise (≤ 60 chars). Every concrete work item is a `step` with `"status": "pending"`.
   - Steps that implement a chosen option belong under that option node.

3. **Show the tree.** The chat cannot render diagrams, so open the interactive view for the user:
   - Run `cc-plan-tree render .cc-plan-tree/plan.json --format html --out .cc-plan-tree/plan.html`, then open it with `open .cc-plan-tree/plan.html` (macOS) or `xdg-open .cc-plan-tree/plan.html` (Linux). This interactive tree (collapsible nodes, rejected options with reasons on hover) is what the user reviews.
   - Also run `cc-plan-tree render .cc-plan-tree/plan.json --format mermaid` and include the output in a ```mermaid code block as a text record (it renders as a diagram on GitHub).

   Then present the plan for approval as usual. If the `cc-plan-tree` command is not found, retry with `uvx cc-plan-tree render ...`; if uv is also unavailable, tell the user to run `pip install cc-plan-tree`.

4. **During implementation.** After approval, implement the plan. As you complete each step, update its `"status"` in `.cc-plan-tree/plan.json` (`"in_progress"` while working, `"done"` when finished). If the design changes mid-implementation, update the tree too — the tree must always reflect the actual design, because /plan-verify will check it against the code later.
