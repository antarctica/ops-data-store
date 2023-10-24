-- CIRCUS

CREATE TABLE IF NOT EXISTS public.circus
(
  pk         INTEGER GENERATED ALWAYS AS IDENTITY
    CONSTRAINT circus_pk PRIMARY KEY,
  pid        UUID                     NOT NULL DEFAULT generate_ulid(),
  id         TEXT                     NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by TEXT                     NOT NULL DEFAULT 'unknown',
  geom       GEOMETRY(Point, 4326),
  lat_dd     TEXT GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd     TEXT GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED
);

CREATE INDEX IF NOT EXISTS circus_geom_idx
  on public.circus using gist (geom);

CREATE TRIGGER circus_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON circus
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER circus_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON circus
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();
