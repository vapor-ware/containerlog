"""Test fixtures."""

import datetime
import io

import pytest

import containerlog


@pytest.fixture(scope='function', autouse=True)
def reset_manager():
    """Fixture to reset the module Manager after each test."""
    yield
    containerlog.manager = containerlog.Manager()


@pytest.fixture()
def test_logger():
    """Fixture to get an instance of a Logger with mocked proxy module functions."""
    err = io.StringIO()
    out = io.StringIO()
    log = containerlog.Logger(name='test')

    log.utcnow = lambda: datetime.datetime(2020, 1, 1)
    log.writeout = out.write
    log.writeerr = err.write

    yield log, out, err

    err.close()
    out.close()
