from importlib.metadata import version

from dotenv import load_dotenv


class Config:
    """Application configuration."""

    def __init__(self) -> None:
        """Create Config instance and load options from dotenv file."""
        load_dotenv()

    def dump(self) -> dict:
        """Return application configuration as a dictionary."""
        return {"VERSION": self.VERSION}

    @property
    def VERSION(self) -> str:
        """Application version."""
        return version("ops-data-store")
