from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory

import psycopg
from typer.testing import CliRunner

from ops_data_store.cli import app as cli
from ops_data_store.config import Config


class TestCliDBRun:
    """Tests for `db run` CLI command."""

    def test_input_file_not_exist(self, fx_cli_runner: CliRunner) -> None:
        """Aborts when input file does not exist."""
        fake_path = "/fake/path"

        result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", fake_path])

        assert result.exit_code == 1
        assert f"No. Input path '{fake_path}' does not exist." in result.output

    def test_input_file_is_dir(self, fx_cli_runner: CliRunner) -> None:
        """Aborts when input file is really a directory."""
        with TemporaryDirectory() as tmp_dir:
            tmp_dir = Path(tmp_dir)
            result = fx_cli_runner.invoke(app=cli, args=["db", "run", "--input-path", tmp_dir])

            assert result.exit_code == 1
            assert f"No. Input path '{tmp_dir.resolve()}' is not a file." in result.output

    def test_ok(self, fx_cli_runner: CliRunner, fx_test_config: Config):
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

            assert result.exit_code == 0
            assert f"Executing SQL from input file at '{tmp_file_path.resolve()}'" in result.output
            assert "Complete." in result.output

            with psycopg.connect(fx_test_config.DB_DSN) as conn, conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM test;")
                assert cur.fetchone()[0] == 1

                cur.execute("DROP TABLE IF EXISTS test;")
