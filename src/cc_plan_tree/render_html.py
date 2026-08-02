"""Render a plan tree as a self-contained interactive HTML file (no external assets)."""

from __future__ import annotations

from html import escape

from .layout import display_label
from .schema import Node, Plan
from .styles import REJECTED, STYLES, style_for

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, 'Segoe UI', 'Helvetica Neue', 'Hiragino Sans',
    'Noto Sans CJK JP', Meiryo, sans-serif;
  background: #ffffff; color: #0f172a; padding: 24px;
}
header { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
h1 { font-size: 20px; margin-right: auto; }
.toolbar button {
  font: inherit; font-size: 13px; padding: 4px 12px; border: 1px solid #cbd5e1;
  background: #f8fafc; border-radius: 6px; cursor: pointer;
}
.toolbar button:hover { background: #eef2f7; }
.legend { display: flex; gap: 12px; flex-wrap: wrap; font-size: 12px; color: #475569; margin-bottom: 18px; }
.legend span { display: inline-flex; align-items: center; gap: 5px; }
.chip { width: 12px; height: 12px; border-radius: 3px; border: 1.5px solid; display: inline-block; }
.chip.dashed { border-style: dashed; }
.tree { overflow-x: auto; padding: 8px 4px 24px; }
.tree ul { display: flex; padding-top: 22px; position: relative; list-style: none; }
.tree li { display: flex; flex-direction: column; align-items: center; position: relative; padding: 22px 7px 0; }
.tree li::before, .tree li::after {
  content: ''; position: absolute; top: 0; right: 50%;
  border-top: 1.5px solid #cbd5e1; width: 50%; height: 22px;
}
.tree li::after { right: auto; left: 50%; border-left: 1.5px solid #cbd5e1; }
.tree li:only-child::before, .tree li:only-child::after { display: none; }
.tree li:only-child { padding-top: 0; }
.tree li:first-child::before, .tree li:last-child::after { border: 0 none; }
.tree li:last-child::before { border-right: 1.5px solid #cbd5e1; border-radius: 0 8px 0 0; }
.tree li:first-child::after { border-radius: 8px 0 0 0; }
.tree ul ul::before {
  content: ''; position: absolute; top: 0; left: 50%;
  border-left: 1.5px solid #cbd5e1; height: 22px;
}
.tree > ul { padding-top: 0; width: max-content; margin: 0 auto; }
.tree > ul > li { padding-top: 0; }
.tree > ul > li::before, .tree > ul > li::after { display: none; }
.node {
  position: relative; border: 1.5px solid; border-radius: 8px;
  padding: 8px 14px; font-size: 13.5px; max-width: 300px; line-height: 1.45;
}
.node.has-children { cursor: pointer; user-select: none; }
.node .caret { margin-left: 8px; font-weight: 700; opacity: 0.5; }
.node.rejected { border-style: dashed; }
li.collapsed > ul { display: none; }
.node[data-reason]:hover::after {
  content: attr(data-reason); position: absolute; left: 50%; transform: translateX(-50%);
  top: calc(100% + 7px); background: #0f172a; color: #f8fafc; font-size: 12px;
  padding: 5px 10px; border-radius: 6px; width: max-content; max-width: 320px;
  white-space: normal; z-index: 10; pointer-events: none;
}
footer { font-size: 12px; color: #94a3b8; }
footer a { color: #64748b; }
"""

_JS = """
document.querySelectorAll('.node.has-children').forEach(function (node) {
  node.addEventListener('click', function () {
    var li = node.parentElement;
    li.classList.toggle('collapsed');
    node.querySelector('.caret').textContent = li.classList.contains('collapsed') ? '+' : '\\u2212';
  });
});
function setAll(collapsed) {
  document.querySelectorAll('.tree ul ul > li').forEach(function (li) {
    var node = li.querySelector(':scope > .node.has-children');
    if (!node) return;
    li.classList.toggle('collapsed', collapsed);
    node.querySelector('.caret').textContent = collapsed ? '+' : '\\u2212';
  });
}
document.getElementById('expand-all').addEventListener('click', function () { setAll(false); });
document.getElementById('collapse-all').addEventListener('click', function () { setAll(true); });
"""

_LEGEND_ITEMS = [
    ("Goal", STYLES["goal"], False),
    ("Phase", STYLES["phase"], False),
    ("Step", STYLES["step"], False),
    ("Decision", STYLES["decision"], False),
    ("Chosen option", STYLES["option"], False),
    ("Rejected option", REJECTED, True),
]


def _node_html(node: Node) -> str:
    fill, stroke, text_color = style_for(node)
    classes = ["node"]
    if node.rejected:
        classes.append("rejected")
    if node.children:
        classes.append("has-children")
    reason = ""
    if node.reason:
        reason = f' data-reason="{escape(node.reason, quote=True)}"'
    caret = '<span class="caret">−</span>' if node.children else ""
    div = (
        f'<div class="{" ".join(classes)}" '
        f'style="background:{fill};border-color:{stroke};color:{text_color}"{reason}>'
        f"{escape(display_label(node))}{caret}</div>"
    )
    if node.children:
        children = "".join(f"<li>{_node_html(child)}</li>" for child in node.children)
        return f"{div}<ul>{children}</ul>"
    return div


def render_html(plan: Plan) -> str:
    legend = "".join(
        f'<span><span class="chip{" dashed" if dashed else ""}" '
        f'style="background:{fill};border-color:{stroke}"></span>{escape(name)}</span>'
        for name, (fill, stroke, _), dashed in _LEGEND_ITEMS
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(plan.title)} — cc-plan-tree</title>
<style>{_CSS}</style>
</head>
<body>
<header>
  <h1>{escape(plan.title)}</h1>
  <div class="toolbar">
    <button id="expand-all">Expand all</button>
    <button id="collapse-all">Collapse all</button>
  </div>
</header>
<div class="legend">{legend}</div>
<div class="tree"><ul><li>{_node_html(plan.root)}</li></ul></div>
<footer>Generated by <a href="https://github.com/natsu0529/cc-plan-tree">cc-plan-tree</a> —
click a node to collapse/expand, hover a rejected option to see why.</footer>
<script>{_JS}</script>
</body>
</html>
"""
