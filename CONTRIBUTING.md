# Contributing to cc-plan-tree

Thanks for taking the time to contribute! 🌳

This project uses the standard GitHub **fork → branch → pull request** flow.
Nobody pushes directly to `main` — including the maintainer.

## Before you start

- For anything more than a typo or a small bug fix, **open an issue first** so we can
  agree on the approach before you spend time on it.
- Check the [open issues](https://github.com/natsu0529/cc-plan-tree/issues) to avoid
  duplicating work already in flight.

## Development setup

```bash
# 1. Fork the repo on GitHub, then clone your fork
git clone https://github.com/<your-username>/cc-plan-tree.git
cd cc-plan-tree

# 2. Add the upstream remote so you can stay in sync
git remote add upstream https://github.com/natsu0529/cc-plan-tree.git

# 3. Create a virtualenv and install in editable mode
python -m venv .venv && source .venv/bin/activate
pip install -e .
```

## Making a change

```bash
git checkout -b my-change            # branch off an up-to-date main
# ... edit ...
cc-plan-tree render examples/sample-plan.json --format mermaid   # sanity check
git commit -m "fix: describe what changed"
git push origin my-change
```

Then open a pull request from your fork against `natsu0529/cc-plan-tree:main`.

### Before you open the PR

- Keep it focused — one logical change per pull request.
- Make sure `cc-plan-tree render examples/sample-plan.json` still works for the
  `mermaid`, `svg`, `html` and `png` formats. CI runs exactly this on Python 3.9,
  3.12 and 3.13.
- If you changed the slash commands under `src/cc_plan_tree/commands/`, bump the
  `<!-- cc-plan-tree-version: ... -->` marker in them so existing users get the
  stale-command warning and re-run `cc-plan-tree init`.
- Update the README if you changed user-facing behaviour.

## Pull request review

- CI must pass, and the maintainer must approve before a PR can be merged.
- Workflow runs on pull requests from forks require maintainer approval before they
  start — this is a security measure, not a comment on your contribution.
- PRs are merged with **squash merge**, so don't worry about tidying up your commit
  history.

## Reporting security issues

Please **do not** open a public issue for security problems. See
[SECURITY.md](SECURITY.md) for how to report them privately.

## License

By contributing, you agree that your contributions will be licensed under the
[MIT License](LICENSE) that covers this project.
