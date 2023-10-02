from ops_data_store.config import Config


class TestCli:
    """Tests for app config."""

    def test_config(self, fx_test_config: Config) -> None:
        """Type check."""
        assert isinstance(fx_test_config, Config)

    def test_config_version(self, fx_test_package_version: str, fx_test_config: Config) -> None:
        """`VERSION` property check."""
        assert fx_test_package_version == fx_test_config.VERSION

    def test_config_db_dsn(self, fx_test_config: Config, fx_test_db_dsn: str) -> None:
        """`DB_DSN` property check."""
        assert fx_test_db_dsn == fx_test_config.DB_DSN

    def test_config_dump(self, fx_test_config: Config, fx_test_package_version: str, fx_test_db_dsn: str) -> None:
        """Config can be dumped to a dict."""
        expected = {"VERSION": fx_test_package_version, "DB_DSN": fx_test_db_dsn}
        assert fx_test_config.dump() == expected
