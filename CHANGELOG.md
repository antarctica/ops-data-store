# Operations Data Store - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

Wherever possible, a reference to an issue in the project issue tracker should be included to give additional context.

## [Unreleased]

### Fixed

* ensuring default value for `updated_by` column is real user

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
