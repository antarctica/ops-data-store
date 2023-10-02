from importlib.metadata import version
from os import environ

from dotenv import load_dotenv


def _get_env(env: str) -> str:
    """
    Get value from environment variables.

    Util method to corrects for double wrapped (e.g. '"Foo"') values and/or values with leading or trailing whitespace.
    Needed due to the way we override settings using an additional .env file for testing.
    """
    return environ.get(env).replace('"', "").strip()


class Config:
    """Application configuration."""

    def __init__(self) -> None:
        """Create Config instance and load options from dotenv file."""
        load_dotenv()

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
        return _get_env("APP_ODS_DB_DSN")
