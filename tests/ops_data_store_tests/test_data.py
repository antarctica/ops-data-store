from pathlib import Path
from tempfile import NamedTemporaryFile

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
        """Export succeeds."""
        expected_name = fx_test_data_managed_table_names[0]

        mocker.patch("ops_data_store.data.VectorTranslate", return_value=None)

        fx_data_client.export(path=Path("/x.gpkg"))

        assert "Exporting datasets to GeoPackage via GDAL/OGR." in caplog.text
        assert "Export path: /x.gpkg" in caplog.text
        assert f"Access mode for layer: {expected_name} is: None." in caplog.text
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

        with NamedTemporaryFile(mode="w") as tmp_file:
            fx_data_client.export(path=Path(tmp_file.name))

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
