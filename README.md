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

### Related projects

This project is limited to the technical and operational aspects of providing a platform for hosting datasets. Other
projects focus on these datasets and other aspects of a providing a wider Geographic Information System (GIS).

* [BAS Field Operations Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/operations/field-operations-gis-data)
* [BAS Air Unit Network Data 🛡](https://gitlab.data.bas.ac.uk/MAGIC/air-unit-network-dataset)

This project is an evolution of an earlier [Experiment 🛡](https://gitlab.data.bas.ac.uk/felnne/ops-data-store-exp).

## Usage

### End-user documentation

End-users should consult the documentation developed for the wider
[Field Operations GIS Platform 🛡](https://app.gitbook.com/o/-MbhSFJ1AEZxhIfX9tgr/s/HmSXoUpviCA3XCta5MDr/), as this
specific project is not aimed at end-users directly.

## Development

### Local development environment

Check out project:

```shell
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store.git
$ cd ops-data-store
```

**Note:** If you do not have access to the BAS GitLab instance, clone from GitHub as a read-only copy instead.

#### Python

[Poetry](https://python-poetry.org/docs/#installation) is used for managing the Python environment and dependencies.

It's strongly recommended to use the same Python version that will be used when deployed. This is currently *3.9.x*.
It's recommended to use [pyenv](https://github.com/pyenv/pyenv) to install and use a suitable version:

```shell
$ pyenv install 3.9.x
$ pyenv local 3.9.x
$ poetry install
```

### Contribution workflow

All code changes should be:

- made using a merge request associated with an issue in the project's
  [Issue Tracker 🛡](https://gitlab.data.bas.ac.uk/MAGIC/ops-data-store/-/issues)
- summarised in the [Change log](./CHANGELOG.md)

### Editorconfig

For consistency is strongly recommended to configure your IDE or other editor to use the [EditorConfig](https://EditorConfig.org) settings defined in [`.editorconfig`](.editorconfig).

## Release procedure

1. create a release issue and merge request using the *release* issue template

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
