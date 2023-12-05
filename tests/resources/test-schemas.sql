-- CIRCUS

CREATE TABLE IF NOT EXISTS public.circus
(
  pk         INTEGER                  GENERATED ALWAYS AS IDENTITY
    CONSTRAINT circus_pk PRIMARY KEY,
  pid        UUID                     NOT NULL UNIQUE DEFAULT generate_ulid(),
  id         TEXT                     NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by TEXT                     NOT NULL DEFAULT 'unknown',
  geom       GEOMETRY(Point, 4326),
  lat_dd     TEXT                     GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd     TEXT                     GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm    TEXT                     GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm    TEXT                     GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED
);

CREATE INDEX IF NOT EXISTS circus_geom_idx
  on public.circus using gist (geom);

CREATE OR REPLACE TRIGGER circus_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON circus
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER circus_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON circus
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- WAYPOINT

CREATE TABLE IF NOT EXISTS public.waypoint
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
  ON public.waypoint USING gist (geom);

CREATE OR REPLACE TRIGGER waypoint_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER waypoint_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- ROUTE CONTAINER

CREATE TABLE IF NOT EXISTS public.route_container
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
  ON route_container
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER route_container_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON route_container
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- ROUTE WAYPOINT

CREATE TABLE IF NOT EXISTS public.route_waypoint
(
    pk           INTEGER                  GENERATED ALWAYS AS IDENTITY
      CONSTRAINT route_waypoint_pk PRIMARY KEY,
    route_pid    UUID                     NOT NULL
      CONSTRAINT route_waypoint_route_pid_fk REFERENCES route_container(pid) ON DELETE CASCADE,
    waypoint_pid UUID                     NOT NULL
      CONSTRAINT route_waypoint_waypoint_pid_fk REFERENCES waypoint(pid) ON DELETE CASCADE,
    sequence     INTEGER                  NOT NULL,
    updated_at   TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_by   TEXT                     NOT NULL DEFAULT 'unknown'
);

CREATE OR REPLACE TRIGGER route_waypoint_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON route_waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER route_waypoint_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON route_waypoint
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- ROUTE

CREATE OR REPLACE VIEW route AS
    WITH route_geom AS (
        SELECT rw.route_pid, st_makeline(w.geom ORDER BY rw.sequence) AS geom
        FROM route_waypoint AS rw
        JOIN waypoint w ON w.pid = rw.waypoint_pid
        GROUP BY rw.route_pid
    )
    SELECT rc.pid, rc.id, rg.geom
    FROM route_container AS rc
    FULL OUTER JOIN route_geom rg ON rc.pid = rg.route_pid;

CREATE OR REPLACE FUNCTION route_insert() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO route_container (id) VALUES (NEW.id);
    INSERT INTO route_waypoint (route_pid, waypoint_pid, sequence)
        (
            SELECT rc.pid as route_pid, w.pid as waypoint_pid, points.path[1] AS sequence
            FROM ST_dumppoints(NEW.geom) AS points
            JOIN waypoint w ON ST_DWithin(ST_Transform(w.geom, 3857) , ST_Transform(points.geom, 3857), 1000)
            JOIN route_container rc ON rc.id = NEW.id
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER route_insert_trigger
INSTEAD OF INSERT ON route
FOR EACH ROW EXECUTE FUNCTION route_insert();


CREATE OR REPLACE FUNCTION route_update() RETURNS TRIGGER AS $$
BEGIN
    UPDATE route_container SET id = NEW.id
        WHERE pid = OLD.pid;
    DELETE FROM route_waypoint
        WHERE route_pid = OLD.pid AND NEW.geom IS NOT NULL;
    INSERT INTO route_waypoint (route_pid, waypoint_pid, sequence)
        (
            SELECT OLD.pid as route_pid, w.pid as waypoint_pid, points.path[1] AS sequence
            FROM ST_dumppoints(NEW.geom) AS points
            JOIN waypoint w ON w.geom = points.geom
            WHERE NEW.geom IS NOT NULL
        );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER route_update_trigger
INSTEAD OF UPDATE ON route
FOR EACH ROW EXECUTE FUNCTION route_update();


CREATE OR REPLACE FUNCTION route_delete() RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM route_waypoint WHERE route_pid = OLD.pid;
    DELETE FROM route_container WHERE pid = OLD.pid;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER route_delete_trigger
INSTEAD OF DELETE ON route
FOR EACH ROW EXECUTE FUNCTION route_delete();
