"""Test fixtures for containerlog proxy tests."""

import datetime
import io
import logging

import pytest

from containerlog.proxy import std


@pytest.fixture()
def reset_logging_manager():
    _m = logging.Logger.manager
    logging.Logger.manager = logging.Manager(logging.root)
    yield
    _m.loggerClass = None
    logging.Logger.manager = _m


@pytest.fixture()
def std_proxy_logger():
    """Fixture to get an instance of a Logger with mocked proxy module functions."""
    err = io.StringIO()
    out = io.StringIO()
    log = std.StdLoggerProxy(name="test")

    log.containerlog.utcnow = lambda: datetime.datetime(2020, 1, 1)
    log.writeout = out.write
    log.writeerr = err.write
    log.err = err
    log.out = out

    yield log

    err.close()
    out.close()
