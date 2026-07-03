# Test Report

Generated: 2026-07-03, `uv run pytest`

## Result

```
6 passed, 1 warning in 0.36s
```

| Test | File | Result |
|---|---|---|
| `test_health` | `tests/test_app.py` | PASSED |
| `test_transport_types_are_disjoint_and_cover_all_routes` | `tests/test_gtfs_api.py` | PASSED |
| `test_stops_search_filters_by_name` | `tests/test_gtfs_api.py` | PASSED |
| `test_journey_with_no_shared_trip_reports_no_options` | `tests/test_gtfs_api.py` | PASSED |
| `test_unknown_transport_type_is_rejected` | `tests/test_gtfs_api.py` | PASSED |
| `test_unknown_route_is_404` | `tests/test_gtfs_api.py` | PASSED |

`tests/test_gtfs_api.py` runs against the real prebuilt `data/gtfs.db` (skipped
automatically if that file doesn't exist, e.g. in a fresh clone before running
the data build step in the README).

## Coverage

```
Name              Stmts   Miss Branch BrPart  Cover   Missing
-------------------------------------------------------------
src/__init__.py       0      0      0      0   100%
src/app.py           56     15      8      2    70%   60-62, 71, 82-96, 124-125, 128
src/gtfs.py         105     52     34      7    45%   76->79, 80-86, 91-94, 113-133, 137-140, 151-170, 177-178, 196, 208-233, 248, 256-257
-------------------------------------------------------------
TOTAL               161     67     42      9    53%
FAIL Required test coverage of 80.0% not reached. Total coverage: 52.71%
```

**Below the repo's configured 80% gate (`pyproject.toml`).** This suite is 5
smoke tests written under a hard time box, not full coverage. Biggest gaps:
`route_detail`'s termini branch, `route_timetable`'s stop_id-not-given
fallback, `find_journeys`' `type=` filter, and most of the `/routes` and
`/routes/{id}/timetable` endpoint code in `app.py`. Honest state, not silently
ignored — see `verify.md` for what was instead checked by hand via live HTTP
smoke tests.

## Lint

```
uv run ruff check src/ tests/
Found 9 errors (S608 only)
```

All 9 remaining findings are `S608` ("possible SQL injection vector through
string-based query construction") on the same pattern in `src/gtfs.py`: an
f-string builds SQL text, but every interpolated fragment is either a
constant (`TYPE_CASE_SQL`, a fixed clause string) or a `:name`-style
placeholder token generated from `range(len(services))` — actual caller
values always flow through the bound `params` dict, never through string
interpolation. Verified by reading each flagged query; ruff can't prove this
statically so it flags the pattern regardless. Left unsuppressed rather than
blanket `# noqa`'d, so a future genuine injection in this file still gets a
fresh set of eyes on the diff.

## Bugs found and fixed while getting to green

1. **Route-type bucketing silently wrong.** The CSV→SQLite import gives every
   column `TEXT` affinity. `CASE WHEN route_type BETWEEN 100 AND 199` compared
   `'1000'` (boat, route_type 1000) as a *string* — `'100' <= '1000' <= '199'`
   is true lexicographically — so every boat route was mis-bucketed as
   `train`. Fixed with explicit `CAST(route_type AS INTEGER)` in
   `TYPE_CASE_SQL`. Same TEXT-affinity trap existed for `stop_sequence`
   ordering/comparisons (`'10' < '9'` as strings) — fixed the same way in
   `route_detail` and `find_journeys`.
2. **Calendar exceptions never applied.** `calendar_dates.exception_type`
   comes back from sqlite3 as the string `"1"`/`"2"`, but the code compared it
   to the integer `1`. This dataset encodes *all* service exclusively via
   `calendar_dates` (every weekly flag in `calendar.txt` is `0`), so this bug
   meant `service_ids_for_date` always returned an empty set — every
   timetable/journey query would have silently returned "no options" for
   every date. Fixed by comparing to the string `"1"`.
3. **Connection leak.** `with gtfs.get_conn() as conn:` looked like it closed
   the connection on exit, but `sqlite3.Connection.__exit__` only
   commits/rolls back a transaction — it never closes the file handle. Every
   request leaked an open handle to the 1.5GB `gtfs.db`. Fixed by making
   `get_conn()` a `@contextmanager` generator that closes in a `finally`
   block; confirmed no leaked `gtfs.db` file descriptors remained after a
   batch of live requests (see `verify.md`).
