-- [SCHEMAS]

-- allow ods_admin to create new schemas (and objects within)
GRANT CREATE ON DATABASE "{{ ops-data-store-dev }}" TO ods_admin;

-- [CONTROLLED SCHEMA]
--

GRANT USAGE, CREATE ON SCHEMA controlled TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA controlled TO ods_admin;

GRANT USAGE ON SCHEMA controlled TO ods_app_eo_acq_script;

GRANT USAGE ON SCHEMA controlled TO ods_write_fo;
GRANT USAGE ON SCHEMA controlled TO ods_write_au;
GRANT USAGE ON SCHEMA controlled TO ods_read;

-- DEPOT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.depot TO ods_write_fo;
GRANT SELECT ON TABLE controlled.depot TO ods_read;

-- INSTRUMENT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.instrument TO ods_write_fo;
GRANT SELECT ON TABLE controlled.instrument TO ods_read;

-- WAYPOINT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.waypoint TO ods_write_au;
GRANT SELECT ON TABLE controlled.waypoint TO ods_read;

-- ROUTE CONTAINER

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.route_container TO ods_write_au;
GRANT SELECT ON TABLE controlled.route_container TO ods_read;

-- ROUTE WAYPOINT

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.route_waypoint TO ods_write_au;
GRANT SELECT ON TABLE controlled.route_waypoint TO ods_read;

-- ROUTE
GRANT SELECT, INSERT, UPDATE, DELETE ON controlled.route TO ods_write_au;
GRANT SELECT ON controlled.route TO ods_read;

-- EO ACQUISITION AOIs
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.eo_acq_aoi TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE controlled.eo_acq_aoi TO ods_write_fo;
GRANT SELECT ON TABLE controlled.eo_acq_aoi TO ods_read;

-- [PUBLIC]
--

-- LAYER STYLES
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.layer_styles TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.layer_styles TO ods_write_fo;
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE public.layer_styles TO ods_write_au;

GRANT USAGE, SELECT ON SEQUENCE public.layer_styles_id_seq TO ods_admin;
GRANT USAGE, SELECT ON SEQUENCE public.layer_styles_id_seq TO ods_write_fo;
GRANT USAGE, SELECT ON SEQUENCE public.layer_styles_id_seq TO ods_write_au;

GRANT SELECT ON TABLE public.layer_styles TO ods_read;

-- [PLANNING FIELD OPS SCHEMA]

GRANT USAGE, CREATE ON SCHEMA planning_field_ops TO ods_admin;
GRANT USAGE, CREATE ON SCHEMA planning_field_ops TO ods_write_fo;
