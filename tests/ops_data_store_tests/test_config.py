from os import environ

import pytest
from environs import EnvError

from ops_data_store.config import Config


class TestConfig:
    """Tests for app config base class and methods."""

    def test_type(self, fx_test_config: Config) -> None:
        """Type check."""
        assert isinstance(fx_test_config, Config)

    def test_dump(self, fx_test_config: Config, fx_test_package_version: str, fx_test_db_dsn: str) -> None:
        """Config can be dumped to a dict."""
        expected = {"VERSION": fx_test_package_version, "DB_DSN": fx_test_db_dsn}
        assert fx_test_config.dump() == expected

    def test_validate_ok(self, fx_test_config: Config) -> None:
        """Config can be validated."""
        fx_test_config.validate()

        assert True


class TestConfigVersion:
    """Tests for `VERSION` property in app config."""

    def test_ok(self, fx_test_package_version: str, fx_test_config: Config) -> None:
        """Property can be read."""
        assert fx_test_package_version == fx_test_config.VERSION


class TestConfigDbDsn:
    """Tests for `DB_DSN` property in app config."""

    def test_ok(self, fx_test_config: Config, fx_test_db_dsn: str) -> None:
        """Property check."""
        assert fx_test_db_dsn == fx_test_config.DB_DSN

    def test_missing(self, fx_test_config: Config) -> None:
        """Missing property raises exception."""
        db_dsn = environ["APP_ODS_DB_DSN"]
        del environ["APP_ODS_DB_DSN"]

        with pytest.raises(EnvError):
            # noinspection PyStatementEffect
            fx_test_config.DB_DSN  # noqa: B018

        environ["APP_ODS_DB_DSN"] = db_dsn

    def test_validate_error(self, fx_test_config: Config) -> None:
        """Missing `DB_DSN` property fails validation."""
        db_dsn = environ["APP_ODS_DB_DSN"]
        del environ["APP_ODS_DB_DSN"]

        # assert validate method returns RuntimeError and message is 'foo'
        with pytest.raises(RuntimeError) as e:
            fx_test_config.validate()

        assert str(e.value) == "Required config option `DB_DSN` not set."

        environ["APP_ODS_DB_DSN"] = db_dsn
