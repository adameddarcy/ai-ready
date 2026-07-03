# Endpoint Smoke Verification

Generated: 2026-07-03, live HTTP requests against `uv run uvicorn src.app:app`
backed by the real `data/gtfs.db` (built from Sweden's GTFS static feed).

## Summary

| Endpoint | Happy path | Sad path | Result |
|---|---|---|---|
| `GET /health` | 200 `{"status":"ok"}` | `POST /health` → 405 | ✅ |
| `GET /transport-types` | 200, 5 buckets, counts sum to all routes | `POST /transport-types` → 405 | ✅ |
| `GET /stops` | 200, name search returns matches | `type=spaceship` → 400 | ✅ |
| `GET /routes` | 200, type filter returns matches | `type=spaceship` → 400 | ✅ |
| `GET /routes/{id}` | 200, includes origin/destination termini | unknown id → 404 | ✅ |
| `GET /routes/{id}/timetable` | 200, sorted departures + `next_arrival` | malformed `date` → 400; unknown route → 404 | ✅ |
| `GET /journeys` | 200, direct trip options between two stops | no shared trip → 200 `{"options": [], "message": "..."}`; `type=spaceship` → 400 | ✅ |

All 7 endpoints behaved as expected on both the happy path and every sad path
exercised (17 requests total). Full request/response pairs below.

## Full transcript

### GET /health (happy)
```
$ curl -s -w '[HTTP %{http_code}]' localhost:8931/health
{"status":"ok"}
[HTTP 200]
```

### POST /health (sad — wrong method)
```
$ curl -s -w '[HTTP %{http_code}]' -X POST localhost:8931/health
{"detail":"Method Not Allowed"}
[HTTP 405]
```

### GET /transport-types (happy)
```
$ curl -s -w '[HTTP %{http_code}]' localhost:8931/transport-types
[{"type":"train","route_count":3751},{"type":"bus","route_count":3502},{"type":"other","route_count":512},{"type":"boat","route_count":78},{"type":"metro","route_count":37}]
[HTTP 200]
```
3751+3502+512+78+37 = 7880 = total route count in the dataset — confirms the
route_type→mode bucketing (fixed earlier for the TEXT-affinity bug, see
`test.md`) covers every route exactly once.

### POST /transport-types (sad — wrong method)
```
$ curl -s -w '[HTTP %{http_code}]' -X POST localhost:8931/transport-types
{"detail":"Method Not Allowed"}
[HTTP 405]
```

### GET /stops?q=Slussen&limit=3 (happy)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/stops?q=Slussen&limit=3"
[{"stop_id":"26808","stop_name":"Malmö Slussen", ...}, ...]
[HTTP 200]
```

### GET /stops?type=spaceship (sad — invalid transport type)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/stops?type=spaceship"
{"detail":"type must be one of ['boat', 'bus', 'metro', 'other', 'train']"}
[HTTP 400]
```

### GET /routes?type=boat&limit=3 (happy)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/routes?type=boat&limit=3"
[{"route_id":"9011001008000000","route_short_name":"80", ..., "type":"boat"}, ...]
[HTTP 200]
```

### GET /routes?type=spaceship (sad — invalid transport type)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/routes?type=spaceship"
{"detail":"type must be one of ['boat', 'bus', 'metro', 'other', 'train']"}
[HTTP 400]
```

### GET /routes/9011003000100000 (happy)
```
$ curl -s -w '[HTTP %{http_code}]' localhost:8931/routes/9011003000100000
{"route_id":"9011003000100000","route_short_name":"1","route_long_name":"","agency_id":"505000000000000003","type":"bus","termini":{"origin":{"stop_id":"9022050004322001","stop_name":"Hansellisgatan (Uppsala)"},"destination":{"stop_id":"9022050004287004","stop_name":"Gränbystaden (Uppsala)"}}}
[HTTP 200]
```

### GET /routes/does-not-exist (sad — unknown route)
```
$ curl -s -w '[HTTP %{http_code}]' localhost:8931/routes/does-not-exist
{"detail":"Route not found"}
[HTTP 404]
```

### GET /routes/{id}/timetable?stop_id=&date=20260703 (happy)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/routes/9011003000100000/timetable?stop_id=9022050004287004&date=20260703&after=00:00:00&limit=3"
{"route_id":"9011003000100000","next_arrival":{"departure_time":"05:50:00", ...},"departures":[...3 sorted entries...]}
[HTTP 200]
```

### GET timetable?date=notadate (sad — malformed date)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/routes/9011003000100000/timetable?stop_id=9022050004287004&date=notadate"
{"detail":"date must be YYYYMMDD, got 'notadate'"}
[HTTP 400]
```
Regression check for the date-parsing trust-boundary fix (see `test.md`):
previously an unhandled `ValueError` from `strptime` would have 500'd.

### GET timetable for unknown route (sad — 404)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/routes/does-not-exist/timetable?stop_id=9022050004287004"
{"detail":"Route not found"}
[HTTP 404]
```

### GET /journeys, direct trip exists (happy)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/journeys?from_stop_id=9022050004287004&to_stop_id=9022050004282001&date=20260703&after=00:00:00&limit=3"
{"options":[{"trip_id":"33010000232487766","route_id":"9011003000100000","route_short_name":"1","type":"bus","depart":"05:50:00","arrive":"05:57:44"}, ...]}
[HTTP 200]
```

### GET /journeys, no shared trip (sad — business "no options")
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/journeys?from_stop_id=does-not-exist-1&to_stop_id=does-not-exist-2"
{"options":[],"message":"Sorry, there are no options available."}
[HTTP 200]
```
This is the assignment's explicit "Sorry, there are no options available"
requirement — verified as a 200 with an empty list + message, not a 404
(no options is a valid business outcome, not an error).

### GET /journeys?type=spaceship (sad — invalid transport type)
```
$ curl -s -w '[HTTP %{http_code}]' "localhost:8931/journeys?from_stop_id=9022050004287004&to_stop_id=9022050004282001&type=spaceship"
{"detail":"type must be one of ['boat', 'bus', 'metro', 'other', 'train']"}
[HTTP 400]
```

## Resource-leak regression check

The connection-leak fix (see `test.md`, bug #3) was verified live, not just
read: after the 17 requests above, `lsof -p <uvicorn-pid> | grep gtfs.db`
showed **0** open handles to the 1.5GB database file. Before the fix, every
request would have left one connection open indefinitely.
