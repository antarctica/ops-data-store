# Operations Data Store - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Wherever possible, a reference to an issue in the project issue tracker should be included to give additional context.

## [Unreleased]

### Added

* EO Acquisition script AOIs controlled dataset
  [#212](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/212)
  [#217](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/217)
* warning that QGIS Layer Styles could leak the name and attributes of possibly sensitive layers
  [#196](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/196)

## [0.9.2] - 2024-06-10

### Fixed

* Permissions for QGIS layer styles ID sequence
  [#221](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/221)

## [0.9.1] - 2024-04-18

### Fixed

* Unqualified table references in air unit conversion methods
  [#208](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/208)

## [0.9.0] - 2024-04-17

### Added

* Database grants/permissions documentation and reference file
  [#153](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/153)
* Information for Cambridge production instance
  [#170](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170)
* Troubleshooting steps for broken GeoPackage backup
  [#179](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/179)
* App secret rotation instructions (as part of setting up Cambridge production instance)
  [#170](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170)
* Documentation for altering structure of an existing dataset
  [#185](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/185)
* Documentation on file quotas
  [#183](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/183)
* Support for unmanaged/uncontrolled/planning datasets
  [#200](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/200)

### Fixed

* Corrected geometry column registration for managed route view
  [#146](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/146)
* Corrected layer styles in GeoPackage backups
  [#160](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/160)
* Updating thresholds for automatic Air Unit conversion Sentry monitoring
  [#164](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/164)
* Clarifying the staging instance is for Rothera not Cambridge
  [#176](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/176)
* Preventing stuck backup files stopping future backups
  [#181](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/181)

### Changed

* Logging level raised to info
  [#150](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/150)
* Postgres DB service moved to `test` CI job rather than running for all
  [#163](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/163)
* Improving backup documentation (as part of setting up Cambridge production instance)
  [#170](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/170)
* Updated dependencies
  [#190](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/190)
* Updated to Safety 3.x for Python vulnerabilities
  [#178](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/178)
* switching `updated_by` trigger to use `SESSION_USER` in preparation for using `SET ROLE` for inheriting permissions
  [#175](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/175)
* refactor `public` schema to `magic_managed` in preparation for supporting non-MAGIC managed datasets
  [#174](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/174)
* refactor database and GeoPackage backups to target MAGIC managed datasets and QGIS layer styles only
  [#169](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/169)
* refactor `magic_managed` into `controlled` as per #199
  [#200](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/200)

## [0.8.0] - 2023-12-13

### Added

* Support for syncing multiple Azure groups to an LDAP group via `auth sync` command
  [#151](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/151)
* Various documentation improvements
  [#161](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/161)

### Fixed

* Empty Air Unit network exports due to missing `fetch()` call
  [#157](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/157)
* Previous Air Unit outputs were incorrectly retained
  [#156](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/156)

### Removed

* Duplicate, inconsistent parameter documentation from doc-blocks
  [#152](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/152)

## [0.7.0] - 2023-12-05

### Added

* Automated backups via cron with Sentry monitoring
  [#41](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/41)
* Documentation improvements based on production setup
  [#128](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/128)
* Documentation for creating/updating/removing QGIS layer styles as underlying tables are added/modified/removed
  [#136](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/136)
* Documenting BAS IT LDAP and DB sync process
  [#98](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/98),
  [#106](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/106)
* Basic documentation on BAS IT VM backups
  [#100](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/100)
* Integrating Air Unit Network Utility for managing Air Unit network datasets
  [#139](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/139),
  [#140](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/140)

### Fixed

* Adding missing unique constraint for platform identifiers (`pid`)
  [#144](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/144)
* GDAL version issue
  [#126](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/126)

### Changed

* Updating documentation diagrams
  [#123](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/123)

## [0.6.1] - 2023-11-21

### Fixed

* Incorrect quoting of type names in DB client setup functions
  [#124](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/124)

## [0.6.0] - 2023-11-14

### Added

* Deployment issue template
  [#97](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/97)
* Architecture and infrastructure diagrams in documentation
  [#81](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/81)
* `db backup` CLI command and `dump` command in app DB client running `pg_dump`
  [#93](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/93)
* `data backup` CLI command and app data client using GDAL
  [#108](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/108)
* Initial implementation of a rolling file set, for keeping a fixed number of iterations of a file
  [#92](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/92)

### Fixed

* Including timestamp in DB client dumps to workaround backups only tracking by file checksum
  [#115](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/115)

### Changed

* Refactoring CLI modules into a single package, rather than by CLI group
  [#72](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/72)
* Refactoring database functions from CLI module to database client class
  [#71](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/71)
* Minor refactoring of Azure auth client
  [#109](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/109)
* Refactoring LDAP auth client
  [#110](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/110)
* Switching to `ruff format` for Python code formatting (echo's Black style)
  [#114](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/114)
* Incorporate depot and instrument managed dataset schema changes
  [#68](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/68)

## [0.5.0] - 2023-11-01

### Added

* `auth check` CLI command
  [#38](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/38)
* `auth sync` CLI command
  [#76](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/76),
  [#77](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/77),
  [#78](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/78),
  [#83](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/83),
  [#84](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/84),
  [#85](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/85),
  [#86](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/86),
  [#87](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/87),
  [#88](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/88),
  [#89](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/89)

### Fixed

* Ensuring default value for `updated_by` column is real user
  [#65](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/65)
* Issue connecting to BAS production LDAP server
  [#75](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/75)
* Order or removing and adding members in LDAP groups to prevent leaving groups empty
  [#94](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/94)

### Changed

* Improving config handling for overriding values when testing
  [#73](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/73)

### Removed

* Flawed/il-defined entity tags concept
  [#66](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/66)

## [0.4.0] - 2023-10-14

### Added

* `updated_at`, `updated_by` fields to managed datasets
  [#59](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/59)
* Instructions for adding new managed datasets
  [#62](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/62)
* Documentation for etags
  [#61](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/61)
* Documentation for layer styles
  [#58](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/58)
* Documentation on Cambridge staging instance
  [#26](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/26)
* Real implementations for Depot and Instrument datasets
  [#48](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/48)

## [0.3.0] - 2023-10-13

### Added

* `db setup` CLI command
  [#33](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/33)
* Postgres function for formatting coordinates in DDM format
  [#46](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/46)
* Documentation on required/expected dataset identifiers
  [#36](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/36)
* Placeholder schemas and seed data for depot and instrument managed datasets
  [#34](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/34)
* `config check` CLI command
  [#56](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/56)

### Fixed

* Adding requirement/checks for 'fuzzystrmatch' Postgres extension
  [#47](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/47)
* Documenting how the dotenv module searches for `.env` files
  [#57](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/57)
* Handling missing `DB_DSN` value
  [#55](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/55)

## [0.2.0] - 2023-10-04

### Added

* note in release issue template to add link to README in each release
  [#15](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/15)
* `config show` CLI command
  [#18](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/18)
* documentation and tests for the config class
  [#20](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/20)
* application database and CLI command to run commands from SQL files
  [#16](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/16)
* `db check` CLI command
  [#22](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/22)

### Fixed

* CI job rules
  [#24](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/24)

### Changed

* Python package should only be published on tagged releases
  [#14](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/14)
* Documenting IT Python version
  [#4](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/4)
* Documenting and including IT GDAL version
  [#5](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/5)

## [0.1.0] - 2023-10-01

### Added

- Initial project documentation
  [#1](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/1)
- Initial Python package
  [#3](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/3)
- Initial control CLI
  [#6](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/6)
- Python linting, formatting and vulnerability tools
  [#7](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/7)
- Python tests and coverage checks
  [#10](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/10)
