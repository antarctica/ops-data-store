from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from psycopg import ProgrammingError
from pytest_mock import MockerFixture
from typer.testing import CliRunner

from ops_data_store.cli import app as cli
from ops_data_store.config import Config


class TestCliDBCheck:
    """Tests for `db check`."""

    def test_ok(self, fx_cli_runner: CliRunner) -> None:
        """Succeeds when DB is reachable."""
        result = fx_cli_runner.invoke(app=cli, args=["db", "check"])

        assert result.exit_code == 0
        assert "Ok. Database connection successful." in result.output

    def test_fail(self, mocker: MockerFixture, fx_cli_runner: CliRunner) -> None:
        """Aborts when DB is not reachable."""
        mocker.patch("ops_data_store.cli.db.DBClient.check", side_effect=RuntimeError("Error"))

        result = fx_cli_runner.invoke(app=cli, args=["db", "check"])

        assert result.exit_code == 1
        assert "No. Database connection failed." in result.output


class TestCliDBSetup:
    """Tests for `db setup`."""

    def test_ok(self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Succeeds when DB is reachable."""
        mocker.patch("ops_data_store.cli.db.DBClient.setup", return_value=None)

        result = fx_cli_runner.invoke(app=cli, args=["db", "setup"])

        assert result.exit_code == 0
        assert "Ok. Database setup completed normally." in result.output

    def test_fail(self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Fails when error occurs."""
        mocker.patch("ops_data_store.cli.db.DBClient.setup", side_effect=RuntimeError("Error"))

        result = fx_cli_runner.invoke(app=cli, args=["db", "setup"])

        assert result.exit_code == 1
        assert "No. Database setup failed." in result.output


class TestCliDBRun:
    """Tests for `db run`."""

    def test_input_file_not_exist(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Aborts when input file does not exist."""
        fake_path = "/fake/path"

        result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", fake_path])

        assert "Loading file contents and running inside database." in caplog.text
        assert "Input path not found." in caplog.text

        assert result.exit_code == 1
        assert f"No. Input path '{fake_path}' does not exist." in result.output

    def test_input_file_is_dir(self, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Aborts when input file is really a directory."""
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", tmp_dir])

            assert "Loading file contents and running inside database." in caplog.text
            assert "Input path not a file." in caplog.text

            assert result.exit_code == 1
            assert f"No. Input path '{tmp_dir.resolve()}' is not a file." in result.output

    def test_ok(
        self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, fx_test_config: Config
    ):
        """Executes contents of input file against DB."""
        mocker.patch("ops_data_store.cli.db.DBClient.execute", return_value=None)

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

            assert "Loading file contents and running inside database." in caplog.text
            assert "Input file loaded and executed normally." in caplog.text

            assert result.exit_code == 0
            assert f"Executing SQL from input file at '{tmp_file_path.resolve()}'" in result.output
            assert "Complete." in result.output

    def test_error(
        self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner, fx_test_config: Config
    ):
        """Invalid input file gives error."""
        mocker.patch("ops_data_store.cli.db.DBClient.check", side_effect=ProgrammingError())

        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)
            tmp_file.write(
                """
            INVALID;
            """
            )
            tmp_file.flush()

            result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", tmp_file_path])

            assert "Loading file contents and running inside database." in caplog.text
            assert 'syntax error at or near "INVALID"' in caplog.text

            assert result.exit_code == 1
            assert f"Executing SQL from input file at '{tmp_file_path.resolve()}'" in result.output
            assert "No. Error running commands in input file." in result.output


class TestCliDBBackup:
    """Tests for `db backup`."""

    def test_ok(self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Dumps database."""
        mocker.patch("ops_data_store.cli.db.DBClient.dump", return_value=None)

        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)

            result = fx_cli_runner.invoke(app=cli, args=["db", "backup", "--output-path", tmp_file_path])

            assert "Saving app database to file." in caplog.text
            assert "App database saved to file normally." in caplog.text

            assert result.exit_code == 0
            assert "Ok. Complete." in result.output

    def test_error(self, mocker: MockerFixture, caplog: pytest.LogCaptureFixture, fx_cli_runner: CliRunner) -> None:
        """Displays error."""
        mocker.patch("ops_data_store.cli.db.DBClient.dump", side_effect=RuntimeError("Error"))

        with NamedTemporaryFile(mode="w") as tmp_file:
            tmp_file_path = Path(tmp_file.name)

            result = fx_cli_runner.invoke(app=cli, args=["db", "backup", "--output-path", tmp_file_path])

            assert "Saving app database to file." in caplog.text

            assert result.exit_code == 1
            assert "No. Error saving database." in result.output
