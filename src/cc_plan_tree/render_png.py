"""Render a plan tree to PNG using Pillow (no headless browser needed)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .layout import FONT_SIZE, LINE_H, PAD_Y, layout
from .schema import Plan
from .styles import style_for

SCALE = 2  # supersample for crisp text
MARGIN = 28
TITLE_SIZE = 17
TITLE_GAP = 20

# Fonts with CJK coverage first, then common latin fallbacks.
FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W4.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/meiryo.ttc",
    "C:/Windows/Fonts/YuGothM.ttc",
    "C:/Windows/Fonts/segoeui.ttf",
]


def _load_font(size: int):
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_png(plan: Plan, out_path) -> Path:
    placed, tree_w, tree_h = layout(plan)
    title_h = TITLE_SIZE + TITLE_GAP
    width = int((tree_w + MARGIN * 2) * SCALE)
    height = int((tree_h + MARGIN * 2 + title_h) * SCALE)
    ox = MARGIN * SCALE
    oy = (MARGIN + title_h) * SCALE

    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    font = _load_font(FONT_SIZE * SCALE)
    title_font = _load_font(TITLE_SIZE * SCALE)

    draw.text((MARGIN * SCALE, MARGIN * SCALE), plan.title, fill="#0f172a", font=title_font)

    for p in placed:
        if p.parent is None:
            continue
        color = "#cbd5e1" if p.node.rejected else "#94a3b8"
        x1 = ox + p.parent.x * SCALE
        y1 = oy + (p.parent.y + p.parent.h) * SCALE
        x2 = ox + p.x * SCALE
        y2 = oy + p.y * SCALE
        mid_y = (y1 + y2) / 2
        draw.line([(x1, y1), (x1, mid_y), (x2, mid_y), (x2, y2)], fill=color, width=SCALE)

    for p in placed:
        fill, stroke, text_color = style_for(p.node)
        x0 = ox + (p.x - p.w / 2) * SCALE
        y0 = oy + p.y * SCALE
        x1 = ox + (p.x + p.w / 2) * SCALE
        y1 = oy + (p.y + p.h) * SCALE
        draw.rounded_rectangle(
            [x0, y0, x1, y1], radius=8 * SCALE, fill=fill, outline=stroke, width=SCALE
        )
        for i, line in enumerate(p.lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_w = bbox[2] - bbox[0]
            tx = ox + p.x * SCALE - text_w / 2
            ty = y0 + (PAD_Y + i * LINE_H + 1) * SCALE
            draw.text((tx, ty), line, fill=text_color, font=font)

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    return out_path
