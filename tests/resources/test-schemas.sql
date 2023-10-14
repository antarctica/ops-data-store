-- CIRCUS

create table if not exists public.circus
(
  pk         INTEGER GENERATED ALWAYS AS IDENTITY
    CONSTRAINT circus_pk PRIMARY KEY,
  pid        UUID                     NOT NULL DEFAULT generate_ulid(),
  id         TEXT                     NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
  updated_by TEXT                     NOT NULL DEFAULT 'unknown',
  etag       TEXT GENERATED ALWAYS AS (md5(id || '__' || st_asewkt(geom, 10))) STORED,
  geom       GEOMETRY(Point, 4326),
  lat_dd     TEXT GENERATED ALWAYS AS (st_y(geom)::text) STORED,
  lon_dd     TEXT GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm    TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED
);

create index if not exists circus_geom_idx
  on public.circus using gist (geom);

create trigger circus_updated_at_trigger
  before update
  on circus
  for each row
execute function set_updated_at();

create trigger circus_updated_by_trigger
  before update
  on circus
  for each row
execute function set_updated_by();
