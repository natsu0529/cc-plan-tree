"""Shared node colors: (fill, stroke, text)."""

from __future__ import annotations

STYLES = {
    "goal": ("#eef2ff", "#4f46e5", "#312e81"),
    "phase": ("#ecfeff", "#0e7490", "#155e75"),
    "step": ("#f8fafc", "#64748b", "#1e293b"),
    "decision": ("#fffbeb", "#b45309", "#78350f"),
    "option": ("#f0fdf4", "#15803d", "#14532d"),
    "note": ("#faf5ff", "#7e22ce", "#581c87"),
}
REJECTED = ("#f1f5f9", "#94a3b8", "#64748b")


def style_for(node):
    if node.rejected:
        return REJECTED
    return STYLES.get(node.type, STYLES["step"])
