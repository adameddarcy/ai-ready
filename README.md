# ai-ready

Claude Code skills and configuration for writing Python backend code. Drop this into a project to get a structured, opinionated workflow out of the box.

## What's in here

**CLAUDE.md** — Base personality ("ponytail"): lazy senior dev mode. Shortest working diff, no unnecessary abstractions, YAGNI ladder before writing anything.

**Skills** (`.claude/commands/`):

| Skill | Invoke | Purpose |
|---|---|---|
| Preflight | `/preflight` | One calibrated pass before writing code — approach, alternative, and (only where triggered) security/failure risk and volatility |
| TDD Guide | `/tdd-guide` | Red-green-refactor workflow for Python/pytest |
| Boy Scout | `/boy-scout` | Leave touched code cleaner than you found it |
| Clean Code | `/clean-code` | Clean Code principles adapted for Python — triggered by cyclomatic complexity |
| Righting Software | `/righting-software` | Volatility-based decomposition per Juval Löwy — triggered by architectural decisions |
| Python Code Review | `/py-review` | Principal-engineer review pass — readability, scalability, security, failure paths |

## New feature workflow

The skills chain together automatically when implementing a new feature (configured in CLAUDE.md):

1. **Think** — Preflight commits to an approach, and only pulls in security/failure risk when the change actually touches that surface
2. **Test** — TDD red-green-refactor, any invariants from preflight first
3. **Clean up** — Boy Scout Rule on touched code
4. **Conditionally** — Clean Code and Righting Software fire when complexity or architecture warrants it

## Usage

Clone or copy this repo's contents into your project:

```
your-project/
├── CLAUDE.md              # copy or symlink
└── .claude/
    └── commands/
        ├── preflight.md
        ├── tdd-guide.md
        ├── boy-scout.md
        ├── clean-code.md
        ├── righting-software.md
        └── py-review.md
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
