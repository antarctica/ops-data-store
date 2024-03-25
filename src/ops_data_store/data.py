import logging
from pathlib import Path
from sqlite3 import connect as sqlite3_connect

from osgeo.gdal import (
    OF_VECTOR as GDAL_OUTPUT_FORMAT_VECTOR,
)
from osgeo.gdal import (
    OpenEx as GDALOpenDataSource,
)
from osgeo.gdal import (
    UseExceptions as GDALUseExceptions,
)
from osgeo.gdal import (
    VectorTranslate,
    VectorTranslateOptions,
)

from ops_data_store.airnet import AirUnitNetworkClient
from ops_data_store.config import Config
from ops_data_store.db import DBClient
from ops_data_store.utils import empty_dir


class DataClient:
    """
    Application data client.

    A high level abstraction over the database client to manage datasets.
    """

    def __init__(self) -> None:
        """Create instance."""
        self.config = Config()

        self.logger = logging.getLogger("app")
        self.logger.info("Creating data client.")

        GDALUseExceptions()

        self.db_client = DBClient()
        self.airnet_client = AirUnitNetworkClient()

        self._magic_managed_connection = f"PG:{self.config.DB_DSN}"
        self._magic_managed_tables = self.config.DATA_MANAGED_TABLE_NAMES
        self._qgis_styles_table = self.config.DATA_QGIS_TABLE_NAMES[0]
        self.export_tables = [*self._magic_managed_tables, self._qgis_styles_table]

    def export(self, path: Path) -> None:
        """
        Save datasets to GeoPackage.

        Warning: Any existing file at `path` will be overwritten.

        See the `VectorTranslateOptions` class for parameters supported by GDAL/OGR when exporting.

        For database sources, GDAL defines a layer via an SQL query. In our case all data from all columns should be
        included so this query is very simple.

        GDAL uses different access modes for creating new outputs that support multiple layers, in order to control
        whether subsequent layers should replace/overwrite existing layers (if the output exists), or be included as
        additional layers. We always include subsequent layers as additional layers, automatically switching access
        mode as needed (from 'create' for the initial layer to 'update' for additional layers).

        Any QGIS layer styles are also exported, with references updated to remove Postgres schema/catalog references
        so that styles will be automatically loaded in the exported GeoPackage.
        """
        self.logger.info("Exporting datasets to GeoPackage via GDAL/OGR.")
        self.logger.info("Export path: %s", path.resolve())
        self.logger.info("Export tables: %s", self.export_tables)
        if path.exists():
            self.logger.info("Export path exists and will be overwritten.")

        source = GDALOpenDataSource(self._magic_managed_connection, GDAL_OUTPUT_FORMAT_VECTOR)
        target = str(path.resolve())

        for table_name in self._magic_managed_tables:
            access_mode = "update"
            if not path.exists():
                access_mode = None
            self.logger.info("Access mode for layer: %s is: %s.", table_name, access_mode)

            try:
                VectorTranslate(
                    destNameOrDestDS=target,
                    srcDS=source,
                    options=VectorTranslateOptions(
                        format="GPKG",
                        layerName=table_name,
                        SQLStatement=f"SELECT * FROM {self.config.DATA_MANAGED_SCHEMA_NAME}.{table_name};",  # noqa: S608
                        accessMode=access_mode,
                    ),
                )
            except RuntimeError as e:
                self.logger.error(e, exc_info=True)
                msg = "GDAL export failed."
                raise RuntimeError(msg) from e

        access_mode = "update"
        VectorTranslate(
            destNameOrDestDS=target,
            srcDS=source,
            options=VectorTranslateOptions(
                format="GPKG",
                layerName=self._qgis_styles_table,
                SQLStatement=f"SELECT * FROM public.{self._qgis_styles_table};",  # noqa: S608
                accessMode=access_mode,
            ),
        )

        self.logger.info("Fixing layer style references in GeoPackage")
        with sqlite3_connect(path) as conn:
            cur = conn.cursor()
            cur.execute("""UPDATE layer_styles SET f_table_catalog = '', f_table_schema = '';""")

        self.logger.info("Export ok.")

    def convert(self) -> None:
        """
        Convert Air Unit datasets to CSV, GPX and FPL formats.

        Warning: Any existing content within the output path will be removed, and any existing outputs overwritten.
        """
        self.logger.info("Converting Air Unit datasets to output formats.")

        self.logger.info("Clearing output directory.")
        empty_dir(path=self.config.DATA_AIRNET_OUTPUT_PATH)

        self.airnet_client.fetch()
        self.airnet_client.export()

        self.logger.info("Conversion ok.")
