"""Read-only query layer over the prebuilt Sweden GTFS SQLite snapshot.

Build the snapshot with: see README "Data setup". This module never touches
the raw GTFS CSVs at request time - all of that is baked into data/gtfs.db.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "gtfs.db"

# ponytail: Sweden's GTFS feed uses Google's "extended" route_type codes
# (hundreds groups) rather than plain 0-7. We collapse them into the four
# transport modes the API promises, plus "other" for anything left over
# (e.g. 1501 demand-responsive taxi). Ceiling: a handful of niche modes
# (funicular, aerial tram) fall into "other" instead of getting their own
# bucket - fine for this dataset, would need real mapping if scope grows.
## ponytail: the GTFS CSV import gives every column TEXT affinity, so
## unquoted numeric literals in SQL get coerced to TEXT for comparison
## (e.g. '1000' sorts lexicographically between '100' and '199'). Cast
## route_type to INTEGER explicitly rather than rebuilding the DB with
## typed columns.
TYPE_CASE_SQL = """
CASE
    WHEN CAST(route_type AS INTEGER) IN (0, 1)
        OR CAST(route_type AS INTEGER) BETWEEN 900 AND 999 THEN 'metro'
    WHEN CAST(route_type AS INTEGER) BETWEEN 400 AND 599 THEN 'metro'
    WHEN CAST(route_type AS INTEGER) = 2
        OR CAST(route_type AS INTEGER) BETWEEN 100 AND 199 THEN 'train'
    WHEN CAST(route_type AS INTEGER) = 3
        OR CAST(route_type AS INTEGER) BETWEEN 200 AND 299
        OR CAST(route_type AS INTEGER) BETWEEN 700 AND 899 THEN 'bus'
    WHEN CAST(route_type AS INTEGER) = 4
        OR CAST(route_type AS INTEGER) BETWEEN 1000 AND 1299 THEN 'boat'
    ELSE 'other'
END
"""

VALID_TYPES = {"train", "metro", "bus", "boat", "other"}


@contextmanager
def get_conn():
    # ponytail: plain sqlite3.Connection.__exit__ only commits/rolls back -
    # it does NOT close the connection, which leaked a file handle on every
    # request. Wrapping as a generator context manager makes `with
    # gtfs.get_conn() as conn:` at call sites actually close on exit.
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def list_transport_types(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        f"SELECT {TYPE_CASE_SQL} AS type, COUNT(*) AS route_count "
        "FROM routes GROUP BY type ORDER BY route_count DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def search_stops(
    conn: sqlite3.Connection,
    q: str | None = None,
    type: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
    limit: int = 25,
) -> list[dict]:
    clauses, params = [], {}
    if q:
        clauses.append("stop_name LIKE :q COLLATE NOCASE")
        params["q"] = f"%{q}%"
    if type:
        clauses.append(
            "EXISTS (SELECT 1 FROM stop_times st "
            "JOIN trips t ON t.trip_id = st.trip_id "
            "JOIN routes r ON r.route_id = t.route_id "
            f"WHERE st.stop_id = stops.stop_id AND ({TYPE_CASE_SQL}) = :type)"
        )
        params["type"] = type
    if lat is not None and lon is not None and radius_km is not None:
        # ponytail: flat-earth degree bounding box, not haversine - fine at
        # city/region scale (a few km), would skew near the poles or at
        # country-wide radii.
        deg = radius_km / 111.0
        clauses.append("stop_lat BETWEEN :lat_min AND :lat_max")
        clauses.append("stop_lon BETWEEN :lon_min AND :lon_max")
        params.update(
            lat_min=lat - deg, lat_max=lat + deg, lon_min=lon - deg, lon_max=lon + deg
        )
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        "SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops "
        f"{where} ORDER BY stop_name LIMIT :limit"
    )
    params["limit"] = limit
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def list_routes(
    conn: sqlite3.Connection,
    type: str | None = None,
    stop_id: str | None = None,
    q: str | None = None,
    limit: int = 50,
) -> list[dict]:
    clauses, params = [], {"limit": limit}
    if type:
        clauses.append(f"({TYPE_CASE_SQL}) = :type")
        params["type"] = type
    if q:
        clauses.append(
            "(route_short_name LIKE :q OR route_long_name LIKE :q COLLATE NOCASE)"
        )
        params["q"] = f"%{q}%"
    if stop_id:
        clauses.append(
            "route_id IN (SELECT t.route_id FROM stop_times st "
            "JOIN trips t ON t.trip_id = st.trip_id WHERE st.stop_id = :stop_id)"
        )
        params["stop_id"] = stop_id
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sql = (
        f"SELECT route_id, route_short_name, route_long_name, agency_id, "
        f"{TYPE_CASE_SQL} AS type FROM routes {where} LIMIT :limit"
    )
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def _representative_trip(conn: sqlite3.Connection, route_id: str) -> str | None:
    row = conn.execute(
        "SELECT trip_id FROM trips WHERE route_id = :r LIMIT 1", {"r": route_id}
    ).fetchone()
    return row["trip_id"] if row else None


def route_detail(conn: sqlite3.Connection, route_id: str) -> dict | None:
    route = conn.execute(
        f"SELECT route_id, route_short_name, route_long_name, agency_id, "
        f"{TYPE_CASE_SQL} AS type FROM routes WHERE route_id = :r",
        {"r": route_id},
    ).fetchone()
    if not route:
        return None
    result = dict(route)
    trip_id = _representative_trip(conn, route_id)
    result["termini"] = None
    if trip_id:
        ends = conn.execute(
            "SELECT s.stop_id, s.stop_name, st.stop_sequence FROM stop_times st "
            "JOIN stops s ON s.stop_id = st.stop_id "
            "WHERE st.trip_id = :t ORDER BY CAST(st.stop_sequence AS INTEGER)",
            {"t": trip_id},
        ).fetchall()
        if ends:
            origin, dest = ends[0], ends[-1]
            result["termini"] = {
                "origin": {"stop_id": origin["stop_id"], "stop_name": origin["stop_name"]},
                "destination": {
                    "stop_id": dest["stop_id"],
                    "stop_name": dest["stop_name"],
                },
            }
    return result


def service_ids_for_date(conn: sqlite3.Connection, date: str) -> set[str]:
    """date is YYYYMMDD. Combines calendar weekday rules with exceptions."""
    try:
        weekday = datetime.strptime(date, "%Y%m%d").strftime("%A").lower()
    except ValueError:
        raise ValueError(f"date must be YYYYMMDD, got {date!r}") from None
    base = {
        r["service_id"]
        for r in conn.execute(
            f"SELECT service_id FROM calendar WHERE {weekday} = 1 "
            "AND start_date <= :d AND end_date >= :d",
            {"d": date},
        ).fetchall()
    }
    for r in conn.execute(
        "SELECT service_id, exception_type FROM calendar_dates WHERE date = :d",
        {"d": date},
    ).fetchall():
        # ponytail: exception_type comes back as the string "1"/"2" because
        # the CSV import gave every column TEXT affinity - compare as text.
        if r["exception_type"] == "1":
            base.add(r["service_id"])
        else:
            base.discard(r["service_id"])
    return base


def route_timetable(
    conn: sqlite3.Connection,
    route_id: str,
    stop_id: str | None,
    date: str,
    after_time: str,
    limit: int = 10,
) -> list[dict]:
    services = service_ids_for_date(conn, date)
    if not services:
        return []
    if stop_id is None:
        trip_id = _representative_trip(conn, route_id)
        if not trip_id:
            return []
        first = conn.execute(
            "SELECT stop_id FROM stop_times WHERE trip_id = :t "
            "ORDER BY CAST(stop_sequence AS INTEGER) LIMIT 1",
            {"t": trip_id},
        ).fetchone()
        stop_id = first["stop_id"] if first else None
    if not stop_id:
        return []
    placeholders = ",".join(f":s{i}" for i in range(len(services)))
    params = {f"s{i}": sid for i, sid in enumerate(services)}
    params.update(stop_id=stop_id, route_id=route_id, after=after_time, limit=limit)
    sql = (
        "SELECT st.departure_time, st.arrival_time, t.trip_id, t.trip_headsign "
        "FROM stop_times st JOIN trips t ON t.trip_id = st.trip_id "
        "WHERE t.route_id = :route_id AND st.stop_id = :stop_id "
        f"AND t.service_id IN ({placeholders}) AND st.departure_time >= :after "
        "ORDER BY st.departure_time LIMIT :limit"
    )
    return [dict(r) for r in conn.execute(sql, params).fetchall()]


def find_journeys(
    conn: sqlite3.Connection,
    from_stop_id: str,
    to_stop_id: str,
    date: str,
    after_time: str,
    type: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """Direct (single-vehicle) trips passing from_stop before to_stop."""
    services = service_ids_for_date(conn, date)
    if not services:
        return []
    placeholders = ",".join(f":s{i}" for i in range(len(services)))
    params = {f"s{i}": sid for i, sid in enumerate(services)}
    params.update(
        from_stop_id=from_stop_id, to_stop_id=to_stop_id, after=after_time, limit=limit
    )
    type_clause = ""
    if type:
        type_clause = f"AND ({TYPE_CASE_SQL}) = :type"
        params["type"] = type
    sql = f"""
        SELECT t.trip_id, r.route_id, r.route_short_name, r.route_long_name,
               {TYPE_CASE_SQL} AS type,
               a.departure_time AS depart, b.arrival_time AS arrive
        FROM stop_times a
        JOIN stop_times b ON a.trip_id = b.trip_id
            AND CAST(b.stop_sequence AS INTEGER) > CAST(a.stop_sequence AS INTEGER)
        JOIN trips t ON t.trip_id = a.trip_id
        JOIN routes r ON r.route_id = t.route_id
        WHERE a.stop_id = :from_stop_id AND b.stop_id = :to_stop_id
          AND t.service_id IN ({placeholders})
          AND a.departure_time >= :after
          {type_clause}
        ORDER BY a.departure_time LIMIT :limit
    """
    return [dict(r) for r in conn.execute(sql, params).fetchall()]
