"""Render a plan tree as Mermaid flowchart text (GitHub renders this natively in PR bodies)."""

from __future__ import annotations

import re

from .layout import display_label
from .schema import Node, Plan


def _escape(text: str) -> str:
    return text.replace('"', "#quot;")


def render_mermaid(plan: Plan) -> str:
    lines = ["flowchart TD"]
    ids: dict[int, str] = {}
    used: set[str] = set()
    by_class: dict[str, list[str]] = {"decision": [], "chosen": [], "rejected": [], "done": []}

    def uid(node: Node) -> str:
        if id(node) in ids:
            return ids[id(node)]
        base = re.sub(r"[^A-Za-z0-9_]", "_", node.id) or "n"
        name = base
        counter = 2
        while name in used:
            name = f"{base}_{counter}"
            counter += 1
        used.add(name)
        ids[id(node)] = name
        return name

    def walk(node: Node) -> None:
        name = uid(node)
        label = _escape(display_label(node))
        if node.type == "decision":
            lines.append(f'  {name}{{"{label}"}}')
            by_class["decision"].append(name)
        else:
            lines.append(f'  {name}["{label}"]')
            if node.rejected:
                by_class["rejected"].append(name)
            elif node.type == "option" and node.chosen:
                by_class["chosen"].append(name)
            elif node.status == "done":
                by_class["done"].append(name)
        for child in node.children:
            arrow = "-.->" if child.rejected else "-->"
            walk(child)
            lines.append(f"  {name} {arrow} {uid(child)}")

    walk(plan.root)

    class_defs = {
        "decision": "fill:#fffbeb,stroke:#b45309,color:#78350f",
        "chosen": "fill:#f0fdf4,stroke:#15803d,color:#14532d",
        "rejected": "fill:#f1f5f9,stroke:#94a3b8,color:#64748b,stroke-dasharray: 4 3",
        "done": "fill:#f0fdf4,stroke:#16a34a,color:#14532d",
    }
    for key, members in by_class.items():
        if members:
            lines.append(f"  classDef {key} {class_defs[key]}")
            lines.append(f"  class {','.join(members)} {key}")

    return "\n".join(lines)
