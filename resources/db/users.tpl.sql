-- APP USERS

CREATE ROLE ops_data_store_app WITH LOGIN PASSWORD '[REDACTED]';
CREATE ROLE ods_app_eo_acq_script WITH LOGIN PASSWORD '[REDACTED]';

GRANT ods_admin TO ops_data_store_app;
GRANT ods_read TO ops_app_eo_acq_script;

-- TEST USERS

CREATE ROLE test_user_ods_admin WITH LOGIN PASSWORD '[REDACTED]';
CREATE ROLE test_user_ods_write_fo WITH LOGIN PASSWORD '[REDACTED]';
CREATE ROLE test_user_ods_write_au WITH LOGIN PASSWORD '[REDACTED]';
CREATE ROLE test_user_ods_read WITH LOGIN PASSWORD '[REDACTED]';

GRANT ods_admin TO test_user_ods_admin;
GRANT ods_write_fo TO test_user_ods_write_fo;
GRANT ods_write_au TO test_user_ods_write_au;
GRANT ods_read TO test_user_ods_read;
