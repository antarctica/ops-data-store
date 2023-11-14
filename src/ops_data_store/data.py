import logging
from pathlib import Path

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

from ops_data_store.config import Config
from ops_data_store.db import DBClient


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

        self.export_tables: list[str] = self.config.DATA_MANAGED_TABLE_NAMES + self.config.DATA_QGIS_TABLE_NAMES

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

        :type path: Path
        :param path: Where to save dump file.
        """
        self.logger.info("Exporting datasets to GeoPackage via GDAL/OGR.")
        self.logger.info("Export path: %s", path.resolve())
        self.logger.info("Export tables: %s", self.export_tables)
        if path.exists():
            self.logger.info("Export path exists and will be overwritten.")

        source = GDALOpenDataSource(f"PG:{self.config.DB_DSN}", GDAL_OUTPUT_FORMAT_VECTOR)
        target = str(path.resolve())

        for table_name in self.export_tables:
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
                        SQLStatement=f"SELECT * FROM {table_name};",  # noqa: S608
                        accessMode=access_mode,
                    ),
                )
            except RuntimeError as e:
                self.logger.error(e, exc_info=True)
                msg = "GDAL export failed."
                raise RuntimeError(msg) from e

        self.logger.info("Export ok.")
