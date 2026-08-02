# Security Policy

## Supported versions

Only the latest released version of `cc-plan-tree` on PyPI receives security fixes.

## Reporting a vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Use GitHub's private vulnerability reporting instead:
[Report a vulnerability](https://github.com/natsu0529/cc-plan-tree/security/advisories/new).

Please include:

- the version of `cc-plan-tree` and your Python version,
- a description of the issue and its impact,
- steps to reproduce, ideally with a minimal plan JSON file.

You can expect an initial response within 7 days. If the report is confirmed, a fix
will be released and you will be credited in the advisory unless you prefer otherwise.

## Scope notes

`cc-plan-tree` reads plan JSON files and renders them to Mermaid, SVG, HTML and PNG.
Reports about untrusted plan input causing code execution, file writes outside the
requested output path, or HTML/SVG injection in rendered output are in scope.
