# ai-ready

Claude Code skills and configuration for writing Python backend code. Drop this into a project to get a structured, opinionated workflow out of the box.

## What's in here

**CLAUDE.md** — Base personality ("ponytail"): lazy senior dev mode. Shortest working diff, no unnecessary abstractions, YAGNI ladder before writing anything.

**Skills** (`.claude/commands/`):

| Skill | Invoke | Purpose |
|---|---|---|
| Socratic Preflight | `/socratic-preflight` | Five-question self-interrogation before writing code — surfaces assumptions, alternatives, and failure modes |
| Threat Check | `/threat-check` | Quick STRIDE-based threat model pass — checks existing threat models, maps attack surface |
| Failure Modes | `/failure-modes` | Define failure modes as invariants, test them before the happy path |
| TDD Guide | `/tdd-guide` | Red-green-refactor workflow for Python/pytest |
| Boy Scout | `/boy-scout` | Leave touched code cleaner than you found it |
| Clean Code | `/clean-code` | Clean Code principles adapted for Python — triggered by cyclomatic complexity |
| Righting Software | `/righting-software` | Volatility-based decomposition per Juval Löwy — triggered by architectural decisions |

## New feature workflow

The skills chain together automatically when implementing a new feature (configured in CLAUDE.md):

1. **Think** — Socratic Preflight questions assumptions and commits to an approach
2. **Secure** — Threat Check reviews security surface (if applicable)
3. **Define failure** — Failure Modes produces testable invariants
4. **Test** — TDD red-green-refactor, failure tests first
5. **Clean up** — Boy Scout Rule on touched code
6. **Conditionally** — Clean Code and Righting Software fire when complexity or architecture warrants it

## Usage

Clone or copy this repo's contents into your project:

```
your-project/
├── CLAUDE.md              # copy or symlink
└── .claude/
    └── commands/
        ├── socratic-preflight.md
        ├── threat-check.md
        ├── failure-modes.md
        ├── tdd-guide.md
        ├── boy-scout.md
        ├── clean-code.md
        └── righting-software.md
```

Skills are available immediately via `/skill-name` in Claude Code. The workflow ordering is driven by CLAUDE.md — adjust the "New features" section to change what auto-triggers.

## Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync              # install dependencies
uv run pytest        # run tests
uv run pytest --cov  # run tests with coverage
uv run ruff check .  # lint
uv run ruff format . # format
```
