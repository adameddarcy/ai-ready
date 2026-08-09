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

## Transit API (Sweden GTFS)

`src/app.py` is a developer-friendly FastAPI layer over Sweden's static GTFS
feed (see `transit-api.md` for the brief). It never exposes raw GTFS rows —
routes are collapsed into four transport modes (`train`/`metro`/`bus`/`boat`,
plus `other`), and stop/route/journey/timetable queries hide the
trips↔stop_times↔calendar joins GTFS requires.

**Data setup** (not committed — `data/` is gitignored, ~1.5GB db file):

```bash
Z=/path/to/gtfs-sweden-3-static.zip
mkdir -p data && cd data
unzip -o "$Z" agency.txt routes.txt stops.txt trips.txt stop_times.txt calendar.txt calendar_dates.txt -d .
# shapes.txt (3GB) is intentionally skipped - not needed for these endpoints
sqlite3 gtfs.db < ../scripts/build_gtfs_db.sql   # or see git history for the raw commands
rm agency.txt routes.txt stops.txt trips.txt stop_times.txt calendar.txt calendar_dates.txt
```

**Run:** `uv run uvicorn src.app:app --reload`

**Endpoints:**
- `GET /transport-types` — the four modes + counts
- `GET /stops?q=&type=&lat=&lon=&radius_km=` — search/filter stops (name substring or geo radius)
- `GET /routes?type=&stop_id=&q=` — filter routes
- `GET /routes/{route_id}` — route detail incl. origin/destination termini
- `GET /routes/{route_id}/timetable?stop_id=&date=&after=` — next arrivals at a stop, defaults to now
- `GET /journeys?from_stop_id=&to_stop_id=&date=&type=` — direct trip options between two stops, or `{"options": [], "message": "..."}`

Known simplifications (see `ponytail:` comments in `src/gtfs.py`): geography
is name-substring or lat/lon radius (GTFS has no "city" field), route_type
mapping buckets Google's extended codes into the four requested modes, and
journeys only cover single-vehicle direct trips (no transfers/multi-leg
routing).
