import logging

import pytest

import ops_data_store


class TestLogging:
    """Tests for application logging."""

    def test_logging(self, caplog: pytest.LogCaptureFixture):
        """Logging works."""
        caplog.set_level(logging.INFO)
        ops_data_store.logging.init()

        logger = logging.getLogger("app")
        logger.info("test log message")

        assert "test log message" in caplog.text
