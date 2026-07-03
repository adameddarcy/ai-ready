from datetime import datetime

from fastapi import FastAPI, HTTPException, Query

from src import gtfs

app = FastAPI(
    title="Vibe the Tube API",
    description="Developer-friendly API over Sweden's GTFS static feed.",
)


def _today() -> str:
    return datetime.now().strftime("%Y%m%d")


def _now_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


def _check_type(type: str | None) -> None:
    if type is not None and type not in gtfs.VALID_TYPES:
        raise HTTPException(400, f"type must be one of {sorted(gtfs.VALID_TYPES)}")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/transport-types")
def transport_types():
    with gtfs.get_conn() as conn:
        return gtfs.list_transport_types(conn)


@app.get("/stops")
def stops(
    q: str | None = Query(None, description="Substring match on stop/place name"),
    type: str | None = Query(None, description="train | metro | bus | boat | other"),
    lat: float | None = None,
    lon: float | None = None,
    radius_km: float | None = None,
    limit: int = Query(25, le=200),
):
    _check_type(type)
    with gtfs.get_conn() as conn:
        return gtfs.search_stops(
            conn, q=q, type=type, lat=lat, lon=lon, radius_km=radius_km, limit=limit
        )


@app.get("/routes")
def routes(
    type: str | None = None,
    stop_id: str | None = Query(None, description="Only routes serving this stop"),
    q: str | None = Query(None, description="Substring match on route name"),
    limit: int = Query(50, le=200),
):
    _check_type(type)
    with gtfs.get_conn() as conn:
        return gtfs.list_routes(conn, type=type, stop_id=stop_id, q=q, limit=limit)


@app.get("/routes/{route_id}")
def route_detail(route_id: str):
    with gtfs.get_conn() as conn:
        result = gtfs.route_detail(conn, route_id)
    if result is None:
        raise HTTPException(404, "Route not found")
    return result


@app.get("/routes/{route_id}/timetable")
def route_timetable(
    route_id: str,
    stop_id: str | None = Query(None, description="Defaults to the route's origin"),
    date: str | None = Query(None, description="YYYYMMDD, defaults to today"),
    after: str | None = Query(None, description="HH:MM:SS, defaults to now"),
    limit: int = Query(10, le=100),
):
    with gtfs.get_conn() as conn:
        if gtfs.route_detail(conn, route_id) is None:
            raise HTTPException(404, "Route not found")
        try:
            departures = gtfs.route_timetable(
                conn,
                route_id,
                stop_id=stop_id,
                date=date or _today(),
                after_time=after or _now_time(),
                limit=limit,
            )
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
    return {
        "route_id": route_id,
        "next_arrival": departures[0] if departures else None,
        "departures": departures,
    }


@app.get("/journeys")
def journeys(
    from_stop_id: str,
    to_stop_id: str,
    date: str | None = Query(None, description="YYYYMMDD, defaults to today"),
    after: str | None = Query(None, description="HH:MM:SS, defaults to now"),
    type: str | None = None,
    limit: int = Query(10, le=100),
):
    _check_type(type)
    with gtfs.get_conn() as conn:
        try:
            options = gtfs.find_journeys(
                conn,
                from_stop_id,
                to_stop_id,
                date=date or _today(),
                after_time=after or _now_time(),
                type=type,
                limit=limit,
            )
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
    if not options:
        return {"options": [], "message": "Sorry, there are no options available."}
    return {"options": options}
