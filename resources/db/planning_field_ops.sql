-- [Field Ops Planning]
CREATE SCHEMA planning_field_ops;

GRANT USAGE, CREATE ON SCHEMA planning_field_ops TO ods_admin;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA planning_field_ops TO ods_admin;

GRANT USAGE, CREATE ON SCHEMA planning_field_ops TO ods_write_fo;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA planning_field_ops TO ods_write_fo;
