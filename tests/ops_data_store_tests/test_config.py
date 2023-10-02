from importlib.metadata import version

from ops_data_store.config import Config


class TestCli:
    """Tests for app config."""

    def test_config(self, fx_test_config: Config) -> None:
        """Type check."""
        assert isinstance(fx_test_config, Config)

    def test_config_version(self, fx_test_config: Config) -> None:
        """`VERSION` property check."""
        assert version("ops-data-store") == fx_test_config.VERSION

    def test_config_dump(self, fx_test_config: Config) -> None:
        """Config can be dumped to a dict."""
        expected = {"VERSION": version("ops-data-store")}
        assert fx_test_config.dump() == expected
