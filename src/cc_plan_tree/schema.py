"""Plan tree data model and JSON loading/validation."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

NODE_TYPES = {"goal", "phase", "step", "decision", "option", "note"}
STATUSES = {"pending", "in_progress", "done"}


class PlanError(ValueError):
    """Raised when a plan file is malformed."""


@dataclass
class Node:
    id: str
    label: str
    type: str = "step"
    chosen: bool | None = None
    status: str | None = None
    reason: str | None = None
    children: list[Node] = field(default_factory=list)

    @property
    def rejected(self) -> bool:
        return self.type == "option" and self.chosen is False

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()


@dataclass
class Plan:
    title: str
    root: Node
    version: int = 1


def _parse_node(data, path: str, seen_ids: set) -> Node:
    if not isinstance(data, dict):
        raise PlanError(f"{path}: node must be an object, got {type(data).__name__}")

    node_id = data.get("id")
    label = data.get("label")
    if not isinstance(node_id, str) or not node_id:
        raise PlanError(f"{path}: missing or invalid 'id'")
    if node_id in seen_ids:
        raise PlanError(f"{path}: duplicate id '{node_id}'")
    seen_ids.add(node_id)
    if not isinstance(label, str) or not label:
        raise PlanError(f"{path} (id={node_id}): missing or invalid 'label'")

    node_type = data.get("type", "step")
    if node_type not in NODE_TYPES:
        raise PlanError(
            f"{path} (id={node_id}): unknown type '{node_type}' "
            f"(expected one of {sorted(NODE_TYPES)})"
        )

    status = data.get("status")
    if status is not None and status not in STATUSES:
        raise PlanError(
            f"{path} (id={node_id}): unknown status '{status}' "
            f"(expected one of {sorted(STATUSES)})"
        )

    chosen = data.get("chosen")
    if chosen is not None and not isinstance(chosen, bool):
        raise PlanError(f"{path} (id={node_id}): 'chosen' must be a boolean")

    children_data = data.get("children", [])
    if not isinstance(children_data, list):
        raise PlanError(f"{path} (id={node_id}): 'children' must be a list")
    children = [
        _parse_node(child, f"{path}.children[{i}]", seen_ids)
        for i, child in enumerate(children_data)
    ]

    return Node(
        id=node_id,
        label=label,
        type=node_type,
        chosen=chosen,
        status=status,
        reason=data.get("reason"),
        children=children,
    )


def load_plan(path) -> Plan:
    path = Path(path)
    if not path.exists():
        raise PlanError(f"plan file not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PlanError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise PlanError(f"{path}: top level must be an object")
    title = data.get("title")
    if not isinstance(title, str) or not title:
        raise PlanError(f"{path}: missing or invalid 'title'")
    root_data = data.get("root")
    if root_data is None:
        raise PlanError(f"{path}: missing 'root' node")

    root = _parse_node(root_data, "root", set())
    return Plan(title=title, root=root, version=data.get("version", 1))
