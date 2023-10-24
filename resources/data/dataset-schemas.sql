-- DEPOT

CREATE TABLE IF NOT EXISTS public.depot
(
  pk                         INTEGER GENERATED ALWAYS AS IDENTITY
    CONSTRAINT depot_pk PRIMARY KEY,
  pid                        UUID                     NOT NULL DEFAULT generate_ulid(),
  id                         TEXT                     NOT NULL,
  updated_at                 TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  etag                       TEXT GENERATED ALWAYS AS (md5(id || '__' || st_asewkt(geom, 10))) STORED,
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
  fuel_avtur_bulk_ltrs       INT,
  fuel_avtur_drums           INT,
  fuel_drums_herc            INT,
  fuel_no_fssi               INT,
  fuel_drums_petrol          INT,
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
  on public.depot using gist (geom);

CREATE TRIGGER depot_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON depot
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER depot_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON depot
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();

-- INSTRUMENT

CREATE TABLE IF NOT EXISTS public.instrument
(
  pk                         INTEGER GENERATED ALWAYS AS IDENTITY
    CONSTRAINT instrument_pk PRIMARY KEY,
  pid                        UUID                     NOT NULL DEFAULT generate_ulid(),
  id                         TEXT                     NOT NULL,
  updated_at                 TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  etag                       TEXT GENERATED ALWAYS AS (md5(id || '__' || st_asewkt(geom, 10))) STORED,
  updated_by                 TEXT                     NOT NULL DEFAULT 'unknown',
  geom                       GEOMETRY(Point, 4326),
  lat_dd                     TEXT GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd                     TEXT GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm                    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm                    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED,
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
  last_known_raise_date      DATE,
  recovered_at               DATE,
  service_interval_years     INT,
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
  on public.instrument using gist (geom);

CREATE TRIGGER instrument_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON instrument
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER instrument_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON instrument
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();
