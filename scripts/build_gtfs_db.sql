.mode csv
.import agency.txt agency
.import routes.txt routes
.import stops.txt stops
.import trips.txt trips
.import calendar.txt calendar
.import calendar_dates.txt calendar_dates
.import stop_times.txt stop_times

CREATE INDEX idx_stop_times_trip ON stop_times(trip_id, stop_sequence);
CREATE INDEX idx_stop_times_stop ON stop_times(stop_id);
CREATE INDEX idx_trips_route ON trips(route_id);
CREATE INDEX idx_trips_service ON trips(service_id);
CREATE INDEX idx_trips_id ON trips(trip_id);
CREATE INDEX idx_routes_id ON routes(route_id);
CREATE INDEX idx_routes_agency ON routes(agency_id);
CREATE INDEX idx_routes_type ON routes(route_type);
CREATE INDEX idx_stops_id ON stops(stop_id);
CREATE INDEX idx_stops_name ON stops(stop_name COLLATE NOCASE);
CREATE INDEX idx_calendar_service ON calendar(service_id);
CREATE INDEX idx_calendar_dates ON calendar_dates(service_id, date);
CREATE INDEX idx_agency_id ON agency(agency_id);
ANALYZE;
