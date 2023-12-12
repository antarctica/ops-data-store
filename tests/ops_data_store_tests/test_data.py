from os import environ
from pathlib import Path
from sqlite3 import connect as sqlite3_connect
from tempfile import TemporaryDirectory

import pytest
from pytest_mock import MockFixture

from ops_data_store.data import DataClient


class TestDataClient:
    """Tests for app DB client."""

    def test_init(self, caplog: pytest.LogCaptureFixture) -> None:
        """Can be initialised."""
        client = DataClient()

        assert "Creating data client." in caplog.text

        assert isinstance(client, DataClient)

    def test_attribute_export_tables(
        self,
        fx_data_client: DataClient,
        fx_test_data_managed_table_names: list[str],
        fx_test_data_qgis_table_names: list[str],
    ) -> None:
        """`export_tables` attribute includes correct values."""
        expected = fx_test_data_managed_table_names + fx_test_data_qgis_table_names

        assert fx_data_client.export_tables == expected

    def test_export_ok(
        self,
        mocker: MockFixture,
        fx_data_client: DataClient,
        caplog: pytest.LogCaptureFixture,
        fx_test_data_managed_table_names: list[str],
    ):
        """
        Export succeeds.

        This test is currently flawed because we have to fake an existing GPKG file for the layer_styles fixes to work.
        This means there is always an existing file, so we can't test the 'create' (None) access mode.
        """
        expected_name = fx_test_data_managed_table_names[0]

        mocker.patch("ops_data_store.data.VectorTranslate", return_value=None)

        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            gpkg_path = workspace_path.joinpath("x.gpkg")

            # fake a GPKG with relevant table for patching layer styles (must come before `export()` call)
            with sqlite3_connect(gpkg_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS layer_styles (
                        id INTEGER PRIMARY KEY,
                        f_table_catalog TEXT,
                        f_table_schema TEXT
                    );
                    """
                )
                cur.execute(
                    "INSERT INTO layer_styles (f_table_catalog, f_table_schema) VALUES (?, ?);",
                    ("ops-data-store", "public"),
                )

            fx_data_client.export(path=gpkg_path)

        assert "Exporting datasets to GeoPackage via GDAL/OGR." in caplog.text
        assert f"Export path: {gpkg_path.resolve()}" in caplog.text
        assert f"Access mode for layer: {expected_name} is: update." in caplog.text
        assert "Export ok." in caplog.text

    def test_export_ok_exist(
        self,
        mocker: MockFixture,
        fx_data_client: DataClient,
        caplog: pytest.LogCaptureFixture,
        fx_test_data_managed_table_names: list[str],
    ):
        """Export succeeds with existing file."""
        expected_name = fx_test_data_managed_table_names[0]

        mocker.patch("ops_data_store.data.VectorTranslate", return_value=None)

        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            gpkg_path = workspace_path.joinpath("x.gpkg")

            # fake a GPKG with relevant table for patching layer styles (must come before `export()` call)
            with sqlite3_connect(gpkg_path) as conn:
                cur = conn.cursor()
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS layer_styles (
                        id INTEGER PRIMARY KEY,
                        f_table_catalog TEXT,
                        f_table_schema TEXT
                    );"""
                )
                cur.execute(
                    "INSERT INTO layer_styles (f_table_catalog, f_table_schema) VALUES (?, ?);",
                    ("ops-data-store", "public"),
                )

            fx_data_client.export(path=gpkg_path)

        assert "Exporting datasets to GeoPackage via GDAL/OGR." in caplog.text
        assert f"Access mode for layer: {expected_name} is: update." in caplog.text
        assert "Export ok." in caplog.text

    def test_export_fail(
        self,
        mocker: MockFixture,
        fx_data_client: DataClient,
        caplog: pytest.LogCaptureFixture,
    ):
        """Failed export raises error."""
        mocker.patch("ops_data_store.data.VectorTranslate", side_effect=RuntimeError("Error"))

        with pytest.raises(RuntimeError, match="GDAL export failed."):
            fx_data_client.export(path=Path("/x.gpkg"))

        assert "Exporting datasets to GeoPackage via GDAL/OGR." in caplog.text

    def test_convert_ok(
        self,
        mocker: MockFixture,
        fx_data_client: DataClient,
        caplog: pytest.LogCaptureFixture,
    ):
        """Convert succeeds."""
        mocker.patch("ops_data_store.data.AirUnitNetworkClient.fetch", return_value=None)
        mocker.patch("ops_data_store.data.AirUnitNetworkClient.export", return_value=None)

        output_path = environ["APP_ODS_DATA_AIRNET_OUTPUT_PATH"]

        with TemporaryDirectory() as workspace:
            workspace_path = Path(workspace)
            test_file = workspace_path.joinpath("test.txt")
            environ["APP_ODS_DATA_AIRNET_OUTPUT_PATH"] = str(workspace_path)

            # make a test file that will be removed
            test_file.touch()

            fx_data_client.convert()

            assert test_file.exists() is False

        assert "Converting Air Unit datasets to output formats." in caplog.text
        assert "Conversion ok." in caplog.text

        environ["APP_ODS_DATA_AIRNET_OUTPUT_PATH"] = output_path
