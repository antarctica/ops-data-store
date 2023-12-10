# Operations Data Store - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Wherever possible, a reference to an issue in the project issue tracker should be included to give additional context.

## [Unreleased]

### Added

* Support for syncing multiple Azure groups to an LDAP group via `auth sync` command
  [#151](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues/151)

### Removed

* Duplicate, inconsistent parameter documentation from docblocks
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
* Include Air Unit Network Utility for managing Air Unit network datasets
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

* Python package should only published on tagged releases
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
