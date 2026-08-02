"""cc-plan-tree command line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .schema import PlanError, load_plan

DEFAULT_PLAN = ".cc-plan-tree/plan.json"
COMMAND_FILES = ["plan-tree.md", "plan-verify.md", "plan-export.md"]


def _bundled_commands_dir():
    from importlib import resources

    return resources.files("cc_plan_tree") / "commands"


def cmd_init(args: argparse.Namespace) -> int:
    if args.project:
        target = Path.cwd() / ".claude" / "commands"
        scope = "this project"
    else:
        target = Path.home() / ".claude" / "commands"
        scope = "all projects (user level)"
    target.mkdir(parents=True, exist_ok=True)

    src_dir = _bundled_commands_dir()
    installed = []
    for name in COMMAND_FILES:
        content = (src_dir / name).read_text(encoding="utf-8")
        dest = target / name
        dest.write_text(content, encoding="utf-8")
        installed.append(dest)

    print(f"Installed Claude Code slash commands for {scope}:")
    for path in installed:
        print(f"  {path}")
    print("\nAvailable in Claude Code as: /plan-tree, /plan-verify, /plan-export")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    try:
        plan = load_plan(args.plan)
    except PlanError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.format == "mermaid":
        from .render_mermaid import render_mermaid

        text = render_mermaid(plan)
        if args.out:
            Path(args.out).write_text(text + "\n", encoding="utf-8")
            print(args.out)
        else:
            print(text)
    elif args.format == "svg":
        from .render_svg import render_svg

        out = Path(args.out or "plan-tree.svg")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_svg(plan), encoding="utf-8")
        print(out)
    elif args.format == "png":
        from .render_png import render_png

        out = render_png(plan, args.out or "plan-tree.png")
        print(out)
    elif args.format == "html":
        from .render_html import render_html

        out = Path(args.out or "plan-tree.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render_html(plan), encoding="utf-8")
        print(out)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="cc-plan-tree",
        description="Visualize Claude Code plans as design trees.",
    )
    parser.add_argument("--version", action="version", version=f"cc-plan-tree {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="install the /plan-tree, /plan-verify and /plan-export slash commands")
    p_init.add_argument(
        "--project",
        action="store_true",
        help="install into ./.claude/commands (default: ~/.claude/commands)",
    )
    p_init.set_defaults(func=cmd_init)

    p_render = sub.add_parser("render", help="render a plan tree to mermaid, svg or png")
    p_render.add_argument("plan", nargs="?", default=DEFAULT_PLAN, help=f"plan JSON path (default: {DEFAULT_PLAN})")
    p_render.add_argument("--format", choices=["mermaid", "svg", "png", "html"], default="mermaid")
    p_render.add_argument("--out", help="output path (mermaid defaults to stdout)")
    p_render.set_defaults(func=cmd_render)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
