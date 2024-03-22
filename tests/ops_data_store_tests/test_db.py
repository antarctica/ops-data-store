from pathlib import Path
from subprocess import CalledProcessError
from unittest.mock import MagicMock

import psycopg
import pytest
from psycopg import ProgrammingError
from psycopg.sql import SQL
from pytest_mock import MockFixture

from ops_data_store.db import DBClient
from ops_data_store.db import Path as DBClientPath


class TestDBClient:
    """Tests for app DB client."""

    def test_init(self, caplog: pytest.LogCaptureFixture) -> None:
        """Can be initialised."""
        client = DBClient()

        assert "Creating DB client." in caplog.text

        assert isinstance(client, DBClient)

    def test_check_ok(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Check succeeds."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.execute.return_value = (1,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        client.check()

        assert "Creating DB client." in caplog.text
        assert "DB connection ok." in caplog.text

    def test_check_fail(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Failed raises error."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.execute.side_effect = ProgrammingError
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        assert "Creating DB client." in caplog.text

        with pytest.raises(RuntimeError, match="DB connection failed."):
            client.check()

    def test_setup_ok(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Setup succeeds."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchone.return_value = (1,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        client.setup()

        assert "Setting up required database objects." in caplog.text
        assert "Setting up required DB extension 'postgis'." in caplog.text
        assert "Setting up required DB data type 'ddm_point'." in caplog.text
        assert "Setting up required DB function 'generate_ulid'." in caplog.text

    def test_setup_extensions_fails(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Failed extensions setup raises error."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchone.return_value = (0,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        with pytest.raises(RuntimeError, match="No. Required extension 'postgis' not found."):  # noqa: SIM117
            with psycopg.connect("") as conn, conn.cursor() as cur:
                client._setup_extensions(cur=cur)

    def test_setup_data_types_fails(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Failed data types setup raises error."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchone.return_value = (0,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        with pytest.raises(RuntimeError, match="No. Required data type 'ddm_point' not found."):  # noqa: SIM117
            with psycopg.connect("") as conn, conn.cursor() as cur:
                client._setup_types(cur=cur)

    def test_setup_functions_fails(self, caplog: pytest.LogCaptureFixture, mocker: MockFixture) -> None:
        """Failed functions setup raises error."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.fetchone.return_value = (0,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        with pytest.raises(RuntimeError, match="No. Required function 'generate_ulid' not found."):  # noqa: SIM117
            with psycopg.connect("") as conn, conn.cursor() as cur:
                client._setup_functions(cur=cur)

    def test_int_setup_ok(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        Setup succeeds (Integration test).

        Connects to real database to address #124, #125.
        """
        client = DBClient()

        client.setup()

        assert "Setting up required database objects." in caplog.text
        assert "Setting up required DB extension 'postgis'." in caplog.text
        assert "Setting up required DB data type 'ddm_point'." in caplog.text
        assert "Setting up required DB function 'generate_ulid'." in caplog.text

    def test_execute(self, mocker: MockFixture):
        """Execute succeeds."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.execute.return_value = None
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        client.execute(query="SELECT 1;")

    def test_dump_ok(self, mocker: MockFixture, caplog: pytest.LogCaptureFixture):
        """Dump succeeds."""
        mocker.patch("subprocess.run")
        mocker.patch.object(DBClientPath, "open", mocker.mock_open())

        client = DBClient()

        # mock needs to be localised to prevent issues loading config from `.env` files
        client.dump(path=Path("/x.sql"))

        assert "Dumping database via `pg_dump`." in caplog.text
        assert "DB dump ok." in caplog.text

    def test_dump_fail(self, mocker: MockFixture, caplog: pytest.LogCaptureFixture):
        """Failed dump raises error."""
        mocker.patch("subprocess.run", side_effect=CalledProcessError(returncode=1, cmd="x"))

        client = DBClient()

        with pytest.raises(RuntimeError, match="DB dump failed."):
            client.dump(path=Path("/x.sql"))

        assert "Dumping database via `pg_dump`." in caplog.text

    def test_fetch_ok(self, mocker: MockFixture, caplog: pytest.LogCaptureFixture) -> None:
        """Fetch succeeds."""
        mock_cursor = MagicMock()
        mock_cursor.__enter__.return_value.execute.return_value = (1,)
        mock_conn = MagicMock()
        mock_conn.__enter__.return_value.cursor.return_value = mock_cursor
        mocker.patch("psycopg.connect", return_value=mock_conn)

        client = DBClient()

        # noinspection PyTypeChecker
        client.fetch(query=SQL("SELECT 1;"))

        assert "Fetching from database." in caplog.text
