from importlib.metadata import version

import pytest
from environs import Env
from typer.testing import CliRunner

from ops_data_store.config import Config


@pytest.fixture()
def fx_test_config() -> Config:
    """Provide access to app configuration."""
    return Config()


@pytest.fixture()
def fx_cli_runner() -> CliRunner:
    """CLI testing fixture."""
    return CliRunner()


@pytest.fixture()
def fx_test_package_version() -> str:
    """Package version configured in `pyproject.toml`."""
    return version("ops-data-store")


@pytest.fixture()
def fx_test_db_dsn() -> str:
    """DB Connection string configured in `.test.env`."""
    env = Env()
    env.read_env()
    env.read_env(".test.env", override=True)
    return env.str("APP_ODS_DB_DSN")
