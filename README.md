# Operations Data Store

Data store for hosted and managed datasets for BAS Field Operations and Air Unit.

## Overview

### Purpose

This Data Store is a platform provided by the British Antarctic Survey (BAS) Mapping and Geospatial Information Centre
([MAGIC](https://bas.ac.uk/teams/magic)) for hosting vector geospatial data used by BAS Operational Teams.

It consists of a limited set of managed datasets used and controlled by the BAS Air Unit and Field Operations teams for
planning and delivering field seasons.

**Note:** This project is focused on needs within the British Antarctic Survey. It has been open-sourced in case it's
of use to others with similar or related needs. Some resources, indicated with a 🛡 symbol, are not accessible publicly.

### Status

This project is an early alpha. The aim is to provide a robust, useful, live service within the next few field seasons.

The aim for this season is to provide a initial minimal implementation which meets core user needs. This will likely
change in form and function based on feedback from end-users and our experience of operating the platform.

### Limitations

As an alpha project, all, or parts, of this service:

- may, but should not, stop working (due to regressions or instability)
- may not work correctly, or as expectedly (including destructively)
- may change at any time (in terms of implementation or functionality)
- may have missing or outdated documentation

**Note:** Support for this project is provided on a best efforts / 'as is' basis.

**WARNING:** Outputs from this project should not be relied upon for operational use without through scrutiny.

In relation to operations that can performed by end-users vs. platform operators (MAGIC):

- end-users cannot define new datasets (tables) themselves
  - due to needing database permissions we can't yet assign safely
- end-users cannot add, change or remove dataset fields (table columns) themselves
  - due to schemas being defined within this project and risking inconsistencies due to ad-hoc, per-instance changes

In all these cases, end-users will need to request changes are made by contacting someone from MAGIC.

In relation to dataset [Permissions](#permissions), support for the following are not yet available:

- creating and synchronising LDAP members to the database as postgres roles and users
- running the Azure to LDAP group sync from a hosted environment (depends on a central LDAP user)

### Related projects

This project is limited to the technical and operational aspects of providing a platform for hosting datasets. Other
projects focus on these datasets and other aspects of a providing a wider Geographic Information System (GIS).

- [BAS Field Operations Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/operations/field-operations-gis-data)
- [BAS Air Unit Network Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset)

This project is an evolution of an earlier [Experiment 🛡](https://gitlab.data.bas.ac.uk/felnne/ops-data-store-exp).

## Usage

### End-user documentation

End-users should consult the documentation developed for the wider
[Field Operations GIS Platform 🛡](https://app.gitbook.com/o/-MbhSFJ1AEZxhIfX9tgr/s/HmSXoUpviCA3XCta5MDr/), as this
specific project is not aimed at end-users directly.

### Control CLI

**Note:** This CLI is intended for use by MAGIC team members, not end-users.

A command line interface, `ods-ctl`, is available for performing administrative tasks.

```
$ ssh [user]@[host]
$ ods-ctl --help
```

See the [Infrastructure](#infrastructure) section for connection details (specifically the relevant app server).

**Note:** Calling the CLI without any command will not return any output. This is expected.

**Note:** Currently all log entries down to debug level are displayed alongside programme output. This includes a debug
message from the `psycopg` Postgres database module that can be safely ignored:

```
YYYY-MM-SS HH:MM:SS - psycopg.pq - DEBUG - couldn't import psycopg 'c' implementation: No module named 'psycopg_c'
0.2.0
```

#### Control CLI `auth` commands

- `ods-ctl auth check`: verifies authentication/authorisation services are available
- `ods-ctl auth sync --azure-group [group-id] --ldap-group [group-id]`: syncs members of an Azure group to an LDAP group

#### Control CLI `config` commands

- `ods-ctl config check`: verifies required configuration options have been set
- `ods-ctl config show`: displays the current application configuration

#### Control CLI `db` commands

- `ods-ctl db check`: verifies the database is available
- `ods-ctl db setup`: configure a new database for use
- `ods-ctl db run --input-path [path/to/file.sql]`: runs SQL commands contained in the input file

### QGIS project

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

The included QGIS project, developed as part of the wider Field Operations and Air Unit GIS, can be used for testing
editing workflows and verifying expected behaviour.

1. start QGIS LTR with the `ops-data-store` profile selected:
1. open the included QGIS project file [`qgis-project.qgz`](/resources/qgis/qgis-project.qgz)

If needed, shortcuts can be created to start QGIS with a specific profile:

- on macOS: `open -a QGIS-LTR.app --args --profile {profile}`
- on Windows: `C:\Program Files\QGIS 3.28.7\bin\qgis-bin.exe --profile {profile}`

**Note:** To start QGIS normally use the `default` profile.

#### Adding DB connection

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

Replace `{placeholder}` values wth settings from the relevant database listed in the [Infrastructure](#infrastructure)
section, except for `{username}` and `{password}` which should be the users BAS LDAP credentials.

1. open QGIS with the relevant profile active
2. from *Browser* pane -> *PostgreSQL* -> *New Connection*:
   - *(ignore or use default values for options not specified)*
    - Name: `Ops Data Store ({location})`
    - Host: `{host}`
    - Database: `{database}`
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

**Note:** These instructions depend on the [Adding DB connection](#adding-db-connection) workflow.

1. open QGIS with the relevant profile and project active
1. from the *Browser* pane -> *PostgreSQL* -> *Ops Data Store*
    - *(the user may have multiple *Ops Data Store* entries they'll need to pick from based on their current location)*
1. select relevant layer -> *Add Layer to Project*

To configure a layer for the first time:

1. from the *Layers* pane -> (added layer) -> *Properties* -> *Attribute Form*:
    - *pk* and *pid*:
      - *General* -> *Editable*: *Uncheck*
      - *Widget Type*: *Hidden*
      - *Constraints* -> *Enforce not null constraint*: *Uncheck*
      - *Constraints* -> *Enforce unique constraint*: *Uncheck* (for *pk* field)
    - *id*:
      - *Constraints* -> *Enforce not null constraint*: *Check* (if desired)
    - *pk*, *pid*, *updated_at*, *updated_by*, *lat_dd*, *lon_dd*, *lat_ddm* and *lon_ddm*:
      - *General* -> *Editable*: *Uncheck*
      - *Widget Type*: *Hidden*
1. set other layer properties (symbology, labelling, etc.) as needed
1. *Style* -> *Save as Default* -> *Datasource Database* -> *Ok*

**Note:** The first layer style saved to the database will automatically create a `layer_styles` table.

#### Editing features in DB layer

**Note:** These instructions are intended for adapting into documentation by MAGIC team members.

**Note:** These instructions depend on the [Adding DB layer](#adding-db-layer) workflow.

Layers can be edited as normal, the add feature form should already be configured to hide generated or platform fields.

## Implementation

### Command line interface

[Typer](https://typer.tiangolo.com) is used as the framework for the control CLI.

### Configuration

The [control CLI](#command-line-interface) uses a series of settings for connecting to external services and reporting internal information.
Some settings are read-only, such as the application version, others are write-only, such as database connection
details, and must be defined by the user, using either appropriate environment variables, or an `.env` file.

**Note:** If using an `.env` file, an example [`.example.env`](.example.env) is available as a guide.

| Config Property            | Environment Variable               | Required | Sensitive | Read Only | Type            | Description                                             | Example                                                                  |
|----------------------------|------------------------------------|----------|-----------|-----------|-----------------|---------------------------------------------------------|--------------------------------------------------------------------------|
| `VERSION`                  | -                                  | No       | No        | Yes       | String          | Application version, read from package metadata         | '0.1.0'                                                                  |
| `DB_DSN`                   | `APP_ODS_DB_DSN`                   | Yes      | Yes       | No        | String          | Application database connection string [1]              | 'postgresql://user:pass@host/db'                                         |
| `AUTH_AZURE_AUTHORITY`     | `APP_ODS_AUTH_AZURE_AUTHORITY`     | No [2]   | No        | No        | String          | Endpoint used for authenticating against Azure          | 'https://login.microsoftonline.com/b311db95-32ad-438f-a101-7ba061712a4e' |
| `AUTH_AZURE_CLIENT_ID`     | `APP_ODS_AUTH_AZURE_CLIENT_ID`     | No [2]   | No        | No        | String          | Identifier used for authenticating against Azure        | '3b2c5acf-728a-4b78-85f0-9560a6aad701'                                   |
| `AUTH_AZURE_CLIENT_SECRET` | `APP_ODS_AUTH_AZURE_CLIENT_SECRET` | No [2]   | Yes       | No        | String          | Secret used for authenticating against Azure            | 'xxx'                                                                    |
| `AUTH_AZURE_SCOPES`        | -                                  | No [2]   | No        | Yes       | List of Strings | Permissions requested when authenticating against Azure | ['https://graph.microsoft.com/.default']                                 |
| `AUTH_MS_GRAPH_ENDPOINT`   | -                                  | No [2]   | No        | Yes       | String          | Endpoint used for the Microsoft Graph API               | 'https://graph.microsoft.com/v1.0'                                       |
| `AUTH_LDAP_URL`            | `APP_ODS_AUTH_LDAP_URL`            | No [2]   | No        | No        | String          | Endpoint used for authenticating against LDAP server    | 'ldap://ldap.example.com:389'                                            |
| `AUTH_LDAP_BASE_DN`        | `APP_ODS_AUTH_LDAP_BASE_DN`        | No [2]   | No        | No        | String          | Base scope to apply to all LDAP queries                 | 'dc=example,dc=com'                                                      |
| `AUTH_LDAP_BIND_DN`        | `APP_ODS_AUTH_LDAP_BIND_DN`        | No [2]   | No        | No        | String          | Identifier used for authenticating against LDAP server  | 'cn=app,ou=apps,dc=example,dc=com' [3]                                   |
| `AUTH_LDAP_BIND_PASSWORD`  | `APP_ODS_AUTH_LDAP_BIND_PASSWORD`  | No [2]   | Yes       | No        | String          | Secret used for authenticating against LDAP server      | 'xxx'                                                                    |
| `AUTH_LDAP_OU_USERS`       | `APP_ODS_AUTH_LDAP_OU_USERS`       | No [2]   | No        | No        | String          | Scope for user related objects in LDAP server           | 'users'                                                                  |
| `AUTH_LDAP_OU_GROUPS`      | `APP_ODS_AUTH_LDAP_OU_GROUPS`      | No [2]   | No        | No        | String          | Scope for group related objects in LDAP server          | 'groups'                                                                 |
| `AUTH_LDAP_CXT_USERS`      | `APP_ODS_AUTH_LDAP_CXT_USERS`      | No [2]   | No        | No        | String          | LDAP naming context prefix used to identify users       | 'cn' [3]                                                                 |
| `AUTH_LDAP_CXT_GROUPS`     | `APP_ODS_AUTH_LDAP_CXT_GROUPS`     | No [2]   | No        | No        | String          | LDAP naming context prefix used to identify groups      | 'cn' [3]                                                                 |

**Note:**

[1] The `DB_DSN` config option MUST be a valid [psycopg](https://www.psycopg.org) connection string

[2] `AUTH_*` config options are required if managing authentication/authorisation aspects of the Data Store

[3] Make sure to use the correct naming context prefix for the LDAP server, e.g. `cn=conwat` vs. `uid=conwat`.

### Database

[PostgreSQL](https://www.postgresql.org) is used for storing datasets. It uses the [PostGIS](https://postgis.net)
extension for storing spatial information along with custom functions and data types for:

- creating [ULIDs](https://github.com/ulid/spec) (stored as a UUID data-type)
  - [pgcrypto](https://www.postgresql.org/docs/current/pgcrypto.html) extension, `generate_ulid` function
- formatting latitude and longitude values in the Degrees, Decimal Minutes format (DDM)
  - using the `geom_as_ddm` function and `ddm_point` data type
- recording when and by who rows in managed datasets are changed
  - using the `set_updated_at` and `set_updated_by` functions

### QGIS

[QGIS](https://qgis.org) is the QGIS client end-users will use for editing and visualising geospatial data, and acts as
the database client in relation to this project specifically.

For consistency/compatibility, the QGIS profile and project developed for the wider GIS are used for consistency and
compatibility.

### Azure

Azure Entra (Active Directory) is the Identity Provider (IDP) used by NERC, within which BAS sits. An application
registration represents this project within Azure and is used to grant permission to resources within the Microsoft
Graph API.

### Microsoft Graph

The Microsoft Graph API provides programmatic access to Microsoft Team member listings (represented as Office 365
Groups). These membership listings are replicated to LDAP groups as part of the Data Store's
[Permissions](#permissions) system.

### LDAP

LDAP is the Identity Provider (IDP) used by BAS IT, specifically for unix systems including [Postgres](#database) and
[Apache](#web-server). It is used for both authentication and authorisation through a number of application controlled
groups. The members of these groups are synced from one or more Microsoft Azure groups as part of the Data Store's
[Permissions](#permissions) system.

### Web Server [WIP]

**Note:** This section is a work in progress and may be incomplete.

...

### Permissions

**Note:** This section is a work in progress and may be incomplete.

Datasets hosted in this platform are typically restricted as to who can read and/or edit from them. The platform
includes a simple permissions system to enforce these restrictions. This system includes three roles which can be
assigned to individual users:

- *admins*: can view and change any information to manage and administer the platform (inc. members of MAGIC and BAS IT)
- *owners*: can change and view information
- *viewers*: can read information only

Individuals can hold multiple roles at the same time (i.e. a user can hold the *owner* and *viewer* roles).

The *admin* and *viewers* roles are global (applies to all datasets). The *owner* role is scoped to datasets owned by
particular team. Team members can only change datasets within their team. These teams are currently:

- BAS Field Operations
- BAS Air Unit

E.g. For a dataset for field instruments owned by the BAS Field Operations team:

- BAS Field Operations team members can change this dataset
- BAS Air Unit team members cannot change this dataset, as though they hold the *owners* role, they are a different team
- *admin* role holders can change this dataset, as they can change all information in the platform
- *viewer* role holders can view but cannot change this dataset, as they can view all information in the platform

**Note:** It is not currently possible to limit viewing information to a specific team, only who can change it.

These roles are implemented in the [Database](#database) using roles and users:

- roles are represented as postgres roles, which are granted permissions to read or change information in all or
  specific tables
- individuals are represented as postgres users, which are assigned (inherit) one or more postgres roles

Users are assigned to roles based on the membership of groups held in an [LDAP server](#ldap). I.e. members of LDAP
group 'x' are assigned to Postgres role 'x'. LDAP group members are copied from a series of [Azure](#azure) groups
representing Microsoft Teams. These Microsoft Teams are used by teams generally and not specific to this project or
platform (for example the Microsoft Team used by the BAS Air Unit generally is used for `app_magic_ods_write_au` group).

Membership information moves in one direction: from Azure (MS Teams) to LDAP, then to Postgres. Users must exist in the
relevant LDAP server before they can be added to LDAP groups. LDAP users and groups may be synced between environments,
or may require adding in each. See the notes in the [Infrastructure](#infrastructure) section for more information.

Mappings for roles, teams, the database and LDAP:

| Role     | Team                 | Postgres Role               | LDAP Group                   |
|----------|----------------------|-----------------------------|------------------------------|
| Admins   | -                    | `app_magic_ods_write_admin` | `apps_magic_ods_write_admin` |
| Owners   | BAS Field Operations | `app_magic_ods_write_fo`    | `apps_magic_ods_write_fo`    |
| Owners   | BAS Air Unit         | `app_magic_ods_write_au`    | `apps_magic_ods_write_au`    |
| Viewers  | -                    | `app_magic_ods_read`        | `apps_magic_ods_read`        |

**Note:** There is currently an inconsistency between Postgres role names and LDAP group names (`app` vs `apps`).

The [Command Line Interface](#command-line-interface), specifically commands in the [`auth`](#control-cli-auth-commands)
command group can be used to synchronise users between these systems.

## Datasets

Datasets hosted in this platform can be classed as either:

- *managed*: formally defined datasets, where changes to structure of the dataset (i.e. new, changed or removed fields)
   must be agreed between data owners (Ops) and platform operators (MAGIC)
- *unmanaged*: any other datasets users may wish to store, which are essentially ignored by this platform

### Managed datasets

This platform defines base requirements for managed datasets, such that they provide minimally agreed functionality. In
practical terms this means all managed datasets using the same base table structure, with additional fields and
functionality extending from this.

This base schema comprises:

- a set of [Identifier](#managed-dataset-identifiers) fields
- a pair of [Last Update](#managed-dataset-last-update-fields) fields
- a set of [Geospatial](#managed-dataset-geometry-fields) fields

Any additional fields are determined in these other projects:

- BAS [Field Operations GIS Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/operations/field-operations-gis-data)
- BAS [Air Unit Network Dataset 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset)

Complete schemas for managed datasets are defined in [`dataset-schemas.sql`](resources/data/dataset-schemas.sql).

See the relevant sub-section for adding to, amending or removing from these schemas.

### Managed dataset identifiers

All managed datasets have at least two identifiers, though most will have three as defined below:

| Domain     | Owner    | Audience  | Column Name | Data Type | Format/Scheme                        | Required |
|------------|----------|-----------|-------------|-----------|--------------------------------------|----------|
| Technology | MAGIC/IT | MAGIC/IT  | `pk`        | Integer   | PostgreSQL Identity                  | Yes      |
| Platform   | MAGIC    | MAGIC/Ops | `pid`       | UUID      | [ULID](https://github.com/ulid/spec) | Yes      |
| Dataset    | Ops      | MAGIC/Ops | `id`        | String    | -                                    | No       |

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

### Managed dataset last update fields

All managed datasets have two last update columns:

- `updated_at`: timestamp of when a row was last changed
- `updated_by`: identity of who last changed a row

Both fields are updated when any data in a given row changes via a Postgres trigger on each table calling a simple
functions (`NOW()` and `current_user` respectively). The value of `current_user` should correspond to a NERC username,
and therefore an end-user (e.g. `conwat` -> *Connie Watson*).

For example:

| PK  | PID                           | Updated At                          | Updated By | ... |
|-----|-------------------------------|-------------------------------------|------------|-----|
| `1` | `01H26N7D9Q064B6QQMCPP5NQK0 ` | `2023-08-24 15:23:01.583312 +00:00` | `conwat`   | ... |
| ... | ...                           | ...                                 | ...        | ... |
| `9` | `01H26N7D9SGG348R24KN6W50GX ` | `2023-10-14 09:46:23.237912 +00:00` | `conwat`   | ... |
| ... | ...                           | ...                                 | ...        | ... |

### Managed dataset geometry fields

All managed datasets have a PostGIS EPSG:4326 point geometry column named `geom`.

Managed datasets also have a set of derived fields to format the coordinates of this geometry in both:

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

### Adding a new managed dataset

**Note:** This section is a work in progress and may be incomplete.

Update [`dataset-schemas.sql`](resources/data/dataset-schemas.sql) with the template below replacing:

1. `NEW_DATASET` with the singular, lower case, name of the new dataset (e.g. 'cave' not 'CAVES')
    - for multi-word names use underscores as a separator (e.g. 'moon_base' not 'moon-base')
1. adding additional fields as needed
    - use `TEXT` for string fields rather than `VARCHAR`

```sql
-- NEW_DATASET

CREATE TABLE IF NOT EXISTS public.NEW_DATASET
(
  pk         INTEGER GENERATED ALWAYS AS IDENTITY
    CONSTRAINT NEW_DATASET_pk PRIMARY KEY,
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

CREATE INDEX IF NOT EXISTS NEW_DATASET_geom_idx
  ON public.NEW_DATASET USING gist (geom);

CREATE TRIGGER NEW_DATASET_updated_at_trigger
  BEFORE INSERT OR UPDATE
  ON NEW_DATASET
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER NEW_DATASET_updated_by_trigger
  BEFORE INSERT OR UPDATE
  ON NEW_DATASET
  FOR EACH ROW
  EXECUTE FUNCTION set_updated_by();
```

### Amending an existing managed dataset [WIP]

**Note:** This section is a work in progress and may be incomplete.

...

### Removing a managed dataset [WIP]

**Note:** This section is a work in progress and may be incomplete.

...

## Requirements

Required infrastructure:

- a service or server for running [Python](https://www.python.org) applications
- a service or server for running [Postgres](https://www.postgresql.org) databases
- an Azure Entra (Active Directory) app registration

### Application server requirements

Required OS packages for Python app server:

- Python 3.9+
- GDAL 3.4 (including development headers and the `gdal-config` binary)
- libxml (including the `xmllint` binary)
- libpq

**Note:** The GDAL OS and Python packages *MUST* be the same version, and must therefore be version `3.4`.

### Database requirements

Required Postgres extensions:

- PostGIS
- pgcrypto
- fuzzystrmatch

A single database, and an account with permissions to create, read, update and delete objects within this, is required
to run this application. This database and account can be named anything but `ops_data_store` and `ops_data_store_app`
respectively are recommended as conventional defaults.

### Azure Entra requirements

Required Azure app registration permissions (application assigned):

- `https://graph.microsoft.com/GroupMember.Read.All`
- `https://graph.microsoft.com/User.Read.All`

This app registration will need to be registered within the tenancy that group/team members will be synced from.

## Installation

For the Python application, it is strongly recommended to install this project into a virtual environment:

```
$ python -m venv /path/to/venv
$ source /path/to/venv/bin/activate
$ pip install --upgrade pip
```

The Python Package for this project (see [Deployment](#deployment) section) requires installing from a private package
registry provided by the BAS GitLab instance. This registry requires authentication, however as this project is
available publicly, and has been open sourced, the generic deployment token below can be used by anyone to access it.

```
pip install ops-data-store --extra-index-url https://public-access:RPiBoxfdzokx_GSzST5M@gitlab.data.bas.ac.uk/api/v4/projects/1134/packages/pypi/simple
```

The control CLI can be used to check the application has been installed correctly and is the expected version:

```
# if installed in a virtual environment
$ source /path/to/venv/bin/activate

$ ods-ctl --version
0.1.0
```

Optionally, the `ods-ctl` command can be added to the PATH or symlinked to a location already in the PATH (such as
`~/bin/`) to make it easier to call:

```
$ mkdir ~/bin
$ cd ~/bin
$ ln -s /path/to/venv/bin/ ods-ctl
$ cd ~
```

Optionally, create a `.env` file to set [Configuration](#configuration) options or use relevant environment variables.

**Note:** If using an `.env` file, the application will look in parent directory of where the application is installed
(i.e. the virtual environment) and it's parents, up to the root directory (i.e. `/`). Common directories for
configuration files such as `/etc/` and `~/.config/` are not checked.

To check the application configuration is valid and as expected:

```
$ ods-ctl config check
Ok. Configuration valid.

$ ods-ctl config show
```

To check the application database is available, and then configure it for use:

```
$ ods-ctl db check
Ok. DB connection successful.

$ ods-ctl db setup
Setting up database for first time use.
Note: If this command fails, please either create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at magic@bas.ac.uk with the output of this command.
Ok. Database setup complete.
```

Create the schemas for managed datasets by running the contents of the
[`dataset-schemas.sql`](resources/data/dataset-schemas.sql) file against the database.

```
$ ods-ctl db run --input-path dataset-schemas.sql
```

If using an instance for syncing users and assigning dataset permissions, check Azure and LDAP are available:

```
$ ods-ctl auth check
Note: If this command fails, please check the configured credentials and external connectivity.
If problem persists, create an issue in the 'Ops Data Store' project in GitLab, or contact MAGIC at magic@bas.ac.uk with the output of this command.
Ok. Auth connection successful.
```

Then sync Azure groups to LDAP using the script from `auth sync` command.

**Note:** See [1Password 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=i7gk2ohhoaalmnwcwhmco4rnzm&h=magic.1password.eu)
for a script with the specific group identifiers to sync.

### Upgrading [WIP]

To upgrade the Python application, upgrade the Python package version using Pip:

```
# if installed in a virtual environment
$ source /path/to/venv/bin/activate
$ pip install --upgrade ops-data-store --extra-index-url https://public-access:RPiBoxfdzokx_GSzST5M@gitlab.data.bas.ac.uk/api/v4/projects/1134/packages/pypi/simple
```

Check the version is as expected:

```
$ ods-ctl --version
0.2.0
```

Check the application configuration is still valid:

```
$ ods-ctl config check
Ok. Configuration valid.
```

## Project Setup [WIP]

**Note:** This section is a work in progress and may be restructured.

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
- request a Postgres database with required extensions
- request a Windows VM (configured as a BAS workstation) with QGIS LTS installed to act as a reference VM
- request a LDAP entity to use for managing application LDAP groups
- request LDAP groups as needed for implementing application permissions

## Infrastructure

### Staging (Cambridge)

Used for pre-release testing and experimentation.

- [app server 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=rhe6qd7w46i5hrs42jhwtbnpuq&h=magic.1password.eu)
- [database 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=wmpfl7kynx63yd3yzx2dyam7y4&h=magic.1password.eu)

See [MAGIC/ops-data-store#39 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/39) for initial setup.

### Azure App Registrations

- [BAS Operations Data Store 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=27ra54r3yrhogzesxdpw2iuybu&h=magic.1password.eu)


### LDAP servers

- [BAS Cambridge (Production) 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=27ra54r3yrhogzesxdpw2iuybu&h=magic.1password.eu)

### Reference VM

Used to simulate a GIS workstation used by Operations and act as a known working example for debugging and testing.

- [Windows VM 🔒](https://start.1password.com/open/i?a=QSB6V7TUNVEOPPPWR6G7S2ARJ4&v=ffy5l25mjdv577qj6izuk6lo4m&i=mb2mfbk66zrowd4kcj3kjc5tdy&h=magic.1password.eu)

## Development

### Local development environment

Check out project:

```
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store.git
$ cd ops-data-store
```

**Note:** If you do not have access to the BAS GitLab instance, clone from GitHub as a read-only copy instead.

[Poetry](https://python-poetry.org/docs/#installation) is used for managing the Python environment and dependencies.

[pyenv](https://github.com/pyenv/pyenv) is strongly recommended to ensure the Python version is the same as the one
used in externally provisioned environments. This is currently *3.9.18*.

```
$ pyenv install 3.9.18
$ pyenv local 3.9.18
$ poetry install
```

Two [Postgres](https://www.postgresql.org) databases on a host running or accessible locally with the required
extensions available are required (one for local development and one for testing).

For example, if a Postgres instance is running locally with trust based authentication for the local user:

```
$ psql -d postgres -c "CREATE DATABASE ops_data_store_dev;"
$ psql -d postgres -c "COMMENT ON DATABASE ops_data_store_dev IS 'Ops Data Store local development DB'";
$ psql -d postgres -c "CREATE DATABASE ops_data_store_test;"
$ psql -d postgres -c "COMMENT ON DATABASE ops_data_store_test IS 'Ops Data Store local development testing DB'"
```

It's strongly recommended to set required configuration options using a `.env` file based off the
[`.example.env`](/.example.env) file as a reference.

A `.test.env` file MUST be created as per the [Testing Configuration](#test-config) section.

Setup the database and load the [Test Schemas and Data](#test-schemas-and-data):

```
$ poetry run ops-ctl db setup
$ poetry run ops-ctl db run --input-path tests/resources/test-schemas.sql
$ poetry run ops-ctl db run --input-path tests/resources/test-data.sql
```

The QGIS profile used for testing needs [downloading 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/packages/)
from GitLab package registry (as it's too large to sensibly store in Git).

Once downloaded, extract and rename to `ops-data-store`. Then copy to the relevant QGIS profile directory:

- macOS: `~/Library/Application\ Support/QGIS/QGIS3/profiles/`
- Windows: `%APPDATA%\Roaming\QGIS\QGIS3\profiles/`

### Running control CLI locally

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
- configuration options should be defined in the common [`Config`](/src/ops_data_store/config.py) class and this README
- configuration options should be read using the relevant [environs](https://github.com/sloria/environs) helper method
- use logging to record how actions progress, using the `app` logger (e.g. `logger = logging.getLogger('app')`)

### Python dependency vulnerability checks

The [Safety](https://pypi.org/project/safety/) package is used to check dependencies against known vulnerabilities.

**WARNING!** As with all security tools, Safety is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this is using the free vulnerability database, which is updated less frequently than paid options.

Checks are run automatically in [Continuous Integration](#continuous-integration). To check locally:

```
$ poetry run safety check --full-report
```

### Python static security analysis

Ruff is configured to run [Bandit](https://github.com/PyCQA/bandit), a static analysis tool for Python.

**WARNING!** As with all security tools, Bandit is an aid for spotting common mistakes, not a guarantee of secure code.
In particular this tool can't check for issues that are only be detectable when running code.

### Python linting

[Ruff](https://docs.astral.sh/ruff/) is used to lint Python files. Specific checks and config options are set in
`pyproject.toml`. Linting checks are run automatically in [Continuous Integration](#continuous-integration). To check
locally:

```
$ poetry run ruff src/
```

### Database

If using a local Postgres database installed through homebrew (where `@14` is the version installed):

- to manage the service: `brew services [command] postgresql@14`
- to view logs: `/usr/local/var/log/postgresql@14.log`

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
database. This file requires creating from the [`.example.env`](/.example.env) reference file.

### Test schemas and data

A set of static datasets are defined for testing. These datasets are based on real [Datasets](#datasets) but sanitised
to remove any sensitive information. To support repeatable testing these datasets do not change.

See [`test-schemas.sql`](tests/resources/test-schemas.sql) for the structure of each dataset and
[`test-data.sql`](tests/resources/test-data.sql) for related seed data (4 features for each).

**Note:** This data is not yet representative. For details see
[https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/48 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/48).

#### Running tests

Tests and coverage checks are run automatically in [Continuous Integration](#continuous-integration). To check
locally:

```
poetry run pytest --strict-markers --random-order --cov --cov-report=html tests
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

To create a release, create an issue using the *release* issue template and follow it's steps.

## Feedback

This project is maintained by the BAS Mapping and Geographic Information Centre
([MAGIC](https://bas.ac.uk/teams/magic)), contactable at: [magic@bas.ac.uk](mailto:magic@bas.ac.uk).

## License

Copyright (c) 2023 UK Research and Innovation (UKRI), British Antarctic Survey.

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
