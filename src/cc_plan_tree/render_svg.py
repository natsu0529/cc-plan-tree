"""Render a plan tree as a standalone SVG string (no external dependencies)."""

from __future__ import annotations

from xml.sax.saxutils import escape

from .layout import FONT_SIZE, LINE_H, PAD_Y, layout
from .schema import Plan
from .styles import style_for

MARGIN = 28
TITLE_SIZE = 17
TITLE_GAP = 20
FONT_STACK = (
    "-apple-system, 'Segoe UI', 'Helvetica Neue', 'Hiragino Sans', "
    "'Noto Sans CJK JP', Meiryo, sans-serif"
)


def render_svg(plan: Plan) -> str:
    placed, tree_w, tree_h = layout(plan)
    title_h = TITLE_SIZE + TITLE_GAP
    width = tree_w + MARGIN * 2
    height = tree_h + MARGIN * 2 + title_h
    ox = MARGIN
    oy = MARGIN + title_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" '
        f'height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">',
        f'<rect width="{width:.0f}" height="{height:.0f}" fill="#ffffff"/>',
        f'<text x="{MARGIN}" y="{MARGIN + TITLE_SIZE - 4}" font-family="{FONT_STACK}" '
        f'font-size="{TITLE_SIZE}" font-weight="700" fill="#0f172a">{escape(plan.title)}</text>',
    ]

    for p in placed:
        if p.parent is None:
            continue
        x1, y1 = ox + p.parent.x, oy + p.parent.y + p.parent.h
        x2, y2 = ox + p.x, oy + p.y
        bend = min(24.0, (y2 - y1) / 2)
        dash = ' stroke-dasharray="5 4"' if p.node.rejected else ""
        color = "#cbd5e1" if p.node.rejected else "#94a3b8"
        parts.append(
            f'<path d="M {x1:.1f} {y1:.1f} C {x1:.1f} {y1 + bend:.1f}, '
            f'{x2:.1f} {y2 - bend:.1f}, {x2:.1f} {y2:.1f}" '
            f'stroke="{color}" stroke-width="1.5" fill="none"{dash}/>'
        )

    for p in placed:
        fill, stroke, text_color = style_for(p.node)
        x0 = ox + p.x - p.w / 2
        y0 = oy + p.y
        dash = ' stroke-dasharray="5 4"' if p.node.rejected else ""
        parts.append(
            f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{p.w:.1f}" height="{p.h:.1f}" '
            f'rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>'
        )
        for i, line in enumerate(p.lines):
            ty = y0 + PAD_Y + i * LINE_H + FONT_SIZE
            parts.append(
                f'<text x="{ox + p.x:.1f}" y="{ty:.1f}" text-anchor="middle" '
                f'font-family="{FONT_STACK}" font-size="{FONT_SIZE}" '
                f'fill="{text_color}">{escape(line)}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)
