-- CIRCUS

INSERT INTO public.circus (pid, id, geom) VALUES ('018b241d-d8a0-9691-698d-dfd1ad57db4a', 'ALPHA', '0101000020E6100000F049670B7E804FC0F983F2C579D850C0');
INSERT INTO public.circus (pid, id, geom) VALUES ('018b241d-d8b0-7046-d8cc-a3c2d91a663d', 'BRAVO', '0101000020E61000000C10507CE23E50C065592F7403B051C0');
INSERT INTO public.circus (pid, id, geom) VALUES ('018b241d-d8b1-1220-d504-0e41f89e3fca', 'CHARLIE', '0101000020E610000047E3951AC0C150C08DF26198458A52C0');
INSERT INTO public.circus (pid, id, geom) VALUES ('018b241d-d8b2-e98b-0ee6-7c306a47746e', 'DELTA', '0101000020E6100000B685DCAFBB7752C06F6E39F206B852C0');

-- WAYPOINT
INSERT INTO waypoint (pid, id, name, colocated_with, last_accessed_at, last_accessed_by, comment, geom) VALUES ('018c36a6-ce23-95f4-e9e8-1d4fb9647e54', 'ALPHA', 'Alpha', 'Foo', '2012-04-24', '~conwat', 'There''s unlimited juice?', '0101000020E61000000000B8C0EFC052C000005217927A51C0');
INSERT INTO waypoint (pid, id, geom) VALUES ('018c36a6-ce3f-ee5f-f027-2436451e1b10', 'BRAVO', '0101000020E61000000000B46B2ECC52C00000687321B551C0');

-- ROUTE_CONTAINER
INSERT INTO route_container (pid, id) VALUES ('018c36a6-ce54-904f-52df-a5b8360e0f95', '01_ALPHA_TO_BRAVO');

-- ROUTE_WAYPOINT
INSERT INTO route_waypoint (route_pid, waypoint_pid, sequence) VALUES ('018c36a6-ce54-904f-52df-a5b8360e0f95', '018c36a6-ce23-95f4-e9e8-1d4fb9647e54', 1);
INSERT INTO route_waypoint (route_pid, waypoint_pid, sequence) VALUES ('018c36a6-ce54-904f-52df-a5b8360e0f95', '018c36a6-ce3f-ee5f-f027-2436451e1b10', 2);
