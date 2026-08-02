"""Tiered top-down tree layout, shared by the SVG and PNG renderers."""

from __future__ import annotations

from dataclasses import dataclass, field

from .schema import Node, Plan

FONT_SIZE = 13
LINE_H = 18
PAD_X = 14
PAD_Y = 9
H_GAP = 26
V_GAP = 54
WRAP_UNITS = 30  # max label width in half-width character units
UNIT_W = FONT_SIZE * 0.62  # approx pixel width of one half-width unit


def _units(ch: str) -> int:
    # CJK and other wide characters count as two half-width units
    return 2 if ord(ch) > 0x2E80 else 1


def _tokenize(text: str) -> list[str]:
    """Split into wrappable tokens: latin words stay whole, CJK chars break anywhere."""
    tokens: list[str] = []
    cur = ""
    for ch in text:
        if ch == " " or _units(ch) == 2:
            if cur:
                tokens.append(cur)
                cur = ""
            tokens.append(ch)
        else:
            cur += ch
    if cur:
        tokens.append(cur)
    return tokens


def _width(token: str) -> int:
    return sum(_units(c) for c in token)


def wrap_label(text: str, max_units: int = WRAP_UNITS) -> list[str]:
    lines: list[str] = []
    for raw_line in text.split("\n"):
        cur = ""
        used = 0
        for token in _tokenize(raw_line):
            width = _width(token)
            if used + width > max_units and cur.strip():
                lines.append(cur.rstrip())
                cur, used = "", 0
                if token == " ":
                    continue
            while width > max_units:  # single token longer than a line: hard-break it
                part = ""
                part_units = 0
                for ch in token:
                    if part_units + _units(ch) > max_units:
                        break
                    part += ch
                    part_units += _units(ch)
                lines.append(part)
                token = token[len(part):]
                width = _width(token)
            cur += token
            used += width
        lines.append(cur.rstrip())
    return [line for line in lines if line] or [""]


def display_label(node: Node) -> str:
    if node.rejected:
        return "× " + node.label
    if node.status == "done":
        return "✓ " + node.label
    if node.status == "in_progress":
        return "… " + node.label
    return node.label


@dataclass
class Placed:
    node: Node
    x: float  # center x
    y: float  # top y
    w: float
    h: float
    lines: list[str] = field(default_factory=list)
    parent: Placed | None = None


def layout(plan: Plan) -> tuple[list[Placed], float, float]:
    """Compute node positions. Returns (placed nodes, total width, total height)."""
    sizes: dict[int, tuple[list[str], float, float]] = {}

    def measure(node: Node) -> None:
        lines = wrap_label(display_label(node))
        width = max(sum(_units(c) for c in line) for line in lines) * UNIT_W + PAD_X * 2
        height = len(lines) * LINE_H + PAD_Y * 2
        sizes[id(node)] = (lines, width, height)
        for child in node.children:
            measure(child)

    measure(plan.root)

    subtree_w: dict[int, float] = {}

    def compute_width(node: Node) -> float:
        _, width, _ = sizes[id(node)]
        if not node.children:
            subtree_w[id(node)] = width
            return width
        total = sum(compute_width(c) for c in node.children)
        total += H_GAP * (len(node.children) - 1)
        subtree_w[id(node)] = max(width, total)
        return subtree_w[id(node)]

    compute_width(plan.root)

    # uniform row heights per depth so siblings align
    row_h: list[float] = []

    def scan_depth(node: Node, depth: int) -> None:
        _, _, height = sizes[id(node)]
        if depth >= len(row_h):
            row_h.append(height)
        else:
            row_h[depth] = max(row_h[depth], height)
        for child in node.children:
            scan_depth(child, depth + 1)

    scan_depth(plan.root, 0)

    row_y: list[float] = []
    y = 0.0
    for height in row_h:
        row_y.append(y)
        y += height + V_GAP
    total_h = y - V_GAP

    placed: list[Placed] = []

    def assign(node: Node, left: float, depth: int, parent: Placed | None) -> None:
        lines, width, height = sizes[id(node)]
        stw = subtree_w[id(node)]
        p = Placed(
            node=node,
            x=left + stw / 2,
            y=row_y[depth],
            w=width,
            h=height,
            lines=lines,
            parent=parent,
        )
        placed.append(p)
        if node.children:
            children_w = sum(subtree_w[id(c)] for c in node.children)
            children_w += H_GAP * (len(node.children) - 1)
            cx = left + (stw - children_w) / 2
            for child in node.children:
                assign(child, cx, depth + 1, p)
                cx += subtree_w[id(child)] + H_GAP

    assign(plan.root, 0.0, 0, None)
    return placed, subtree_w[id(plan.root)], total_h
