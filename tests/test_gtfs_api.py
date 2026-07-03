"""Smoke tests against the real prebuilt data/gtfs.db (see data/README build steps)."""

import pytest
from fastapi.testclient import TestClient

from src.app import app
from src.gtfs import DB_PATH

pytestmark = pytest.mark.skipif(not DB_PATH.exists(), reason="data/gtfs.db not built")

client = TestClient(app)


def test_transport_types_are_disjoint_and_cover_all_routes():
    types = {t["type"]: t["route_count"] for t in client.get("/transport-types").json()}
    assert set(types) <= {"train", "metro", "bus", "boat", "other"}
    assert types["boat"] > 0  # regression check: route_type 1000 must bucket as boat,
    # not get swallowed by train via TEXT-affinity string comparison (100 <= '1000' <= 199)


def test_stops_search_filters_by_name():
    stops = client.get("/stops", params={"q": "Slussen", "limit": 5}).json()
    assert stops
    assert all("slussen" in s["stop_name"].lower() for s in stops)


def test_journey_with_no_shared_trip_reports_no_options():
    resp = client.get(
        "/journeys",
        params={"from_stop_id": "does-not-exist-1", "to_stop_id": "does-not-exist-2"},
    )
    assert resp.status_code == 200
    assert resp.json() == {"options": [], "message": "Sorry, there are no options available."}


def test_unknown_transport_type_is_rejected():
    resp = client.get("/stops", params={"type": "spaceship"})
    assert resp.status_code == 400


def test_unknown_route_is_404():
    resp = client.get("/routes/does-not-exist")
    assert resp.status_code == 404
