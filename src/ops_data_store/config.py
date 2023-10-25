from importlib.metadata import version

from environs import Env, EnvError


class Config:
    """Application configuration."""

    def __init__(self) -> None:
        """
        Create Config instance and load options from possible dotenv file.

        To support application tests which may need to manipulate options, such as the application database, variables
        loaded from a possible `.env` file, or that are set as environment variables directly, will be overriden by any
        variables set in a possible `.test.env` file.
        """
        self.env = Env()
        self.env.read_env()
        self.env.read_env(".test.env", override=True)

    def validate(self) -> None:
        """Validate required configuration options have valid values."""
        try:
            self.env.str("APP_ODS_DB_DSN")
        except EnvError as e:
            msg = "Required config option `DB_DSN` not set."
            raise RuntimeError(msg) from e

    def dump(self) -> dict:
        """Return application configuration as a dictionary."""
        return {"VERSION": self.VERSION, "DB_DSN": self.DB_DSN}

    @property
    def VERSION(self) -> str:
        """Application version."""
        return version("ops-data-store")

    @property
    def DB_DSN(self) -> str:
        """DB connection string."""
        return self.env.str("APP_ODS_DB_DSN")
