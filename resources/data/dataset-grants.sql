-- DEPOT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.depot TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.depot TO ods_write_fo;
GRANT SELECT ON TABLE magic_managed.depot TO ods_read;

-- INSTRUMENT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.instrument TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.instrument TO ods_write_fo;
GRANT SELECT ON TABLE magic_managed.instrument TO ods_read;

-- WAYPOINT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.waypoint TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.waypoint TO ods_write_au;
GRANT SELECT ON TABLE magic_managed.waypoint TO ods_read;

-- ROUTE CONTAINER

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.route_container TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.route_container TO ods_write_au;
GRANT SELECT ON TABLE magic_managed.route_container TO ods_read;

-- ROUTE WAYPOINT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.route_waypoint TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE magic_managed.route_waypoint TO ods_write_au;
GRANT SELECT ON TABLE magic_managed.route_waypoint TO ods_read;

-- ROUTE
GRANT SELECT, INSERT, UPDATE, DELETE ON magic_managed.route TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON magic_managed.route TO ods_write_au;
GRANT SELECT ON magic_managed.route TO ods_read;

-- LAYER STYLES
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE layer_styles TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE layer_styles TO ods_write_fo;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE layer_styles TO ods_write_au;
GRANT SELECT ON TABLE layer_styles TO ods_read;
