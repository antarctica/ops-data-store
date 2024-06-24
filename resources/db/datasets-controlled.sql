SET search_path TO controlled, public;

-- DEPOT

CREATE TABLE IF NOT EXISTS controlled.depot
(
  pk                         INTEGER GENERATED ALWAYS AS IDENTITY
    CONSTRAINT depot_pk PRIMARY KEY,
  pid                        UUID                     NOT NULL UNIQUE DEFAULT generate_ulid(),
  id                         TEXT                     NOT NULL,
  updated_at                 TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by                 TEXT                     NOT NULL DEFAULT 'unknown',
  geom                       GEOMETRY(Point, 4326),
  lat_dd                     TEXT GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd                     TEXT GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm                    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm                    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED,
  name                       TEXT,
  status                     TEXT,
  restrictions               TEXT,
  access                     TEXT,
  owner                      TEXT,
  depots_no                  INT,
  elevation_m                FLOAT,
  installed_at               DATE,
  position_updated_at        DATE,
  last_visited_at            DATE,
  last_visited_by            TEXT,
  last_raised_at             DATE,
  fuel_bulk_avtur_ltrs       INT,
  fuel_drums_avtur_205ltr    INT,
  fuel_drums_herc_180ltr     INT,
  fuel_drums_fssi_180ltr     INT,
  fuel_drums_petrol_205ltr   INT,
  fuel_drums_kero            INT,
  fuel_drums_empty           INT,
  fuel_total_ltrs            INT,
  hazards                    TEXT,
  terrain                    TEXT,
  annual_drift_rate_m        FLOAT,
  annual_snow_accumulation_m FLOAT,
  comments                   TEXT,
  info_rothera               TEXT,
  info_cambridge             TEXT
);

CREATE INDEX IF NOT EXISTS depot_geom_idx
  on controlled.depot using gist (geom);

CREATE OR REPLACE TRIGGER depot_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.depot
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER depot_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.depot
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- INSTRUMENT

CREATE TABLE IF NOT EXISTS controlled.instrument
(
  pk                         INTEGER                  GENERATED ALWAYS AS IDENTITY
    CONSTRAINT instrument_pk PRIMARY KEY,
  pid                        UUID                     NOT NULL UNIQUE DEFAULT generate_ulid(),
  id                         TEXT                     NOT NULL,
  updated_at                 TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by                 TEXT                     NOT NULL DEFAULT 'unknown',
  geom                       GEOMETRY(Point, 4326),
  lat_dd                     TEXT                     GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd                     TEXT                     GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm                    TEXT                     GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm                    TEXT                     GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED,
  name                       TEXT,
  other_names                TEXT,
  status                     TEXT,
  proposed_visit             TEXT,
  restrictions               TEXT,
  access                     TEXT,
  instrument_type            TEXT,
  owner                      TEXT,
  elevation_m                FLOAT,
  installed_at               DATE,
  position_updated_at        DATE,
  last_visited_at            DATE,
  last_visited_by            TEXT,
  last_raised_at             DATE,
  recovered_at               DATE,
  service_interval_years     INTEGER,
  hazards                    TEXT,
  terrain                    TEXT,
  annual_drift_rate_m        FLOAT,
  annual_snow_accumulation_m FLOAT,
  satellite_comms            TEXT,
  comments                   TEXT,
  info_rothera               TEXT,
  info_cambridge             TEXT
);

CREATE INDEX IF NOT EXISTS instrument_geom_idx
  on controlled.instrument using gist (geom);

CREATE OR REPLACE TRIGGER instrument_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.instrument
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER instrument_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.instrument
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- WAYPOINT

CREATE TABLE IF NOT EXISTS controlled.waypoint
(
  pk               INTEGER                  GENERATED ALWAYS AS IDENTITY
    CONSTRAINT waypoint_pk PRIMARY KEY,
  pid              UUID                     NOT NULL UNIQUE DEFAULT generate_ulid(),
  id               TEXT                     NOT NULL,
  name             TEXT,
  colocated_with   TEXT,
  last_accessed_at DATE,
  last_accessed_by TEXT,
  comment          TEXT,
  updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by       TEXT                     NOT NULL DEFAULT 'unknown',
  geom             GEOMETRY(Point, 4326),
  lat_dd           TEXT                     GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd           TEXT                     GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm          TEXT                     GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm          TEXT                     GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED
);

CREATE INDEX IF NOT EXISTS waypoint_geom_idx
  ON controlled.waypoint USING gist (geom);

CREATE OR REPLACE TRIGGER waypoint_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER waypoint_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- ROUTE CONTAINER

CREATE TABLE IF NOT EXISTS controlled.route_container
(
  pk         INTEGER                  GENERATED ALWAYS AS IDENTITY
    CONSTRAINT route_pk PRIMARY KEY,
  pid        UUID                     NOT NULL UNIQUE DEFAULT generate_ulid(),
  id         TEXT                     NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by TEXT                     NOT NULL DEFAULT 'unknown'
);

CREATE OR REPLACE TRIGGER route_container_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.route_container
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER route_container_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.route_container
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- ROUTE WAYPOINT

CREATE TABLE IF NOT EXISTS controlled.route_waypoint
(
    pk           INTEGER                  GENERATED ALWAYS AS IDENTITY
      CONSTRAINT route_waypoint_pk PRIMARY KEY,
    route_pid    UUID                     NOT NULL
      CONSTRAINT route_waypoint_route_pid_fk REFERENCES controlled.route_container(pid) ON DELETE CASCADE,
    waypoint_pid UUID                     NOT NULL
      CONSTRAINT route_waypoint_waypoint_pid_fk REFERENCES controlled.waypoint(pid) ON DELETE CASCADE,
    sequence     INTEGER                  NOT NULL,
    updated_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_by   TEXT                     NOT NULL DEFAULT 'unknown'
);

CREATE OR REPLACE TRIGGER route_waypoint_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.route_waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER route_waypoint_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.route_waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- ROUTE

CREATE OR REPLACE VIEW controlled.route AS
    WITH route_geom AS (
        SELECT rw.route_pid, st_makeline(w.geom ORDER BY rw.sequence)::geometry(LINESTRING, 4326) AS geom
        FROM controlled.route_waypoint AS rw
        JOIN controlled.waypoint w ON w.pid = rw.waypoint_pid
        GROUP BY rw.route_pid
    )
    SELECT rc.pid, rc.id, rg.geom
    FROM controlled.route_container AS rc
    FULL OUTER JOIN route_geom rg ON rc.pid = rg.route_pid;

CREATE OR REPLACE FUNCTION route_insert() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO controlled.route_container (id) VALUES (NEW.id);
    INSERT INTO controlled.route_waypoint (route_pid, waypoint_pid, sequence)
        (
            SELECT rc.pid as route_pid, w.pid as waypoint_pid, points.path[1] AS sequence
            FROM ST_dumppoints(NEW.geom) AS points
            JOIN controlled.waypoint w ON ST_DWithin(ST_Transform(w.geom, 3857) , ST_Transform(points.geom, 3857), 1000)
            JOIN controlled.route_container rc ON rc.id = NEW.id
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER route_insert_trigger
INSTEAD OF INSERT ON controlled.route
FOR EACH ROW EXECUTE FUNCTION route_insert();

CREATE OR REPLACE FUNCTION route_update() RETURNS TRIGGER AS $$
BEGIN
    UPDATE controlled.route_container SET id = NEW.id
        WHERE pid = OLD.pid;
    DELETE FROM route_waypoint
        WHERE route_pid = OLD.pid AND NEW.geom IS NOT NULL;
    INSERT INTO controlled.route_waypoint (route_pid, waypoint_pid, sequence)
        (
            SELECT OLD.pid as route_pid, w.pid as waypoint_pid, points.path[1] AS sequence
            FROM ST_dumppoints(NEW.geom) AS points
            JOIN controlled.waypoint w ON w.geom = points.geom
            WHERE NEW.geom IS NOT NULL
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER route_update_trigger
INSTEAD OF UPDATE ON controlled.route
FOR EACH ROW EXECUTE FUNCTION route_update();

CREATE OR REPLACE FUNCTION route_delete() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM controlled.route_waypoint WHERE route_pid = OLD.pid;
    DELETE FROM controlled.route_container WHERE pid = OLD.pid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER route_delete_trigger
INSTEAD OF DELETE ON controlled.route
FOR EACH ROW EXECUTE FUNCTION route_delete();

-- EO ACQUISITION AOIs

CREATE TABLE IF NOT EXISTS controlled.eo_acq_aoi
(
  pk         INTEGER                  GENERATED ALWAYS AS IDENTITY
    CONSTRAINT eo_acq_aoi_pk PRIMARY KEY,
  pid        UUID                     NOT NULL UNIQUE DEFAULT generate_ulid(),
  id         TEXT                     NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by TEXT                     NOT NULL DEFAULT 'unknown',
  geom       GEOMETRY(Polygon, 4326)  NOT NULL
);

CREATE INDEX IF NOT EXISTS eo_acq_aoi_geom_idx
  ON controlled.eo_acq_aoi USING gist (geom);

CREATE OR REPLACE TRIGGER eo_acq_aoi_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.eo_acq_aoi
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER eo_acq_aoi_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.eo_acq_aoi
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();
