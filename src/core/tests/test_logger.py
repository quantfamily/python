import logging

from foreverbull_core import logger

logger.Logger()
log = logging.getLogger("test")


def test_logging_output(caplog):
    log.error("bad things")
    assert "bad things" in caplog.text
