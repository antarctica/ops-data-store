from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import psycopg
import pytest
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli
from ops_data_store.config import Config


class TestCliDBCheck:
    """Tests for `db check` CLI command."""

    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Succeeds when DB is reachable."""
        result = fx_cli_runner.invoke(app=cli, args=["db", "check"])

        assert "Checking DB connectivity." in caplog.text
        assert "DB connectivity ok." in caplog.text

        assert result.exit_code == 0
        assert "Ok. DB connection successful." in result.output

    def test_db_not_reachable(
        self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, mocker: MockerFixture
    ) -> None:
        """Aborts when DB is not reachable."""
        mock_db_dsn = mocker.PropertyMock(return_value="invalid")
        mocker.patch.object(target=Config, attribute="DB_DSN", new_callable=mock_db_dsn)

        result = fx_cli_runner.invoke(app=cli, args=["db", "check"])

        assert "Checking DB connectivity." in caplog.text
        assert 'OperationalError: missing "=" after "invalid" in connection info string' in caplog.text

        assert result.exit_code == 1
        assert "No. DB connection failed." in result.output


class TestCliDBSetup:
    """Tests for `db setup` CLI command."""

    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner):
        """Creates any missing DB extensions or functions."""
        result = fx_cli_runner.invoke(app=cli, args=["db", "setup"])

        assert "Required DB extension 'postgis' ok." in caplog.text
        assert "Required DB extension 'pgcrypto' ok." in caplog.text
        assert "Required DB extension 'fuzzystrmatch' ok." in caplog.text
        assert "Required DB function 'generate_ulid' ok." in caplog.text
        assert "Required DB function 'geom_as_ddm' ok." in caplog.text
        assert "Required DB data type 'ddm_point' ok." in caplog.text
        assert "Database setup complete." in caplog.text

        assert result.exit_code == 0
        assert "Setting up database for first time use." in result.output
        assert "Complete." in result.output


class TestCliDBRun:
    """Tests for `db run` CLI command."""

    def test_input_file_not_exist(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Aborts when input file does not exist."""
        fake_path = "/fake/path"

        result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", fake_path])

        assert "Loading file contents and running inside DB." in caplog.text
        assert "Input path not found." in caplog.text

        assert result.exit_code == 1
        assert f"No. Input path '{fake_path}' does not exist." in result.output

    def test_input_file_is_dir(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Aborts when input file is really a directory."""
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", tmp_dir])

            assert "Loading file contents and running inside DB." in caplog.text
            assert "Input path not a file." in caplog.text

            assert result.exit_code == 1
            assert f"No. Input path '{tmp_dir.resolve()}' is not a file." in result.output

    def test_ok(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, fx_test_config: Config):
        """Executes contents of input file against DB."""
        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)
            tmp_file.write(
                """
            CREATE TABLE test (
                id serial PRIMARY KEY,
                name text
            );
            INSERT INTO test (name) VALUES ('test');
            """
            )
            tmp_file.flush()

            result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", tmp_file_path])

            assert "Loading file contents and running inside DB." in caplog.text
            assert "Input file loaded and executed successfully." in caplog.text

            assert result.exit_code == 0
            assert f"Executing SQL from input file at '{tmp_file_path.resolve()}'" in result.output
            assert "Complete." in result.output

            with psycopg.connect(fx_test_config.DB_DSN) as conn, conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test;")
                assert cur.fetchone()[0] == 1

                cur.execute("DROP TABLE IF EXISTS test;")

    def test_error(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, fx_test_config: Config):
        """Invalid input file gives error."""
        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)
            tmp_file.write(
                """
            INVALID;
            """
            )
            tmp_file.flush()

            result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", tmp_file_path])

            assert "Loading file contents and running inside DB." in caplog.text
            assert 'syntax error at or near "INVALID"' in caplog.text

            assert result.exit_code == 1
            assert f"Executing SQL from input file at '{tmp_file_path.resolve()}'" in result.output
            assert "No. Error running commands in input file." in result.output
