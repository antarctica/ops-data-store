# Operations Data Store

Data store for hosted, and optionally controlled, datasets for BAS Field Operations and Air Unit.

## Overview

### Purpose

This Data Store is a platform provided by the British Antarctic Survey (BAS) Mapping and Geospatial Information Centre
([MAGIC](https://bas.ac.uk/teams/magic)) for hosting vector geospatial data used by BAS Operational Teams.

It consists of datasets used and controlled by the BAS Air Unit and Field Operations teams for planning and delivering
field seasons. Some key datasets are further controlled by MAGIC for enhanced data management and automation.

**Note:** This project is focused on needs within the British Antarctic Survey. It has been open-sourced in case it's
of use to others with similar or related needs. Some resources, indicated with a 🛡 symbol, are not accessible publicly.

### Status

This project is a mature alpha. The aim is to provide a robust, useful, live service within the next few field seasons.

The aim for the 2023-2024 season was to provide an initial minimal implementation to meets core user needs.

Usage and feedback of this minimal implementation is helping guide which improvements and new features are needed for
the 2024-2025 season.

### Limitations

#### Limitations - General

As an alpha project, all, or parts, of this service:

- may, but should not, stop working (due to regressions or instability)
- may not work correctly, or as expectedly (including destructively)
- may change at any time (in terms of implementation or functionality)
- may have missing or outdated documentation

**Note:** Support for this project is provided on a best efforts, 'as is', basis.

**WARNING:** Outputs from this project should not be relied upon for operational use without thorough scrutiny.

#### Limitations - Datasets

In relation to operations that can be performed by end-users vs. platform operators (MAGIC):

- end-users cannot define new [Controlled](#controlled-datasets) datasets/layers themselves
- end-users cannot add, change or remove fields/attributes in Controlled datasets themselves

**Note:** These are intentional limitations to ensure controlled datasets are suitably designed and can be supported.

In all these cases, end-users will need to request changes are made by contacting someone from MAGIC.

#### Limitations - Permissions

In relation to dataset [Permissions](#permissions), support for the following is not yet available:

- running the Azure to LDAP group sync automatically
- removing an Azure group from a role once synced
- users belonging to more than one role/team (i.e. a user cannot be in Air Unit and Field Ops team)
- restricting QGIS layer styles to layers a user is authorised to see
  [#196 🛡️](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/196)
- automatically setting default session roles for new users

#### Limitations - Backups

In relation to dataset and database backups:

- backups are not verified as being accurate or usable
- uncontrolled/planning datasets are not included in backups

### Related projects

This project is limited to the technical and operational aspects of providing a platform for hosting datasets. Other
projects focus on these datasets and other aspects of providing a wider Geographic Information System (GIS) to BAS
Operations.

- [BAS Field Operations Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/operations/field-operations-gis-data)
- [BAS Air Unit Network Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset)
- [BAS Remote Sensing Data 🛡️](https://gitlab.data.bas.ac.uk/MAGIC/remote-sensing)

This project is an evolution of a previous [Experiment 🛡](https://gitlab.data.bas.ac.uk/felnne/ops-data-store-exp).

## Usage

### End-user documentation

End-users should consult the documentation developed for the wider
[Field Operations GIS Platform 🛡](https://app.gitbook.com/o/-MbhSFJ1AEZxhIfX9tgr/s/HmSXoUpviCA3XCta5MDr/), as this
project is not aimed at end-users directly.

### Control CLI

**Note:** This CLI is intended for use by MAGIC team members, not end-users.

A command line interface, `ods-ctl`, is available for performing administrative tasks.

```
$ ods-ctl --help
```

This command will need running from within a deployed instance of this project. See the [Infrastructure](#infrastructure) section
for connection details (specifically the relevant app server).

**Note:** Calling the CLI without any command will not return any output. This is expected.

**Note:** Currently all log entries down to the _info_ level are displayed alongside programme output. This includes a
message from the `shapely` that can be safely ignored:

```
2023-10-23 14:01:29 - shapely.speedups._speedups - INFO - Numpy was not imported, continuing without requires()
```

#### Control CLI `auth` commands

- `ods-ctl auth check`: verifies authentication/authorisation services are available
- `ods-ctl auth sync --azure-group [group-id] --ldap-group [group-id]`: syncs members of Azure groups to an LDAP group
  - the `--azure-group` option can be repeated to merge multiple source groups to a single target group

#### Control CLI `backup` commands

- `ods-ctl backup now`: combines `ods-ctl data backup` and `ods-ctl db backup` as part of a managed, rolling, backup set

#### Control CLI `config` commands

- `ods-ctl config check`: verifies required configuration options have been set
- `ods-ctl config show`: displays the current application configuration

#### Control CLI `data` commands

- `ods-ctl data backup --ouput-path [path/to/file.gpkg]`: saves datasets and styles to GeoPackage backup [1]
- `ods-ctl data convert`: saves controlled routes and waypoints for printing and using in GPS devices

[1] [Controlled Datasets](#controlled-datasets) and [QGIS Layer Styles](#qgis-layer-styles) only.

#### Control CLI `db` commands

- `ods-ctl db check`: verifies the database is available
- `ods-ctl db setup`: configure a new database for use
- `ods-ctl db backup --ouput-path [path/to/file.sql]`: saves database to SQL backup file via `pg_dump` [1]
- `ods-ctl db run --input-path [path/to/file.sql]`: runs SQL commands contained in the input file

[1] [Controlled Datasets](#controlled-datasets) and [QGIS Layer Styles](#qgis-layer-styles) only.

### QGIS project

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

The included QGIS project, developed as part of the wider Field Operations and Air Unit GIS, can be used for testing
editing workflows and verifying expected behaviour.

1. start QGIS LTR with the `ops-data-store` profile selected:
1. open the included QGIS project file [`qgis-project.qgz`](/resources/qgis/qgis-project.qgz)

If needed, shortcuts can be created to start QGIS with a specific profile:

- on macOS: `open -a QGIS-LTR.app --args --profile {profile}`
- on Windows: `C:\Program Files\QGIS 3.28.7\bin\qgis-lts-bin.exe --profile {profile}`

**Note:** To start QGIS normally use the `default` profile.

Tested with QGIS 3.28.11, macOS 12.7, Ops Data Store QGIS profile version
[2023-10-02.0](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/206).

#### Adding DB connection

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

Replace `{placeholder}` values wth settings from the relevant database listed in the [Infrastructure](#infrastructure)
section, except for:

- `{database_role}`, which should be the relevant value from the [Permissions Mapping](#permissions-mappings) section
- `{username}` and `{password}`, which should be the users BAS LDAP credentials

1. open QGIS with the relevant profile active
2. from *Browser* pane -> *PostgreSQL* -> *New Connection*:
   - *(ignore or use default values for options not specified)*
    - Name: `Ops Data Store ({location})`
    - Host: `{host}`
    - Database: `{database}`
    - Session Role: `{database_role}`
    - Authentication -> Configurations -> *Create a new authentication configuration*:
        - *(create or enter master password)*
          - *(if a single user computer (i.e. not shared) users MAY use their NERC or login password for this)*
        - *(ignore or use default values for options not specified)*
        - Name: `BAS LDAP ({location})`
        - Type: *Basic Authentication*
        - Username: `{username}`
          - *(users MUST NOT use their email address - e.g. 'conwat' not 'conwat@bas.ac.uk')*
        - Password: `{password}`
        - *Save*
    * *Test Connection*
    * *OK*

Tested with QGIS 3.28.11, macOS 12.7, Ops Data Store QGIS profile version
[2023-10-02.0](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/206).

#### Adding DB Layer

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

**Note:** These instructions depend on the [Adding DB Connection](#adding-db-connection) workflow.

**Note:** These instructions relate to adding existing layers. See the
[Creating Planning DB Layers](#creating-planning-db-layers) section for adding a new layer.

1. open QGIS with the relevant profile and project active
1. from the *Browser* pane -> *PostgreSQL* -> *Ops Data Store*
    - *(the user may have multiple *Ops Data Store* entries they'll need to pick from based on their current location)*
1. select relevant layer -> *Add Layer to Project*

**Note:** As QGIS exposes database schemas as part of layer hierarchy, users will need to pick from the relevant schema.
For [Controlled Datasets](#controlled-datasets) the schema is: `controlled`.

Tested with QGIS 3.28.11, macOS 12.7, Ops Data Store QGIS profile version
[2023-10-02.0](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/206).

#### Configure layer properties

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

**Note:** These instructions depend on the [Adding DB Layer](#adding-db-layer) workflow.

To configure a layer for the first time:

1. from the *Layers* pane -> (added layer) -> *Properties* -> *Attribute Form*:
    - *pk*, *pid*, *updated_at*, *updated_by*, *lat_dd*, *lon_dd*, *lat_ddm* and *lon_ddm*:
      - *General* -> *Editable*: *Uncheck*
      - *Widget Type*: *Hidden*
1. set other layer properties (aliases, symbology, labelling, etc.) as needed
1. *Style* -> *Save as Default* -> *Datasource Database* -> *Ok*

**Note:** The first layer style saved to the database will automatically create a `public.layer_styles` table.

**Note:** The QGIS [Layer Styles](#qgis-layer-styles) table is stored in the `public` Postgres schema (as it is shared).

Tested with QGIS 3.28.11, macOS 12.7, Ops Data Store QGIS profile version
[2023-10-02.0](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/206).

#### Configure layer snapping

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

**Note:** These instructions depend on the [Configure Layer Properties](#configure-layer-properties) workflow.

To edit features in the *route* layer, snapping needs to be configured for the *waypoint* layer, as route features are
constructed from waypoint features.

1. enable the snapping toolbar
1. click the *Enable Snapping* button from the snapping toolbar
1. click the *Advanced Configuration* button from the snapping toolbar and change from *All Layers* to
   *Advanced Configuration*
1. click the *Edit Advanced Configuration* button from the snapping toolbar and edit the configuration to:
    * set Waypoints as the only available snapping layer
    * set the tolerance to `80000.0` meters (80KM)

Tested with QGIS 3.28.11, macOS 12.7, Ops Data Store QGIS profile version
[2023-10-02.0](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/206).

#### Editing features in DB layer

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

**Note:** These instructions depend on the [Configure Layer Properties](#configure-layer-properties) and
[Configure Layer Snapping](#configure-layer-snapping) workflows

Layers should be editable as normal. The add/edit feature form should already be configured to hide generated or
platform fields and set appropriate aliases.

When editing the *Route* layer, all vertices MUST overlap with existing waypoints. QGIS will allow any coordinate to
be selected, however when saved any vertex that does not overlap will be omitted due to the way
[routes are saved](#qgis-editing-support-for-routes).

#### Creating planning DB layers

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

**Note:** These instructions depend on the [Adding DB Connection](#adding-db-connection) workflow.

New layers can be created in the [Field Ops Planning](#field-operations-planning-datasets) DB schema as normal.

Users SHOULD be advised to:

- use the 'Text, unlimited length (text)' data type for string data (rather than VARCHAR or similar)
- create a default style and save to the data source (database)

### Accessing route and waypoint outputs

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

To access the PDF, CSV, GPX and FPL outputs for waypoints and routes in the BAS Air Unit travel network:

1. visit `https://{placeholder}/content/air-unit-network/` in a web browser
2. download the desired outputs, outputs are organised by format

Replace `{placeholder}` values wth settings from the relevant database listed in the [Infrastructure](#infrastructure)
section.

### Creating backups

Database and dataset [backups](#backups) are created automatically every day. A limited number of backups are kept
before the oldest is replaced. Use the [`config show`](#control-cli-config-commands) application CLI command to show
where backups are stored and how many will be kept.

If needed a manual backup can be created using the [`backup now`](#control-cli-backup-commands) application CLI command.
Manual backups count towards maximum number of backups.

### Identifying latest backups

Within a given platform instance, see the relevant 1Password entry in the [Infrastructure](#infrastructure) section for
where backups are stored.

Within this directory, open the relevant JSON [State file](#backups-state-files) and check the
`meta.newest_iteration_sha1sum` property, e.g. "9e0f11af67e08e9368ff3d94445826fd2014df9b".

Find this checksum in the `iterations` list for details including the date of the backup, and it's location.

### Adding a user to a role

[Permissions](#permissions) are assigned to users through groups they are part of being [mapped](#permissions-mappings)
to a roles (e.g. _viewer_).

To assign a user to a role:

1. ask the relevant Azure group owner to add or remove users as needed [1]
1. run the [`auth sync`](#control-cli-auth-commands) CLI command to update the BAS LDAP server
1. wait for the next [BAS IT User Sync](#bas-it-user-sync)
1. ask IT to run their script to set the default session role for the role to the user

**Note:** Users may only be assigned to a single role.

To revoke a role from a user

1. ask the relevant Azure group owners to remove the user from _all_ groups that map to that role
1. run the [`auth sync`](#control-cli-auth-commands) CLI command to update the BAS LDAP server
1. wait for the next [BAS IT User Sync](#bas-it-user-sync)

[1] If needed, BAS IT can also update team/group memberships in addition to owners.

### Adding a new controlled dataset

This section relates to [Controlled datasets](#controlled-datasets).

1. update [`dataset-schemas.sql`](resources/db/datasets-controlled.sql) using the template [1] with these changes:
   1. replace `NEW_DATASET` with the singular, lower case, name of the new dataset (e.g. 'cave' not 'CAVES')
       - for multi-word names use underscores as a separator (e.g. 'moon_base' not 'moon-base')
   1. if the dataset does not include a [Dataset identifier](#dataset-identifier), remove the `id` column
   1. add dataset specific columns as needed:
       - ensure to use `TEXT` for string fields rather than `VARCHAR`, use constraints to validate lengths
1. update [`grants.tpl.sql`](resources/db/grants.tpl.sql) to grant relevant roles and ad-hoc users write access
1. copy the statements creating the new dataset to a separate update file (e.g. `add_NEW_DATASET.sql`)
1. add [Grants](#database-permissions) to the update file to apply schema wide read access grants to the new table [2]
1. copy the update file to each application instance and apply it using the [`db run`](#control-cli-db-commands) command
1. add the new table as a layer in QGIS and configure as needed (e.g. form fields, aliases, symbology)
1. save the layer properties/style back to the data source and verify entry added to QGIS `public.layer_styles` table

[1]

```sql
-- NEW_DATASET

CREATE TABLE IF NOT EXISTS controlled.NEW_DATASET
(
  pk         INTEGER                  GENERATED ALWAYS AS IDENTITY
    CONSTRAINT NEW_DATASET_pk PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS NEW_DATASET_geom_idx
  ON controlled.NEW_DATASET USING gist (geom);

CREATE OR REPLACE TRIGGER NEW_DATASET_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.NEW_DATASET
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE OR REPLACE TRIGGER NEW_DATASET_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON controlled.NEW_DATASET
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();
```

[2] Copy any statements from the `[CONTROLLED SCHEMA]` section of [`grants.tpl.sql`](resources/db/grants.tpl.sql) which
begin `GRANT SELECT ON ALL ...`.

### Amending an existing controlled dataset [WIP]

This section relates to [Controlled datasets](#controlled-datasets).

**Note:** This section is a work in progress and may be incomplete.

1. update [`schemas.sql`](resources/db/datasets-controlled.sql) making any relevant changes
1. create an update file with the statements to change the relevant entities in place (e.g. [1])
1. copy the update file to each application instance and apply it using the [`db run`](#control-cli-db-commands) command
1. in QGIS, update the properties for the updated layer/table as needed and save to the QGIS `public.layer_styles` table

**Note:** QGIS will create a new entry in the `public.layer_styles` table, with the previous style/entry no longer set
as a default. These previous styles can be removed if needed.

[1] E.g.:

```sql
ALTER TABLE EXISTING_DATASET
ADD COLUMN NEW_COLUMN TEXT;
```

### Removing a controlled dataset [WIP]

This section relates to [Controlled datasets](#controlled-datasets).

**Note:** This section is a work in progress and may be incomplete.

After dropping the relevant table, manually remove any styles for the removed layer in the QGIS
`public.layer_styles` table.

### Adding a new planning dataset

It's intended for end users to create new planning datasets using QGIS as a database client.

See the [Creating Planning DB Layers (in QGIS)](#creating-planning-db-layers) section for more information.

## Implementation

### Architecture

![architecture diagram](docs/img/architecture.png)

### Command line interface

[Typer](https://typer.tiangolo.com) is used as the framework for the control CLI.

### Configuration

The [control CLI](#command-line-interface) uses a series of settings for connecting to external services and reporting internal information.
Some settings are read-only, such as the application version, others are write-only, such as database connection
details, and must be defined by the user, using either appropriate environment variables, or an `.env` file.

**Note:** If using an `.env` file, an example [`.example.env`](.example.env) is available as a guide.

| Config Property                     | Environment Variable               | Required | Sensitive | Read Only | Type            | Description                                                      | Example                                                                  |
|-------------------------------------|------------------------------------|----------|-----------|-----------|-----------------|------------------------------------------------------------------|--------------------------------------------------------------------------|
| `AUTH_AZURE_AUTHORITY`              | `APP_ODS_AUTH_AZURE_AUTHORITY`     | No [2]   | No        | No        | String          | Endpoint used for authenticating against Azure                   | 'https://login.microsoftonline.com/b311db95-32ad-438f-a101-7ba061712a4e' |
| `AUTH_AZURE_CLIENT_ID`              | `APP_ODS_AUTH_AZURE_CLIENT_ID`     | No [2]   | No        | No        | String          | Identifier used for authenticating against Azure                 | '3b2c5acf-728a-4b78-85f0-9560a6aad701'                                   |
| `AUTH_AZURE_CLIENT_SECRET`          | `APP_ODS_AUTH_AZURE_CLIENT_SECRET` | No [2]   | Yes       | No        | String          | Secret used for authenticating against Azure                     | 'xxx'                                                                    |
| `AUTH_AZURE_SCOPES`                 | -                                  | No [2]   | No        | Yes       | List of Strings | Permissions requested when authenticating against Azure          | ['https://graph.microsoft.com/.default']                                 |
| `AUTH_LDAP_BASE_DN`                 | `APP_ODS_AUTH_LDAP_BASE_DN`        | No [2]   | No        | No        | String          | Base scope to apply to all LDAP queries                          | 'dc=example,dc=com'                                                      |
| `AUTH_LDAP_BIND_DN`                 | `APP_ODS_AUTH_LDAP_BIND_DN`        | No [2]   | No        | No        | String          | Identifier used for authenticating against LDAP server           | 'cn=app,ou=apps,dc=example,dc=com' [3]                                   |
| `AUTH_LDAP_BIND_PASSWORD`           | `APP_ODS_AUTH_LDAP_BIND_PASSWORD`  | No [2]   | Yes       | No        | String          | Secret used for authenticating against LDAP server               | 'xxx'                                                                    |
| `AUTH_LDAP_CXT_GROUPS`              | `APP_ODS_AUTH_LDAP_CXT_GROUPS`     | No [2]   | No        | No        | String          | LDAP naming context prefix used to identify groups               | 'cn' [3]                                                                 |
| `AUTH_LDAP_CXT_USERS`               | `APP_ODS_AUTH_LDAP_CXT_USERS`      | No [2]   | No        | No        | String          | LDAP naming context prefix used to identify users                | 'cn' [3]                                                                 |
| `AUTH_LDAP_OU_GROUPS`               | `APP_ODS_AUTH_LDAP_OU_GROUPS`      | No [2]   | No        | No        | String          | Scope for group related objects in LDAP server                   | 'groups'                                                                 |
| `AUTH_LDAP_OU_USERS`                | `APP_ODS_AUTH_LDAP_OU_USERS`       | No [2]   | No        | No        | String          | Scope for user related objects in LDAP server                    | 'users'                                                                  |
| `AUTH_LDAP_URL`                     | `APP_ODS_AUTH_LDAP_URL`            | No [2]   | No        | No        | String          | Endpoint used for authenticating against LDAP server             | 'ldap://ldap.example.com:389'                                            |
| `AUTH_MS_GRAPH_ENDPOINT`            | -                                  | No [2]   | No        | Yes       | String          | Endpoint used for the Microsoft Graph API                        | 'https://graph.microsoft.com/v1.0'                                       |
| `BACKUPS_COUNT`                     | `APP_ODS_BACKUPS_COUNT`            | Yes      | No        | No        | Number          | Number of backups to keep as part of a rolling window            | '10'                                                                     |
| `BACKUPS_PATH`                      | `APP_ODS_BACKUPS_PATH`             | Yes      | No        | No        | String (Path)   | Location to store application backups [4]                        | '/var/opt/ops-data-store/backups/'                                       |
| `DATA_AIRNET_OUTPUT_PATH`           | `APP_ODS_DATA_AIRNET_OUTPUT_PATH`  | Yes      | No        | No        | String (Path)   | Location to store Air Unit Network exports [4]                   | `/var/www/ops-data-store/air-unit-outputs/`                              |
| `DATA_AIRNET_ROUTES_TABLE`          | -                                  | No       | No        | Yes       | String          | Name of database table used for Air Unit Network routes          | 'route_container'                                                        |
| `DATA_AIRNET_ROUTE_WAYPOINTS_TABLE` | -                                  | No       | No        | Yes       | String          | Name of database table used for Air Unit Network route waypoints | 'route_waypoint'                                                         |
| `DATA_AIRNET_WAYPOINTS_TABLE`       | -                                  | No       | No        | Yes       | String          | Name of database table used for Air Unit Network waypoints       | 'waypoint'                                                               |
| `DATA_MANAGED_SCHEMA_NAME`          | -                                  | No       | No        | Yes       | String          | Name of the database schema containing controlled datasets       | 'controlled'                                                             |
| `DATA_MANAGED_TABLE_NAMES`          | `APP_ODS_DATA_MANAGED_TABLE_NAMES` | Yes      | No        | No        | List of Strings | Names of database tables used for controlled datasets            | ['depot', 'instrument']                                                  |
| `DATA_QGIS_TABLE_NAMES`             | -                                  | No       | No        | Yes       | List of Strings | Names of database tables optionally used by QGIS                 | ['layer_styles']                                                         |
| `DB_DSN`                            | `APP_ODS_DB_DSN`                   | Yes      | Yes       | No        | String          | Application database connection string [1]                       | 'postgresql://user:pass@host/db'                                         |
| `VERSION`                           | -                                  | No       | No        | Yes       | String          | Application version, read from package metadata                  | '0.1.0'                                                                  |

[1] The `DB_DSN` config option MUST be a valid [psycopg](https://www.psycopg.org) connection string.

[2] `AUTH_*` config options are required if managing authentication/authorisation aspects of the Data Store.

[3] Make sure to use the correct naming context prefix for the LDAP server, e.g. `cn=conwat` vs. `uid=conwat`.

[4] These options MUST point to an existing directory that is writable by the application user.

### BAS Air Unit Network Utility

The [BAS Air Unit Network Dataset utility 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset) is used to
convert the *Waypoint* and *Route* [Controlled Datasets](#controlled-datasets) maintained by the BAS Air Unit into
formats for use in GPS devices and other activities such as printing.

These datasets can be converted using the [`data convert`](#control-cli-data-commands) CLI command. Outputs are written
to the [File Store](#file-store) and available to end-users through the [Web Server](#web-server).

#### Automatic conversion

To avoid the need for end-users to use the [CLI](#command-line-interface) to generate outputs, the
[`data convert`](#control-cli-data-commands) CLI command can be run automatically using cron or other task scheduling
tool.

For example to run with cron every 5 minutes:

```
*/5 * * * * /path/to/ods-ctl data convert >> /path/to/logs/$(date +\%Y-\%m-\%d-\%H-\%M-\%S-\%Z).log 2>&1
```

This will create per-run log files (e.g. `/path/to/logs/2023-11-20-04:00:00-UTC.log`). See the
[Installation](#installation) section for how to configure automated conversions in a deployed instance.

Log files for automatic conversions are retained for 24 hours and then deleted via a crontab entry.

### Database

[PostgreSQL](https://www.postgresql.org) is used for storing datasets. It uses the [PostGIS](https://postgis.net)
extension for storing spatial information along with custom functions and data types for:

- creating [ULIDs](https://github.com/ulid/spec) (stored as a UUID data-type)
  - using the `generate_ulid` custom function
  - which relies on the [pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html) extension
- formatting latitude and longitude values in the Degrees, Decimal Minutes format (DDM)
  - using the `geom_as_ddm` custom function and `ddm_point` custom data type
- recording when and by who rows in controlled datasets are changed
  - using the `set_updated_at` and `set_updated_by` custom functions

#### Database schemas

All extensions, extension support views, custom functions/types and other shared objects are stored in the default
`public` schema.

[Datasets](#datasets) are stored in schemas based on how they are controlled. See the [Datasets](#datasets) section for
more information.

#### Database permissions

Database permissions form part of the Data Store's [Permissions](#permissions) system - specifically to control who
can access underlying data. Database roles, users and grants need to be created/set to implemented to the relevant
parts of this permissions system.

Required Postgres roles are defined in the [Permission Mappings](#permissions-mappings) section. Reference SQL
statements to create these roles are defined in the [`roles.sql`](resources/db/roles.sql) file.

Required Postgres users are defined by a combination of:

- the members of the relevant groups listed in the [Permission Mappings](#permissions-mappings) section
- users to represent applications (see the [Project Setup](#project-setup) section for specific users required)
- a set of example users for each role to test/debug with (strongly recommended)

Reference SQL statements to create these users are defined in the
[`users.tpl.sql`](resources/db/users.tpl.sql) file.

**Note:** This reference is a template. Values that need substituting with specific values based on how the database
has been implemented are indicated with `{{ default/conventional/example value }}`.

**Note:** For BAS IT managed databases, the [BAS IT User Sync](#bas-it-user-sync) will create required database users, including
application users. A set of example users, based on the reference example users, should also be created and assigned
the relevant roles by IT manually. See the relevant [Infrastructure](#databases) subsection for their credentials.

Postgres grants are required to implement the rights described in the [Permission Mappings](#permissions-mappings)
section. Reference SQL statements for these grants are defined in the [`grants.tpl.sql`](resources/db/grants.tpl.sql)
file.

**Note:** This reference is a template. Values that need substituting with specific values based on how the database
has been implemented are indicated with `{{ default/conventional/example value }}`.

### File store

The file store holds application [Backups](#backups) and [Converted Outputs](#bas-air-unit-network-utility). It is
typically a file system, either using local disks or remote file shares. Other technologies, such as objects stores,
cannot currently be used but could be supported if needed.

The file store may also be used for hosting the [CLI](#command-line-interface) and/or [Database](#database), however
this is not required, and not common particularly for the database.

The file system enforces permissions via owner/group and ACL mechanisms (as used by the [Web Server](#web-server))
component.

Each operating [Environment](#infrastructure) uses a separate file store. I.e. there is no single common/global
instance, despite being available from the same mount point in all environments (for consistency).

### QGIS

[QGIS](https://qgis.org) is the QGIS client end-users will use for editing and visualising geospatial data, and acts as
the database client in relation to this project specifically.

For consistency/compatibility, the QGIS profile and project developed for the wider GIS are used for consistency and
compatibility.

#### QGIS layer styles

It is recommended that QGIS layer styles are stored in the platform [Database](#database) such that they are centrally
maintained. The `layer_styles` table QGIS creates should be held in the `public` schema, as it is a shared resource
and not relevant to how datasets are organised.

**Note:** Layer styles are accessible to all authenticated users and so the names and attributes of the table/view/layer
each style belongs to, can be found through this table, even if the related layer is otherwise restricted. This is an
information leak and should be considered when naming layers and their attributes if the names themselves are sensitive.

#### QGIS layer SVGs

SVGs used as part of layer symbologies are stored in `./content/qgis/symbology/svgs/` within the
[File Store](#file-store) and available through the [Web Server](#web-server) for referencing in styles.

### Microsoft Entra

[Microsoft Entra](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id)
(Azure Active Directory) is the Identity Provider (IDP) used by NERC, within which BAS sits. An application
registration represents this project within Azure, granting it permission to relevant resources within the
[Microsoft Graph API](#microsoft-graph).

#### App registration secrets

A client secret (and non-secret client ID) is used for this project to identify its application registration. Separate
secrets used for each instance and need to be rotated every 6 months (180 days).

#### App registration secret rotation

Currently, app registration secrets are rotated manually:

- from the [Application Registration](#azure-app-registrations) in the Azure Portal:
  - from the *Certificates & secrets* section, remove the existing secret
  - from the same section, create a new client secret with the same description and 180 day expiry date
- update the `APP_ODS_AUTH_AZURE_CLIENT_SECRET` environment variable (via a `.env` file or through some other method)
  in the relevant instance

### Microsoft Graph

The [Microsoft Graph API](https://learn.microsoft.com/en-us/graph/) provides programmatic access to Microsoft 365
resources. For this project, the members of specified [Microsoft Teams](#microsoft-teams).

### Microsoft Teams

[Microsoft Teams](https://www.microsoft.com/en-gb/microsoft-teams/group-chat-software) is a collaboration tool within
the Microsoft 365 platform used by a number of BAS departments and projects. Teams use Azure groups to record their
members, which this project can access via the [Microsoft Graph](#microsoft-graph) API as the basis for the Data
Store's [Permissions](#permissions) system.

### LDAP

LDAP is the Identity Provider (IDP) used by BAS IT, specifically for unix systems including [Postgres](#database) and
[Apache](#web-server). It is used for both authentication and authorisation through a number of application controlled
groups. Group members are synced from Azure groups representing [Microsoft Teams](#microsoft-teams) as part of the Data
Store's [Permissions](#permissions) system.

### Web server

[Apache HTTP Server](https://httpd.apache.org) is used for hosting content from the [File Store](#file-store), making it
available to end users. It is managed by BAS IT and uses a [virtual host](https://httpd.apache.org/docs/2.4/vhosts/) configured in
`/etc/httpd/sites/10-ops-data-store.conf`. Automatic directory listings are disabled for this site.

The web server includes:

- outputs for converted [Routes and Waypoints datasets](#bas-air-unit-network-utility), restricted using [LDAP](#ldap)
  - users must have a valid LDAP account and be a member of the *Viewer* role from the [Permissions](#permissions) system
  - automatic directory listings are enabled for this content
- [QGIS Layer SVGs](#qgis-layer-svgs)
  - files are accessible anonymously so they can be used in QGIS layer styles

#### Web server permissions

Where restricted content needs to be shared through the web server, special file permissions are needed for the web
server to access content whilst preventing users accessing files directly through the file system, which would bypass
restrictions enforced by the web server.

Conventional file permissions are set for a parent directory preventing world/other read (and execute for directories)
An additional NFS ACL is set granting these removed permissions to the web server user only.

To read a file from the file system, read access is required on the file itself and all parent directories up to and
including root (`/`). The restrictive file permissions on the parent folder therefore prevent users accessing
restricted content via the file system, even if they know the path to a file or directory.

**Note:** Files or directories within this parent directory require world/other read (and execute for directories)
permissions for the web server to access them. I.e. only the parent directory should use restricted permissions.

These permissions and ACLs are set automatically in BAS IT managed instances.

### BAS IT User sync

As part of the Data Store's [Permissions](#permissions) system, a mechanism has been implemented by BAS IT to:

- replicate relevant objects between [LDAP](#ldap) servers
- create, update or remove [Database](#database) users and their permissions based on LDAP objects

This mechanism is only accessible to BAS IT and any issues will need resolving via the BAS IT Service Desk. IT have
access to a log file which records the results of recent syncs.

**Note:** Inconsistencies can occur after a sync, however these should normally resolve themselves in the next sync.

For reference, this mechanism runs on a daily schedule at:

- 09:00 & 09:15 UTC (06:00 & 06:15 Rothera)
- 15:00 & 15:15 UTC (12:00 & 12:15 Rothera)
- 21:00 & 21:15 UTC (18:00 18:15 Rothera)

(Where the first time is the LDAP to LDAP sync and the second LDAP to Postgres. Rothera is UTC -03:00).

For replicating LDAP objects between servers:

- the *Cambridge (Production)* LDAP server is considered the source of truth
- application LDAP groups, and users these groups contain as members, are replicated to LDAP servers in other environments
- credentials for users are replicated, ensuring users can use the same credentials in all environments
- user credentials will be updated in other environments if changed in the source LDAP server at the next sync execution
- users that are no longer members of groups will be reflected in other environments at the next sync execution

For managing database users based on LDAP objects:

- base Postgres roles are created for each application role/group, granted relevant access to database objects
- for each application LDAP group, each member is created as a Postgres user role, named after the LDAP UID attribute
- these Postgres user roles are configured to inherit the relevant base Postgres role, granting them relevant permissions
- user credentials are not replicated to these user roles as Postgres is configured to use LDAP authentication
- user roles for users removed from an LDAP group will no longer inherit from the relevant base role, revoking permissions
- user roles may inherit from multiple base Postgres roles if members of multiple application LDAP groups

### MAGIC EO Acquisitions script

To provide Field Operations with satellite imagery for areas they are interested in, MAGIC routinely searches for and
downloads imagery for a given series of Areas of Interest (AOIs) using a script. This data is then synced to a nominated
location where Field Operations can access it.

Whilst affiliated with this project (and set up under it), this script/functionality is not formally part of
the Data Store but is facilitated by it.

See the [MAGIC Remote Sensing](https://gitlab.data.bas.ac.uk/MAGIC/remote-sensing) project for more information.

To facilitate this script, this project provides:

- a [controlled](#controlled-datasets) dataset for AOIs (`controlled.eo_acq_aoi`)
- a database user with read access to this dataset (`ods_app_eo_acq_script`)

See the [Database Permissions](#database-permissions) section how this user is managed and assigned permissions.

See [MAGIC/ops-data-store#198 🛡️](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/198) for how this was
set up.

### Permissions

Datasets hosted in this platform are restricted as to who can read and/or edit from them. The platform includes a
simple permissions system to enforce these restrictions.

**Note:** This permissions system does not apply to [QGIS Layer Styles](#qgis-layer-styles).

- for users representing end-users (individuals), a role based permissions system is used
- for users representing applications, ad-hoc permissions are used

#### Permissions - grants

Permissions for users and roles to access/modify entities that are known to exist are implemented using
[Postgres permissions](#database-permissions). This includes ad-hoc permissions needed for users representing
applications.

#### Permissions - grants (dynamic entities)

For entities created dynamically by end-users (such as for [Planning Datasets](#field-operations-planning-datasets)),
it isn't possible to pre-define permissions, or tenable to expect end-users apply database grants after creating new
entities. Without this however other users won't be able to access them.

I.e.:

- a user Alice creates a new table 'foo'
- another user Bob is unable to access it because Alice hasn't granted Bob access to it

To work around this, end-users assume a common role using `SET ROLE` (set in the QGIS database connection for example).
This means entities are created (and otherwise interacted with) as the same user, and so does not require any grants to
be applied.

I.e.:

- a user Alice, acting as a common role `field_team`, creates a new table 'foo'
- another user Bob, also acting as the `field_team` common role, is able to access it because they are the same user

**Note:** Users must be assigned to inherit from any role they wish to act as, and must still login as themselves
before acting as a common role, preventing users bypassing access restrictions.

**Note:** Due to a [bug](https://github.com/qgis/QGIS/issues/57761) in QGIS, the Session Role setting is not respected.
As a workaround, IT can set a default DB role for users.

**Note:** A side effect of this `SET ROLE` approach means that role inheritance is disabled, meaning permissions must
be granted directly to each role.

#### Permissions - roles

This system includes three roles which can be assigned to individual users:

- *admin*: can view and change any information to manage and administer the platform (inc. members of MAGIC and BAS IT)
- *owner*: can change and view information
- *viewer*: can read information only

**Note:** Users can be assigned to multiple roles but may only assume one role at a time within a session.

I.e. If a user is assigned the *owner* and *viewer* roles they may act as either the *owner* or *viewer* role, not both.

**Note:** Users representing applications are assigned permissions directly, rather than via one of these roles.

The *admin* and *viewer* roles are global (applies to all datasets). The *owner* role is scoped to a particular team.
with team members only able to change datasets within their team (i.e. that their team owns). These teams are:

- BAS Field Operations
- BAS Air Unit

**Note:** All roles (including teams) are granted read only access to all [Controlled Datasets](#controlled-datasets).

E.g. For a dataset of field instruments owned by the BAS Field Operations team:

- BAS Field Operations team members can change this dataset, as their team owns the dataset
- BAS Air Unit team members cannot change this dataset, as though they hold the *owner* role, they are a different team
- BAS Air Unit team members will be granted access to view the dataset
- *admin* role holders can change this dataset, as they can change all information in the platform
- *viewer* role holders can view but cannot change this dataset, as they can only view all information in the platform

These roles are implemented in the [Database](#database) using roles and users:

- roles are represented as postgres roles, which are granted permissions (using Postgres grants) to read or change
  information in all or specific tables
- individuals are represented as postgres users, which are assigned to (inherit from) a single role

#### Permissions - role assignments

Users are assigned roles based on the membership of groups held in an [LDAP server](#ldap). I.e. members of LDAP group
'x' are assigned to Postgres role 'x'. LDAP group members are copied from a series of [Azure](#microsoft-entra) groups
representing Microsoft Teams. These Teams are used by departments outside of this platform and project. The intention
is to prevent departments needing to maintain a duplicate membership list, which may get out of sync.

Membership information moves in one direction: from Azure (MS Teams) to LDAP, then to Postgres. Each LDAP group can
include multiple Azure groups forming a union of members.

Users must exist in the LDAP server before they can be added to LDAP groups. Missing users will first need registering,
at BAS by contacting the IT Service Desk.

#### Permissions - mappings

Mappings for roles, teams, the database and LDAP:

| Role    | Team                 | Azure Groups                                                                                                                                                             | LDAP Group                   | Postgres Role     |
|---------|----------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------|-------------------|
| Admins  | -                    | [`34db44b7-4441-4f60-8daa-d0c192d74704`](https://portal.azure.com/#view/Microsoft_AAD_IAM/GroupDetailsMenuBlade/~/Overview/groupId/34db44b7-4441-4f60-8daa-d0c192d74704) | `apps_magic_ods_write_admin` | `ods_write_admin` |
| Owners  | BAS Field Operations | [`75ec55c1-7e92-45e3-9746-e50bd71fcfef`](https://portal.azure.com/#view/Microsoft_AAD_IAM/GroupDetailsMenuBlade/~/Overview/groupId/75ec55c1-7e92-45e3-9746-e50bd71fcfef) | `apps_magic_ods_write_fo`    | `ods_write_fo`    |
| Owners  | BAS Air Unit         | [`7b8458b9-dc90-445b-bff8-2442f77d58a9`](https://portal.azure.com/#view/Microsoft_AAD_IAM/GroupDetailsMenuBlade/~/Overview/groupId/7b8458b9-dc90-445b-bff8-2442f77d58a9) | `apps_magic_ods_write_au`    | `ods_write_au`    |
| Viewers | -                    | [1]                                                                                                                                                                      | `apps_magic_ods_read`        | `ods_read`        |

The [BAS IT User Sync](#bas-it-user-sync) and the [Command Line Interface](#command-line-interface), specifically
commands in the [`auth`](#control-cli-auth-commands) command group are used for synchronising users, and verifying
users have been synced, between these systems and between environments.

[1]

Union of:

- [`34db44b7-4441-4f60-8daa-d0c192d74704`](https://portal.azure.com/#view/Microsoft_AAD_IAM/GroupDetailsMenuBlade/~/Overview/groupId/34db44b7-4441-4f60-8daa-d0c192d74704)
- [`75ec55c1-7e92-45e3-9746-e50bd71fcfef`](https://portal.azure.com/#view/Microsoft_AAD_IAM/GroupDetailsMenuBlade/~/Overview/groupId/75ec55c1-7e92-45e3-9746-e50bd71fcfef)
- [`7b8458b9-dc90-445b-bff8-2442f77d58a9`](https://portal.azure.com/#view/Microsoft_AAD_IAM/GroupDetailsMenuBlade/~/Overview/groupId/7b8458b9-dc90-445b-bff8-2442f77d58a9)

### Backups

[Controlled Datasets](#controlled-datasets) hosted in this platform, their [QGIS Layer Styles](#qgis-layer-styles)
and the underlying [Database](#database) can be exported as file based backups, to allow undesired data changes to be
recovered (i.e. where a feature is accidentally deleted).

A fixed number of backups are kept, with the oldest backup replaced by the newest when a configured limit is reached.
This forms a backup window within which backups can be accessed. The length of this window depends on the number of
backups to keep and how often they are made (i.e. a limit of 7 with daily backups gives a window of a week).

**Note:** Backups are intended as point-in-time snapshots of data, rather than long-term, data archives (which will
likely require manual preparation).

**Note:** Backups only include controlled datasets. Additional 'uncontrolled' datasets, or any other database objects,
are ignored.

Currently, two separate backups are created:

1. [GeoPackages](#geopackage-backups)
2. [PostgreSQL database dumps](#postgresql-backups)

Backups are independent of each other, i.e. if the backup limit is 6, a maximum of 6 GeoPackage, and 6 Postgres,
backups will be retained - rather than 3 of each. Backups are captured together to try and ensure consistency.

The [Command Line Interface](#command-line-interface), specifically commands in the
[`backup`](#control-cli-backup-commands) command group can be used to create and manage backups.

#### GeoPackage backups

GeoPackage backups:

* use a [standardised](https://www.geopackage.org), interoperable, file format for geospatial information
* can be used directly with GIS clients or other tools such as GDAL/OGR
* contain [Controlled Datasets](#controlled-datasets) and QGIS layer style information only

**WARNING!** GeoPackage backups are not tested/verified.

Troubleshooting steps:

- [GeoPackage backups GDAL error](#geopackage-backups-gdal-error)

#### PostgreSQL backups

Database backups:

* use a technology specific file format for database information (postgres dump)
* requires loading into a compatible Postgres database to use
* contains all database objects (data types, tables, views, functions, triggers) from the MAGIC Managed Datasets schema
  and select objects from the `public` schema only
* do not contain global objects (users, roles and grants - see [Permissions](#permissions) section)

Database backups are intended to give additional confidence whilst this project is initially setup system. They MUST
NOT be replied upon for ensuring information not included in the [GeoPackage Backups](#geopackage-backups), such as
uncontrolled datasets, are backed up.

**WARNING!** Database backups are not tested/verified.

**WARNING!** Database backups will be withdrawn in time.

#### Infrastructure backups

For BAS IT managed infrastructure, additional backups are maintained by BAS IT:

- Virtual Machines are backed up incrementally daily and fully every week for 1 month and then a monthly backup for 6
  months

#### Backups state files

To avoid issues with file systems that capture all files within their own managed backups (such as the BAS SAN),
backups are named using generic names that are rotated. In order to tell specific backups apart a backup state file is
maintained automatically alongside each backup.

This state file is encoded as JSON using the `.state.json` extension and designed to be human-readable. State files
contain two sections, a `meta` section and a list of iterations. Iterations are identified using the SHA1 checksum of
the file contents - as the filename will be made generic and change over time.

Example state file for a three file backup set:

```json
{
  "meta": {
    "max_iterations": 3,
    "iterations": 3,
    "newest_iteration_sha1sum": "1f3c3cd6977c3253d6cf0a4219dbb74a791fdccb",
    "schema_version": "1",
    "updated_at": "2023-11-09T11:44:05.188558+00:00"
  },
  "iterations": {
    "5a88d442089f97497fa3e2cc25827073c2d4c518": {
      "sha1sum": "5a88d442089f97497fa3e2cc25827073c2d4c518",
      "replaces_sha1sum": "",
      "created_at": "2023-11-09T11:39:49.535065+00:00",
      "original_name": "db_backup.sql",
      "sequence": 1,
      "path": "backups/db_backup_1.sql"
    },
    "cf7650f9cafda9aee8815161b9e088d820f32f4a": {
      "sha1sum": "cf7650f9cafda9aee8815161b9e088d820f32f4a",
      "replaces_sha1sum": "5a88d442089f97497fa3e2cc25827073c2d4c518",
      "created_at": "2023-11-09T11:43:08.484397+00:00",
      "original_name": "db_backup.sql",
      "sequence": 2,
      "path": "backups/db_backup_2.sql"
    },
    "1f3c3cd6977c3253d6cf0a4219dbb74a791fdccb": {
      "sha1sum": "1f3c3cd6977c3253d6cf0a4219dbb74a791fdccb",
      "replaces_sha1sum": "cf7650f9cafda9aee8815161b9e088d820f32f4a",
      "created_at": "2023-11-09T11:44:05.183804+00:00",
      "original_name": "db_backup.sql",
      "sequence": 3,
      "path": "backups/db_backup_3.sql"
    }
  }
}
```

The oldest backup is identified by the lowest `sequence` value (i.e. `0`) and does not have a `replaces_sha1sum` value
as it logically doesn't replace a previous backup. For other backups, the `replaces_sha1sum` value can be used to
calculate the order of backups if the sequence information is lost. The order backups appear in the `iterations` list
MUST NOT be used to infer the order of backups.

The `created_at` and `original_name` properties relate to the file added to the backup set (which may be named
generically) or include a timestamp or other unique value. These values, along with the `sha1sum` will therefore not
change.

**Note:** The backup system implemented within this application does not include measures to protect against file
corruption. Separate processes will be needed to achieve this if needed.

#### Backups automation

Backups can be captured automatically using cron or other task scheduling tool by calling the
[`backup now`](#control-cli-backup-commands) CLI command.

For example to run with cron every day at 04:00 (AM):

```
0 4 * * * /path/to/ods-ctl backup now >> /path/to/logs/$(date +\%Y-\%m-\%d-\%H-\%M-\%S-\%Z).log 2>&1
```

This will create per-run log files (e.g. `/path/to/logs/2023-11-20-04:00:00-UTC.log`). See the
[Installation](#installation) section for how to configure automated backups in a deployed instance.

Log files for automatic backups are retained for 30 days and then deleted via a crontab entry.

### Monitoring

#### Sentry cron monitoring

The Sentry error tracking platform is used to monitor [scheduled tasks](https://docs.sentry.io/product/crons/) such
as [Backups](#backups-automation) using the [Sentry CLI](https://docs.sentry.io/product/crons/getting-started/cli/).

## Datasets

Datasets hosted in this platform can be classed as either:

- *controlled*: datasets whose schemas are formally controlled by data owners (Ops) and platform operators (MAGIC) and
  typically represent fundamental, enduring, entities such as routes, depots, AOIs, etc.
- *planning*: other datasets Ops users may wish to store, with a wide range of maturity - essentially ignored by this
  platform

### Controlled datasets

Controlled datasets are formally reviewed to ensure a suitable schema is used. All such datasets provide minimally
agreed functionality, using the same base table structure, with additional fields and functionality extending from this.

Controlled datasets are stored in the `controlled` database schema. Definitions for these datasets are declared in
[`dataset-schemas.sql`](resources/db/datasets-controlled.sql).

This base table schema comprises:

- a set of [Identifier](#controlled-datasets-identifiers) fields
- a pair of [Last Update](#controlled-datasets-last-update-fields) fields
- a set of [Geospatial](#controlled-datasets-geometry-fields) fields

Additional fields originate from one of these other projects:

- BAS [Field Operations GIS Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/operations/field-operations-gis-data)
- BAS [Air Unit Network Dataset 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset)

### Controlled datasets owners

Controlled datasets are assigned to these teams in relation to the [Permissions](#permissions) needed to change the
data they contain:

| Dataset Name        | Database Entity Name                         | Owner (Team)         |
|---------------------|----------------------------------------------|----------------------|
| Depots              | `depot`                                      | BAS Field Operations |
| Instruments         | `instrument`                                 | BAS Field Operations |
| Waypoints           | `waypoint`                                   | BAS Air Unit         |
| Routes              | `route_container`, `route_waypoint`, `route` | BAS Air Unit         |
| EO Acquisition AOIs | `eo_acq_aoi`                                 | MAGIC                |

I.e. the Depots dataset can only be changed by the BAS Field Operations team.

### Controlled datasets identifiers

All controlled datasets have at least two identifiers, though most will have three as defined below:

| Domain     | Owner    | Audience  | Column Name | Data Type | Format/Scheme                        | Required | Unique   |
|------------|----------|-----------|-------------|-----------|--------------------------------------|----------|----------|
| Technology | MAGIC/IT | MAGIC/IT  | `pk`        | Integer   | PostgreSQL Identity                  | Yes      | Yes      |
| Platform   | MAGIC    | MAGIC/Ops | `pid`       | UUID      | [ULID](https://github.com/ulid/spec) | Yes      | Yes      |
| Dataset    | Ops      | MAGIC/Ops | `id`        | String    | -                                    | No       | Optional |

For example:

| PK  | PID                           | ID      | ... |
|-----|-------------------------------|---------|-----|
| `1` | `01H26N7D9Q064B6QQMCPP5NQK0 ` | `ALPHA` | ... |
| ... | ...                           | ...     | ... |
| `9` | `01H26N7D9SGG348R24KN6W50GX ` | `INDIA` | ... |
| ... | ...                           | ...     | ... |

#### Technology identifier

This ID is dictated by whichever technology used to implement this platform. For Postgres, this is a primary key using
an [Integer identity](https://www.depesz.com/2017/04/10/waiting-for-postgresql-10-identity-columns/) column, as they
are the easiest to manage.

**WARNING!** This column MUST NOT be relied upon outside each individual database instance, as it MAY NOT be the same
between instances. If we use a different technology in the future, this MAY use a different concept, necessitating the
loss of any existing values.

**Note:** This attribute SHOULD NOT be exposed to end-users, either by using database views, or configuring fields in
layers, to hide the column.

#### Platform identifier

This ID is dictated by us to uniquely and persistently identify features across all datasets hosted in the platform
and ideally across datasets anywhere (i.e. globally unique). The [ULID](https://github.com/ulid/spec) scheme is used to
implement these identifiers as they're reasonably compact and naturally sort by time.

Once issued they do not change and SHOULD be used to distinguish features and/or for defining feature relations.
Crucially this value has no meaning (to us or end-users) and is therefore neutral. This identifier MAY be exposed to
end-users, though it is assumed they won't use or recognise them directly.

**Note:** `PID` was chosen to avoid using `FID`, as this is typically used, and possibly reserved, in GIS systems.

**Note:** ULIDs are stored in a Postgres UUID data type to improve indexing. This results in a non-standard
representation which can appear misleading.

#### Dataset identifier

This ID is not required, though it's assumed almost all datasets will have a value that users use to identify features,
even if only for a time limited period. Values are uncontrolled in terms of needing to be:

- unique
- applied consistently
- following a scheme or convention
- meaningful and/or recognisable by end-users
- persistent over time

**Note:** These properties are nevertheless recommended in any identifier.

### Controlled datasets last update fields

All controlled datasets have two last update columns:

- `updated_at`: timestamp of when a row was last changed
- `updated_by`: identity of who last changed a row

Both fields are updated whenever data in a row changes via a Postgres trigger on each table, which use the `NOW()` or
`session_user` function/variable respectively.

The value of the 'Updated By' column should correspond to an end-user, specifically a NERC username, which can be
optionally resolved to a name or other label. E.g. `conwat` can become *Connie Watson*.

**Note:** `session_user` is used due rather than `current_user` due to the way [Permissions grants](#permissions-grants)
are implemented.

For example:

| PK  | PID                           | Updated At                          | Updated By | ... |
|-----|-------------------------------|-------------------------------------|------------|-----|
| `1` | `01H26N7D9Q064B6QQMCPP5NQK0 ` | `2023-08-24 15:23:01.583312 +00:00` | `conwat`   | ... |
| ... | ...                           | ...                                 | ...        | ... |
| `9` | `01H26N7D9SGG348R24KN6W50GX ` | `2023-10-14 09:46:23.237912 +00:00` | `conwat`   | ... |
| ... | ...                           | ...                                 | ...        | ... |

### Controlled datasets geometry fields

All controlled datasets which implement the base schema have a PostGIS EPSG:4326 point geometry column named `geom`.

Such datasets will also have a set of derived fields to format the coordinates of this geometry in both:

- decimal degrees (DD):
  - derived using the PostGIS `st_y()` and `st_x()` functions respectively
  - held in the `lat_dd` and `lon_dd` columns
- degrees decimal minutes (DDM):
  - derived using the custom `geom_as_ddm` function
  - held in the `lat_ddm` and `lon_ddm` columns

These derived columns are [generated](https://www.postgresql.org/docs/16/ddl-generated-columns.html), meaning they are
computed from other table columns (in this case `geom`) and will always be sync. These columns are inherently read
only and are cast or returned as text.

Values for DDM formatted coordinates use a fixed number of decimal places (6) to match the default used for DD
formatted coordinates.

For example:

| PK  | PID                           | Geom                                                 | Lat (DD)                 | Lon (DD)             | Lat (DDM)          | Lon (DDM)         | ... |
|-----|-------------------------------|------------------------------------------------------|--------------------------|----------------------|--------------------|-------------------|-----|
| `1` | `01H26N7D9Q064B6QQMCPP5NQK0 ` | `0101000020E6100000F049670B7E804FC0F983F2C579D850C0` | `-67.38243244822651`     | `-63.00384657424354` | `67° 22.945947' S` | `63° .230794' W`  | ... |
| ... | ...                           | ...                                                  | ...                      | ...                  | ...                | ...               | ... |
| `9` | `01H26N7D9SGG348R24KN6W50GX ` | `0101000020E6100000B685DCAFBB7752C06F6E39F206B852C0` | `-74.87542396172078`     | `-73.8708305028475`  | `74° 52.525438' S` | `73° 52.24983' W` | ... |
| ... | ...                           | ...                                                  | ...                      | ...                  | ...                | ...               | ... |

### QGIS editing support for routes

The controlled *Route* dataset is non-spatial, as they consist of an ordered sequence of *Waypoint* identifiers. This
prevents editing of routes in QGIS which requires a linestring geometry.

To support being able to edit route features in QGIS a writable view is implemented as part of the controlled dataset
schemas. For reading, the view includes a derived `geom` column by combining the point geometries of each waypoint
included in the route into a linestring. For writing, triggers split the linestring geometry into points, which are
converted into waypoint identifiers, using the waypoint geometry as a join. A tolerance of 1KM is used to avoid
precision differences preventing this spatial join not need to match feature positions exactly.

### Field Operations planning datasets

A schema for Field Operations to plan additional activities by creating additional datasets, storing experimental data
and prototyping changes to [Controlled](#controlled-datasets) datasets.

These datasets are managed by Field Operations, and do not need to (but may) follow any conventions or requirements
such as naming conventions, required columns, etc.

It's expected that datasets will vary in maturity and importance, with data ranging from fully experimental through to
being a definitive source of truth.

Datasets are stored in the `planning_field_ops` database schema. No table schemas etc. are defined for these datasets
in this project.

**Note:** Whilst datasets in this schema are restricted, [QGIS Layer Styles](#qgis-layer-styles) that apply to them are
not due to a general platform limitation.

## Requirements

Required infrastructure:

- a service or server for running [Python](https://www.python.org) applications
- a service or server for running [Postgres](https://www.postgresql.org) databases
- an Azure Entra (Active Directory) app registration
- LDAP groups and application user
- a file system for holding [Backups](#backups)
- a Sentry subscription to monitor [Automated backups](#backups-automation)

### Application server requirements

Required OS packages for Python app server:

- Python >= 3.9
- OpenSSL >= 1.1.1 [1]
- OpenLDAP (including development headers)
- GDAL 3.4 (including development headers and the `gdal-config` binary [2])
- libxml (including the `xmllint` binary)
- libpq (including the `pg_dump` binary)

[1] In exceptional circumstances, the `urllib3` package can be downloaded to use an earlier version of OpenSSL. See
[Installation](#installation) section for more information.

[2] The GDAL OS and Python packages *MUST* be the same version, and must therefore be version `3.4`.

### Database requirements

Required Postgres extensions:

- PostGIS
- pgcrypto
- fuzzystrmatch

A single database, and an account with permissions to create, read, update and delete objects (inc. Postgres schemas)
within this, is required to run this application. This database and account can be named anything but `ops_data_store`
and `ops_data_store_app` respectively are recommended as conventional defaults.

In addition, a mechanism must be available for creating and maintaining Postgres role and users as outlined in abstract
in the [Permissions](#permissions) section and more specifically in [Database Permissions](#database-permissions). This must
support updating permissions as needed based on the memberships of the relevant LDAP groups.

### Microsoft Entra requirements

Required Azure app registration permissions (application assigned):

- `https://graph.microsoft.com/GroupMember.Read.All`
- `https://graph.microsoft.com/User.Read.All`

This app registration will need to be registered within the tenancy that group/team members will be synced from.

### LDAP requirements

LDAP groups are needed for each role in the [Permissions](#permissions) system, named as per the mapping table.

These groups must:

- be owned by a user representing this platform, conventionally named `apps_magic_ods`
- all sit within the same OU (e.g. 'OU=groups')

In addition:

- all LDAP users must be contained in a single OU (e.g. 'people' or 'users')

### File system requirements

A file system is required for storing application backups and log files.

This file system must:

- be accessible/addressable via the Python `Path` class (i.e. a local, or mounted network, file system)
- provide at least the created date for files via metadata the Python `Path.stat` method can access
- provide suitable permissions for the Python application to read and write all files (i.e. via an OS user)
- have sufficient space to maintain the number of backups and log files configured (recommended minimum: 5GB)

As this file system is used for backups, it should to the extent possible, be designed to be stable/reliable.

### Sentry requirements

A [Sentry](https://sentry.io/) subscription is required for monitoring automated backups with:

- a Sentry team that should receive failure notifications (e.g. `magic`)
- a Sentry project to represent the platform (`ops-data-store`)

## Installation

**Note:** Ensure all steps in the [Project Setup](#project-setup) section are complete before installing.

### Install python app

For the Python application, it is strongly recommended to install this project into a virtual environment:

```
$ python -m venv /path/to/venv
$ source /path/to/venv/bin/activate
$ python -m pip install --upgrade pip
```

The Python Package for this project (see [Deployment](#deployment) section) requires installing from a private package
registry provided by the BAS GitLab instance. This registry requires authentication, however as this project is
available publicly, and has been open sourced, the generic deployment token below can be used by anyone to access it.

```
$ python -m pip install ops-data-store --extra-index-url https://public-access:RPiBoxfdzokx_GSzST5M@gitlab.data.bas.ac.uk/api/v4/projects/1134/packages/pypi/simple
```

**Note:** The `urllib3` dependency must be downgraded if installing on an OS with a version of OpenSSL earlier than
1.1.1:

```
$ python -m pip install --upgrade urllib3==1.26.18
```

### Verify python app installation

The control CLI can be used to check the application has been installed correctly and is the expected version:

```
# if installed in a virtual environment
$ source /path/to/venv/bin/activate

$ ods-ctl --version
0.1.0
```

### Create python app alias

Optionally, the `ods-ctl` command can be added to the PATH or symlinked to a location already in the PATH (such as
`~/bin/`) to make it easier to call:

```
$ mkdir ~/bin
$ cd ~/bin
$ ln -s /path/to/venv/bin/ods-ctl ods-ctl
$ cd ~
```

You pay need to add `~/bin` to your `PATH` by editing:

```
$ vi ~/.bash_profile
```

And adding:

```shell
# User specific environment and startup programs

PATH=$PATH:$HOME/.local/bin:$HOME/bin

export PATH
```

### Create python app environment file

Optionally, create a `.env` file to set [Configuration](#configuration) options or use relevant environment variables. See the
[Infrastructure](#infrastructure) section for connection information to use.

**Note:** If using an `.env` file, the application will look in parent directory of where the application is installed
(i.e. the virtual environment) and it's parents, up to the root directory (i.e. `/`). Common directories for
configuration files such as `/etc/` and `~/.config/` are NOT checked.

To check the application configuration is valid and as expected:

```
$ ods-ctl config check
Ok. Configuration valid.

$ ods-ctl config show
```

### Configure database

To check the application database is available, and then configure it for use:

```
$ ods-ctl db check
Ok. DB connection successful.

$ ods-ctl db setup
Setting up database for first time use.
Note: If this command fails, please either create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at magic@bas.ac.uk with the output of this command.
Ok. Database setup complete.
```

Create required schemas and empty controlled datasets in the database:

[`schemas.sql`](resources/db/schemas.sql)
[`dataset-controlled.sql`](resources/db/datasets-controlled.sql) file against the database.

```
$ ods-ctl db run --input-path resources/db/schemas.sql
$ ods-ctl db run --input-path resources/db/datasets-controlled.sql
```

Create database roles and uses needed for the [Permissions](#permissions) system and apply required
[Database Grants](#database-permissions), either directly against the database or by incorporating into a permissions
management mechanism.

### Configure QGIS layer SVGs

- within the [File Store](#file-store) create the [relevant directory](#qgis-layer-svgs) with suitable permissions for:
  - style authors to write to it
  - the [Web Server](#web-server) to serve files from it anonymously

### Configure auth syncing

If using an instance for syncing users and assigning dataset permissions, check Azure and LDAP are available:

```
$ ods-ctl auth check
Note: If this command fails, please check the configured credentials and external connectivity.
If problem persists, create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at magic@bas.ac.uk with the output of this command.
Ok. Auth connection successful.
```

Then sync Azure groups to LDAP:

```
$ ods-ctl auth sync -ag 34db44b7-4441-4f60-8daa-d0c192d74704 -lg apps_magic_ods_admin
$ ods-ctl auth sync -ag 75ec55c1-7e92-45e3-9746-e50bd71fcfef -lg apps_magic_ods_write_fo
$ ods-ctl auth sync -ag 7b8458b9-dc90-445b-bff8-2442f77d58a9 -lg apps_magic_ods_write_au
$ ods-ctl auth sync -ag 34db44b7-4441-4f60-8daa-d0c192d74704 -ag 75ec55c1-7e92-45e3-9746-e50bd71fcfef -ag 7b8458b9-dc90-445b-bff8-2442f77d58a9 -lg apps_magic_ods_read
```

### Install Sentry monitoring

To monitor application backups via Sentry install the [Sentry CLI](https://docs.sentry.io/product/cli/):

```
$ mkdir ~/bin
$ export INSTALL_DIR=./bin
$ curl -sL https://sentry.io/get-cli/ | sh
```

**Note:** The CLI can also be installed [manually](https://docs.sentry.io/product/cli/installation/#manual-download).

### Create backups cron job

Create a Sentry cron monitor within the relevant Sentry subscription:

- project: *ops-data-store*
- name/slug: `ods-backups`
- schedule type: *cron*
- cron pattern: `0 4 * * *`
- cron timezone: *UTC*
- grace period: `1` minutes
- max runtime: `2` minutes
- notify: `#magic`
- failure tolerance: `1`
- recovery tolerance: `1`
- environment: *All Environments*

Once created, edit the monitor's associated alert to set:

- conditions: post message to `#dev` channel in MAGIC Slack (in addition to regular team notification)
- action interval: *5 minutes*
- alert owner: `#magic`

Create directory for cron backup logs:

```
$ mkdir -p ~/logs/cron/
```

Add a new cron job `crontab -e`:

```
SHELL=/bin/bash
MAILTO=monitoring@example.com

## Operations Data Store automated backups - https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store#backups-automation
0 4 * * * SENTRY_DSN=[Sentry DSN] /users/ods/bin/sentry-cli monitors run -e [Sentry ENV] ods-backups -- /var/opt/ops-data-store/venv/bin/ods-ctl backup now >> /users/ods/logs/cron/ods-backup-$(date +\%Y-\%m-\%d-\%H-\%M-\%S-\%Z).log 2>&1

0 0 * * * /usr/bin/find /users/ods/logs/cron/ -name 'ods-backup-*.log' -type f -mtime +30 -delete
```

Replace `[Sentry DSN]`, `[Sentry ENV]` with secret and per-instance/environment label (e.g. `rothera-production`).

### Create conversion cron job

Create a Sentry cron monitor within the relevant Sentry subscription:

- project: *ops-data-store*
- name/slug: `ods-conversion`
- schedule type: *cron*
- cron pattern: `*/5 * * * *`
- cron timezone: *UTC*
- grace period: `5` minutes
- max runtime: `4` minutes
- notify: `#magic`
- failure tolerance: `1`
- recovery tolerance: `1`
- environment: *All Environments*

Once created, edit the monitor's associated alert to set:

- conditions: post message to `#dev` channel in MAGIC Slack (in addition to regular team notification)
- action interval: *5 minutes*
- alert owner: `#magic`

Create directory for cron backup logs:

```
$ mkdir -p ~/logs/cron/
```

Add a new cron job `crontab -e`:

```
SHELL=/bin/bash
MAILTO=monitoring@example.com

## Operations Data Store automated conversion - https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store#automatic-conversion
*/5 * * * * SENTRY_DSN=[Sentry DSN] /users/ods/bin/sentry-cli monitors run -e [Sentry ENV] ods-conversion -- /var/opt/ops-data-store/venv/bin/ods-ctl data convert >> /users/ods/logs/cron/ods-conversion-$(date +\%Y-\%m-\%d-\%H-\%M-\%S-\%Z).log 2>&1

0 0 * * * /usr/bin/find /users/ods/logs/cron/ -name 'ods-conversion-*.log' -type f -mtime +0 -delete
```

Replace `[Sentry DSN]`, `[Sentry ENV]` with secret and per-instance/environment label (e.g. `rothera-production`).

### Post installation tasks [WIP]

**Note:** This section is a work in progress and may be restructured.

- save an ad-hoc layer style in QGIS to create the QGIS `public.layer_styles` table in the new instance
- copy existing QGIS layer styles from an existing instance to the new instance

### Post installation checks [WIP]

**Note:** This section is a work in progress and may be restructured.

- check test data can be created using the application user in QGIS
  - suggested to add a test set of waypoints and route for verifying Air Unit conversion is working
- check test data can be created using an LDAP user
- check the web server can be accessed using an LDAP login
- check the Air Unit conversion process is working (requires some test waypoints/routes and the webserver)
- verify the back-up Sentry conversion monitor is running and ok for the new instance
- verify the Air Unit conversion Sentry monitor is running and ok for the new instance

## Upgrading

To upgrade the Python application, upgrade the Python package version using Pip:

```
# if installed in a virtual environment
$ source /path/to/venv/bin/activate
$ python -m pip install --upgrade ops-data-store --extra-index-url https://public-access:RPiBoxfdzokx_GSzST5M@gitlab.data.bas.ac.uk/api/v4/projects/1134/packages/pypi/simple
```

Check the version is as expected:

```
$ ods-ctl --version
0.2.0
```

Review [Configuration options](#configuration) are set correctly and check the application configuration is still valid:

```
$ ods-ctl config check
Ok. Configuration valid.
```

## Project Setup

Connection details for any resources created should be stored in the MAGIC 1Password shared vault.

### Microsoft Azure

- create app registration with the required permissions
- request NERC DDaT to approve required permissions
- optionally configure branding name, logo and internal note referencing this README

### GitLab

- create project with package registry and CI/CD enabled
- create deployment token for allowing anyone to install packages:
  - name: "Public Access"
  - username: "public-access"
  - scopes: *read_package_registry*

### BAS IT

- request an application server for running Python applications
  - where file quotas are enforced for home directories, request 10GB
    (see [MAGIC/ops-data-store#183 🛡️](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/183) for context)
- request a Postgres database with required extensions
- request a Windows VM (configured as a BAS workstation) with QGIS LTS installed to act as a reference VM
- request an LDAP entity to use for managing application LDAP groups
- request LDAP groups as needed for implementing application permissions
- request LDAP users for application, specifically:
  - the [MAGIC EO Acquisitions Script](#magic-eo-acquisitions-script)
- request SAN/data volume mounted in the application server with permissions for the Python app OS user to read/write
- request a user synchronisation mechanism between LDAP servers and between LDAP and Postgres
- request example users for each database role are created and documented in 1Password.
- request relevant grants be applied to allow Postgres database owner to grant permissions to objects it contains

## Infrastructure

### Environments and instances

There are several instances and environments for this project:

Environments:

* *Development* - for developing the Data Store (see [Development](#local-development-environment) section)
* *Staging* - for pre-release testing and experimentation.
* *Production* - for real use.

Instances:

* Cambridge (*Production*) - managed by BAS IT as general infrastructure
* Rothera (*Staging*) - managed by BAS IT in the wider SDA/stations staging infrastructure
* Rothera (*Production*) - managed by BAS IT in the on-station infrastructure

The infrastructure needed for each instance can be summarised by this diagram:

![infrastructure](docs/img/infrastructure.png)

Some of the infrastructure used by this project is environment or instance specific. Other elements are shared across
all instances/environments as this diagram:

![environments-and-instances](docs/img/environments.png)

### Application servers

- [Cambridge (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=rzt4yigjenbkdtfho2famjzi3m&h=magic.1password.eu)
  - see [MAGIC/ops-data-store#170 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170) for initial setup
- [Rothera (Staging) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=rhe6qd7w46i5hrs42jhwtbnpuq&h=magic.1password.eu)
  - see [MAGIC/ops-data-store#39 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/39) for initial setup
- [Rothera (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=rhe6qd7w46i5hrs42jhwtbnpuq&h=magic.1password.eu)
  - see [MAGIC/ops-data-store#40 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/40) for initial setup

### Databases

- [Cambridge (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=wmpfl7kynx63yd3yzx2dyam7y4&h=magic.1password.eu)
  - see [MAGIC/ops-data-store#170 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170) for initial setup
- [Rothera (Staging) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=wmpfl7kynx63yd3yzx2dyam7y4&h=magic.1password.eu)
  - see [MAGIC/ops-data-store#39 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/39) for initial setup
- [Rothera (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=wmpfl7kynx63yd3yzx2dyam7y4&h=magic.1password.eu)
  - see [MAGIC/ops-data-store#40 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/40) for initial setup

##### Database application users

- `ods_app_eo_acq_script`:
  - [Rothera (Staging) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=qfrapkuwjsxxuevkoavbqiw2ne&h=magic.1password.eu)
    - see [MAGIC/ops-data-store#218 🛡️](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/218) for initial setup

### Azure App Registrations

- [BAS Operations Data Store 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=27ra54r3yrhogzesxdpw2iuybu&h=magic.1password.eu)

Used across all instances/environments. See
[MAGIC/operations/field-operations-gis-data#50 🛡](https://gitlab.data.bas.ac.uk/MAGIC/operations/field-operations-gis-data/-/issues/50)
for initial setup with UKRI.

### LDAP servers

- [Cambridge (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=27ra54r3yrhogzesxdpw2iuybu&h=magic.1password.eu)
- [Rothera (Staging) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=qnqmxfsoxnj7jblkelsgxs5fhu&h=magic.1password.eu)
- [Rothera (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=qnqmxfsoxnj7jblkelsgxs5fhu&h=magic.1password.eu)

### Reference VM

Used to simulate an end user computer used by Operations, acting as a known working example for debugging and testing.
Currently configured to use the *Rothera (Staging)* platform instance.

- [Windows VM 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=mb2mfbk66zrowd4kcj3kjc5tdy&h=magic.1password.eu)

### Sentry Project

- [Operations Data Store 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=ii2ev4tt3w7i3t2hmx7qbgqe6q&h=magic.1password.eu)

## Troubleshooting

### GeoPackage backups GDAL error

Symptoms:

An error occurs with the GeoPackage backup made when running the [`backup now`](#control-cli-backup-commands) command.

Prerequisites:

- access to the relevant instance
- GDAL binaries (`ogr2ogr`)
- connection details for the relevant database

Method:

- in the relevant instance, create an export directly using the [`data export`](#control-cli-data-commands) command
- if successful, check the state of the backup set
  (path available using the [`config show`](#control-cli-config-commands) command)
  - remove `controlled_datasets_backup.gpkg` if it exists
- if unsuccessful, use a test script, similar to the one attached in [1], to test the GDAL Python bindings in isolation
- if unsuccessful, use the GDAL CLI tools to export to a GeoPackage manually
  - try exporting layers into individual files first [2]
  - then if successful, export all layers into the same file [3]

Verify any data using QGIS.

Context:

- https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170#note_112469

References:

[1] https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170#note_112581

[2]

```
$ ogr2ogr -f GPKG test.gpkg PG:"host=[hostname] dbname=[database] user=[username] password=[password]" "[table]"
```

E.g.:

```
$ ogr2ogr -f GPKG test.gpkg PG:"host=db.example.com dbname=ops-data-store user=ops-data-store password=xxx" "depot"
```

[3]

E.g.:

```
$ ogr2ogr -f GPKG test2.gpkg PG:"host=db.example.com dbname=ops-data-store user=ops-data-store password=xxx" "depot"
$ ogr2ogr -f GPKG -append test2.gpkg PG:"host=db.example.com dbname=ops-data-store user=ops-data-store password=xxx" "instrument"
$ ogr2ogr -f GPKG -append test2.gpkg PG:"host=db.example.com dbname=ops-data-store user=ops-data-store password=xxx" "..."
$ ogr2ogr -f GPKG -append test2.gpkg PG:"host=db.example.com dbname=ops-data-store user=ops-data-store password=xxx" "layer_styles"
```

### LDAP queries

#### LDAP query - get user

```
$ ldapsearch -x -H [Server] -D [Bind DN] -W -b "[Base DN]" "(uid=[User])"
```

Where: `[Base DN]` is `[OU people],[Base DN]`, E.g.: `"ou=people,dc=example,dc=com"` and `[User]` is the user to find
(E.g. `conwat`).

#### LDAP query - list group members

```
$ ldapsearch -x -H [Server] -D [Bind DN] -W -b "[Base DN]" member
```

Where: `[Base DN]` is `[Group name with prefix],[OU groups],[Base DN]`, E.g.: `"cn=foo,ou=groups,dc=example,dc=com"`

#### LDAP query - empty group

Remove all members of a group except one, as LDAP groups cannot be empty:

```
$ ldapmodify -x -H [Server] -D [Bind DN] -W -f modify_group.ldif
```

Where `modify_group.ldif` is for example:

```ldif
dn: cn=foo,ou=groups,dc=example,dc=com
changetype: modify
delete: member
member: uid=conwat,ou=users,dc=example,dc=com

...

dn: cn=foo,ou=groups,dc=example,dc=com
changetype: modify
delete: member
member: uid=...,ou=users,dc=example,dc=com
```

## Development

### Local development environment

Check out project:

```
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store.git
$ cd ops-data-store
```

**Note:** If you do not have access to the BAS GitLab instance, clone from GitHub as a read-only copy instead.

#### Local python environment

[Poetry](https://python-poetry.org/docs/#installation) is used for managing the Python environment and dependencies.

[pyenv](https://github.com/pyenv/pyenv) (`brew install pyenv`) is strongly recommended to ensure the Python version
matches deployed instances. E.g. where the deployed Python version is `3.9.18`:

```
$ pyenv install 3.9.18
$ pyenv local 3.9.18
$ poetry install
```

#### Local development database

A local [Postgres](#database) database (`brew install postgis`) is recommended to test storing [Datasets](#datasets):

```
$ brew services start postgresql
$ psql -d postgres -c 'CREATE DATABASE "ops-data-store-dev";'
$ psql -d postgres -c 'COMMENT ON DATABASE "ops-data-store-dev" IS '\''Ops Data Store local development'\'';'
```

**Note:** This database name is a convention and used in SQL files that will be run later. If changed, all references
will need amending locally.

#### Local development setup

It's strongly recommended to set required configuration options using a `.env` file based off the
[`.example.env`](/.example.env) file as a reference.

A `.test.env` file MUST be created as per the [Testing Configuration](#test-config) section.

In QGIS, create the `public.layer_styles` table by creating an ad-hoc layer and saving its style to the database (the
created style and ad-hoc layer can be removed once the table is created).

Set up the database, create schemas and assign permissions for [Controlled Datasets](#controlled-datasets):

```
$ poetry run ods-ctl db run --input-path resources/db/roles.sql
$ poetry run ods-ctl db run --input-path tests/resources/db/users.sql

$ poetry run ods-ctl db setup
$ poetry run ods-ctl db run --input-path resources/db/schemas.sql
$ poetry run ods-ctl db run --input-path resources/db/datasets-controlled.sql
$ poetry run ods-ctl db run --input-path tests/resources/db/grants.sql
```

The QGIS profile used for testing needs [downloading 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/)
from the GitLab package registry (as it's too large to sensibly store in Git).

Once downloaded, extract and rename to `ops-data-store`. Then copy to the relevant QGIS profile directory:

- macOS: `~/Library/Application\ Support/QGIS/QGIS3/profiles/`
- Windows: `%APPDATA%\Roaming\QGIS\QGIS3\profiles/`

#### Running control CLI locally

```
$ poetry run ods-ctl [COMMAND] [ARGS]
```

### Contributing

All code changes should be:

- made using a merge request associated with an issue in the project's
  [Issue Tracker 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues)
- summarised in the [Change log](./CHANGELOG.md)

### Editorconfig

For consistency is strongly recommended to configure your IDE or other editor to use the [EditorConfig](https://EditorConfig.org) settings defined in [`.editorconfig`](.editorconfig).

### Conventions

- except for tests, all Python code should be contained in the [`ops_data_store`](/src/ops_data_store) package.
- use `Path.resolve()` if displaying or logging file/directory paths in Python
- Python dependencies are managed with [Poetry](https://python-poetry.org) in `pyproject.toml`
- configuration options should be defined in the common [`Config`](/src/ops_data_store/config.py) class and this README in alphabetical order
- configuration options should be read using the relevant [environs](https://github.com/sloria/environs) helper method
- use logging to record how actions progress, using the `app` logger (e.g. `logger = logging.getLogger('app')`)

### Python dependency vulnerability checks

The [Safety](https://pypi.org/project/safety/) package is used to check dependencies against known vulnerabilities.

**WARNING!** As with all security tools, Safety is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this is using the free vulnerability database, which is updated less frequently than paid options.

Checks are run automatically in [Continuous Integration](#continuous-integration). To check locally:

```
$ poetry run safety scan
```

### Python GDAL dependency version

The [GDAL Python bindings](https://pypi.org/project/GDAL/) are tied to the [GDAL library](https://gdal.org) version.

BAS IT managed servers currently use an older version of GDAL (3.4.3) which is required by this project. Installing
this version in a development environment is often unsupported due to its age causing an incompatibility.

Running with the 3.4.3 Python bindings but a newer Library version will give errors such as:

```
src/ops_data_store/data.py:4: in <module>
    from osgeo.gdal import (
.venv/lib/python3.9/site-packages/osgeo/__init__.py:45: in <module>
    _gdal = swig_import_helper()
.venv/lib/python3.9/site-packages/osgeo/__init__.py:42: in swig_import_helper
    return importlib.import_module('_gdal')
E   ModuleNotFoundError: No module named '_gdal'
```

The correct fix for this problem is to upgrade the version of GDAL available on BAS IT managed servers. In the meantime
a workaround can be used to locally upgrade the Python bindings to match a newer Library version but not commit the
updated Poetry lock file.

This creates a problem when other dependencies are added or updated as the upgraded Python bindings package will also
be included, and partial updates cannot be committed because the file includes a checksum. To work around this problem
the following workflow can be used:

1. make other changes as needed
2. downgrade the GDAL dependency [1]
3. commit the Poetry lock file
4. upgrade the GDAL dependency (but do not commit change) [2]

[1]

```
$ poetry remove gdal
$ poetry add gdal@3.4.3
```

[2]

```
$ poetry remove gdal
$ poetry add gdal
```

(Adapt the second `add gdal` command to the version of GDAL needed locally).

### Python static security analysis

Ruff is configured to run [Bandit](https://github.com/PyCQA/bandit), a static analysis tool for Python.

**WARNING!** As with all security tools, Bandit is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this tool can't check for issues that are only be detectable when running code.

### Python linting

[Ruff](https://docs.astral.sh/ruff/) is used to lint and format Python files. Specific checks and config options are
set in `pyproject.toml`. Linting checks are run automatically in [Continuous Integration](#continuous-integration).

To check locally:

```
$ poetry run ruff check src/ tests/
$ poetry run ruff format --check src/ tests/
```

To format files:

```
$ poetry run ruff format src/ tests/
```

### Development database

If using a local Postgres database installed through homebrew (where `@14` is the version installed):

- to manage the service: `brew services [command] postgresql@14`
- to view logs: `/usr/local/var/log/postgresql@14.log`

### Adding new configuration options

1. add new properties to `ops_data_store.config.Config` class
2. include new properties to `ops_data_store.config.Config.dump()` method
3. if relevant, update `ops_data_store.config.Config.validate()` method
4. if relevant, update `.env` files and templates
5. if relevant, update `.gitlab-ci.yml` variables
6. add fixture to `tests.conftest`
7. include fixture in `tests.conftest.fx_test_config_dict` fixture
8. update `tests.ops_data_store_tests.test_config` module

## Testing

### Python tests

All 1st party Python code in the [`ops_data_store`](/src/ops_data_store) package must be covered by tests, defined in
the [`ops_data_store_tests`](/tests/ops_data_store_tests) package.

[`pytest`](https://pytest.org) is used as the test framework, configured in [`pyproject.toml`](/pyproject.toml).

#### Python test fixtures

Fixtures should be defined in [`conftest.py`](tests/conftest.py), prefixed with `fx_` to indicate they are a fixture,
e.g.:

```python
import pytest

@pytest.fixture()
def fx_test_foo() -> str:
    """Example of a test fixture."""
    return 'foo'
```

#### Python test coverage

Test coverage is checked with [`pytest-cov`](https://pypi.org/project/pytest-cov/) with an aim for 100% coverage
(with some exceptions). Exemptions for coverage should be used sparingly and only with good justification. Where tests
are added to ensure coverage, the `cov` [mark](https://docs.pytest.org/en/7.1.x/how-to/mark.html) should be added, e.g:

```python
import pytest

@pytest.mark.cov
def test_foo():
    assert 'foo' == 'foo'
```

#### Test config

An additional [`.test.env`](/.test.env) file is used to override some application config properties, such as the
database. This file can be created from the [`.example.test.env`](/.example.test.env) reference file.

#### Test limitations

There is a known and major limitation with tests mocking interactions with the database leading to bugs such as
[MAGIC/ops-data-store#124 🛡️](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/124).

See [MAGIC/ops-data-store#159 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/159) for progress to
address this.

#### Running tests

Tests and coverage checks are run automatically in [Continuous Integration](#continuous-integration). To check locally:

```
$ poetry run pytest --strict-markers --random-order --cov --cov-report=html tests
```

### Continuous Integration

All commits will trigger Continuous Integration using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

The Docker Image used for CI is needed to ensure the correct version of the GDAL is used, which is then configured to
use the correct Python version.

## Deployment

### Python package

This project is distributed as a Python package installable from a private package registry provided by the BAS
GitLab instance. It is built by Poetry automatically as part of [Continuous Deployment](#continuous-deployment). If
needed it can also be built manually:

```
$ poetry build
```

### QGIS profile

If the QGIS profile used for testing needs updating, the generic package stored in GitLab can be updated:

```
$ curl --header "PRIVATE-TOKEN: $BAS_GITLAB_TOKEN" --upload-file resources/qgis/qgis-profile.zip https://gitlab.data.bas.ac.uk/api/v4/projects/1134/packages/generic/qgis-profile/[version]/qgis-profile.zip
```

Where `[version]` is replaced with a calendar based version `YYYY-MM-DD.N`, e.g. the first release on April 12th 2024
would become `2023-04-12.0`. A second release that day would be `2023-04-12.1` etc.

For example:

```
$ curl --header "PRIVATE-TOKEN: $BAS_GITLAB_TOKEN" --upload-file resources/qgis/qgis-profile.zip https://gitlab.data.bas.ac.uk/api/v4/projects/1134/packages/generic/qgis-profile/2023-04-12.0/qgis-profile.zip
```

### Continuous Deployment

Tagged commits will trigger Continuous Deployment using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

## Releases

- [all releases 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/releases)
- [latest release 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/releases/permalink/latest)

To create a release, create an issue using the *release* issue template and follow the included checklist.

## Feedback

This project is maintained by the BAS Mapping and Geographic Information Centre
([MAGIC](https://bas.ac.uk/teams/magic)), contactable at: [magic@bas.ac.uk](mailto:magic@bas.ac.uk).

## License

Copyright (c) 2023-2024 UK Research and Innovation (UKRI), British Antarctic Survey (BAS).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
