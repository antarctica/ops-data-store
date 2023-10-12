-- DEPOT

create table if not exists public.depot
(
       pk INTEGER GENERATED ALWAYS AS IDENTITY
            CONSTRAINT depot_pk PRIMARY KEY,
      pid UUID NOT NULL DEFAULT generate_ulid(),
       id TEXT NOT NULL,
     geom GEOMETRY(Point, 4326),
     etag TEXT GENERATED ALWAYS AS (md5(id || '__' || st_asewkt(geom, 10))) STORED,
   lat_dd TEXT GENERATED ALWAYS AS (st_y(geom)::text) STORED,
   lon_dd TEXT GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED
);

create index if not exists depot_geom_idx
    on public.depot using gist (geom);

-- INSTRUMENT

create table if not exists public.instrument
(
       pk INTEGER GENERATED ALWAYS AS IDENTITY
            CONSTRAINT instrument_pk PRIMARY KEY,
      pid UUID NOT NULL DEFAULT generate_ulid(),
       id TEXT NOT NULL,
     geom GEOMETRY(Point, 4326),
     etag TEXT GENERATED ALWAYS AS (md5(id || '__' || st_asewkt(geom, 10))) STORED,
   lat_dd TEXT GENERATED ALWAYS AS (st_y(geom)::text) STORED,
   lon_dd TEXT GENERATED ALWAYS AS (st_x(geom)::text) STORED,
  lat_ddm TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).y) STORED,
  lon_ddm TEXT GENERATED ALWAYS AS ((geom_as_ddm(geom)).x) STORED
);

create index if not exists instrument_geom_idx
    on public.instrument using gist (geom);
