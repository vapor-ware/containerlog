"""Unit tests for containerlog."""

import sys
from unittest import mock

import pytest

import containerlog


class TestManager:
    def test_init(self):
        manager = containerlog.Manager()
        assert manager.level == containerlog.DEBUG
        assert len(manager.loggers) == 0

    def test_init_with_level(self):
        manager = containerlog.Manager(level=containerlog.WARN)
        assert manager.level == containerlog.WARN
        assert len(manager.loggers) == 0

    def test_set_levels_no_loggers(self):
        manager = containerlog.Manager(level=containerlog.ERROR)
        logger = containerlog.Logger(name="test", manager=manager)
        manager.set_levels()

        # Verify that the manager level is ERROR
        assert manager.level == containerlog.ERROR

        # Verify that a Logger not registered with the manager
        # did not get the Manager's log level.
        assert logger.level == containerlog.DEBUG

    def test_set_levels_with_loggers(self):
        manager = containerlog.Manager(level=containerlog.ERROR)
        logger = containerlog.Logger(name="test", manager=manager)
        manager.loggers = {"test": logger}

        assert logger.level == containerlog.DEBUG
        assert manager.level == containerlog.ERROR

        manager.set_levels()

        assert logger.level == containerlog.ERROR
        assert manager.level == containerlog.ERROR


class TestLogger:
    def test_init(self):
        logger = containerlog.Logger(
            name="test", level=containerlog.INFO, manager=containerlog.manager
        )
        assert logger.name == "test"
        assert logger.level == containerlog.INFO
        assert logger._previous_level is None

    def test_init_default_level(self):
        logger = containerlog.Logger(name="test", manager=containerlog.manager)
        assert logger.name == "test"
        assert logger.level == containerlog.DEBUG
        assert logger._previous_level is None

    def test_disable(self):
        logger = containerlog.Logger(name="test", manager=containerlog.manager)
        assert logger.level == containerlog.DEBUG
        assert logger._previous_level is None

        logger.disable()
        assert logger.level == 99
        assert logger._previous_level == containerlog.DEBUG

    def test_disable_already_disabled(self):
        logger = containerlog.Logger(name="test", manager=containerlog.manager)
        assert logger.level == containerlog.DEBUG
        assert logger._previous_level is None

        logger.disable()
        assert logger.level == 99
        assert logger._previous_level == containerlog.DEBUG

        logger.disable()
        assert logger.level == 99
        assert logger._previous_level == containerlog.DEBUG

    @pytest.mark.parametrize(
        "loglevel",
        [
            containerlog.TRACE,
            containerlog.DEBUG,
            containerlog.INFO,
            containerlog.WARN,
            containerlog.ERROR,
            containerlog.CRITICAL,
        ],
    )
    def test_enable_from_disabled(self, loglevel):
        logger = containerlog.Logger(name="test", level=loglevel, manager=containerlog.manager)
        assert logger.level == loglevel
        assert logger._previous_level is None

        logger.disable()
        assert logger.level == 99
        assert logger._previous_level == loglevel

        logger.enable()
        assert logger.level == loglevel
        assert logger._previous_level == loglevel

    @pytest.mark.parametrize(
        "loglevel",
        [
            containerlog.TRACE,
            containerlog.DEBUG,
            containerlog.INFO,
            containerlog.WARN,
            containerlog.ERROR,
            containerlog.CRITICAL,
        ],
    )
    def test_enable_already_enabled(self, loglevel):
        logger = containerlog.Logger(name="test", level=loglevel, manager=containerlog.manager)
        assert logger.level == loglevel
        assert logger._previous_level is None

        logger.enable()
        assert logger.level == loglevel
        assert logger._previous_level is None

    def test_disabled_false(self):
        logger = containerlog.Logger(name="test", manager=containerlog.manager)
        assert logger.disabled is False

    def test_disabled_true(self):
        logger = containerlog.Logger(name="test", manager=containerlog.manager)
        logger.disable()
        assert logger.disabled is True

    @pytest.mark.parametrize(
        "loglevel,msg,kwargs,out,err",
        [
            (
                0,  # trace
                "test msg",
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='trace' event='test msg' \n",  # noqa
                "",
            ),
            (
                1,  # debug
                "msg 'foo'",
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='msg \\'foo\\'' \n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"a": 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a=1\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"a": "foo"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a='foo'\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"a": [1, 2]},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a=[1, 2]\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"a": (2, 3)},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a=(2, 3)\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"a": {2, 3}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a={2, 3}\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"a": {"x": 1}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a={'x': 1}\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"timestamp": 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _timestamp=1\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"logger": 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _logger=1\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"level": 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _level=1\n",  # noqa
                "",
            ),
            (
                2,  # info
                "msg",
                {"event": 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _event=1\n",  # noqa
                "",
            ),
            (
                4,  # error
                "msg",
                {"a": 1, "b": 2},
                "",
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='msg' a=1 b=2\n",  # noqa
            ),
            (
                5,  # critical
                "msg",
                {"a": 1, "b": 2},
                "",
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='msg' a=1 b=2\n",  # noqa
            ),
        ],
    )
    def test_log(self, loglevel, msg, kwargs, out, err, test_logger):
        logger, o, e = test_logger

        logger.level = loglevel
        logger._log(loglevel, msg, **kwargs)

        assert o.getvalue() == out
        assert e.getvalue() == err

    def test_log_with_processor(self, test_logger):
        logger, o, e = test_logger

        manager = containerlog.Manager()
        logger.manager = manager

        class DummyProcessor:
            def merge(self, event):
                event["foo"] = "bar"

        logger.manager.context_processors = [DummyProcessor()]
        logger._log(containerlog.INFO, "test")

        assert (
            o.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='test' foo='bar'\n"
        )
        assert e.getvalue() == ""

    def test_trace(self, test_logger):
        logger, o, e = test_logger

        logger.level = containerlog.TRACE
        logger.trace("test message", key="value")

        assert (
            o.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='trace' event='test message' key='value'\n"
        )  # noqa
        assert e.getvalue() == ""

    def test_trace_nolog(self, test_logger):
        logger, o, e = test_logger

        logger.level = 99
        logger.trace("test message", key="value")

        assert o.getvalue() == ""
        assert e.getvalue() == ""

    def test_debug(self, test_logger):
        logger, o, e = test_logger

        logger.level = containerlog.DEBUG
        logger.debug("test message", key="value")

        assert (
            o.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='test message' key='value'\n"
        )  # noqa
        assert e.getvalue() == ""

    def test_debug_nolog(self, test_logger):
        logger, o, e = test_logger

        logger.level = 99
        logger.debug("test message", key="value")

        assert o.getvalue() == ""
        assert e.getvalue() == ""

    def test_info(self, test_logger):
        logger, o, e = test_logger

        logger.level = containerlog.INFO
        logger.info("test message", key="value")

        assert (
            o.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='test message' key='value'\n"
        )  # noqa
        assert e.getvalue() == ""

    def test_info_nolog(self, test_logger):
        logger, o, e = test_logger

        logger.level = 99
        logger.info("test message", key="value")

        assert o.getvalue() == ""
        assert e.getvalue() == ""

    def test_warn(self, test_logger):
        logger, o, e = test_logger

        logger.level = containerlog.WARN
        logger.warn("test message", key="value")

        assert (
            o.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='test message' key='value'\n"
        )  # noqa
        assert e.getvalue() == ""

    def test_warn_nolog(self, test_logger):
        logger, o, e = test_logger

        logger.level = 99
        logger.warn("test message", key="value")

        assert o.getvalue() == ""
        assert e.getvalue() == ""

    def test_error(self, test_logger):
        logger, o, e = test_logger

        logger.level = containerlog.ERROR
        logger.error("test message", key="value")

        assert o.getvalue() == ""
        assert (
            e.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='test message' key='value'\n"
        )  # noqa

    def test_error_nolog(self, test_logger):
        logger, o, e = test_logger

        logger.level = 99
        logger.error("test message", key="value")

        assert o.getvalue() == ""
        assert e.getvalue() == ""

    def test_critical(self, test_logger):
        logger, o, e = test_logger

        logger.level = containerlog.CRITICAL
        logger.critical("test message", key="value")

        assert o.getvalue() == ""
        assert (
            e.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='test message' key='value'\n"
        )  # noqa

    def test_critical_nolog(self, test_logger):
        logger, o, e = test_logger

        logger.level = 99
        logger.critical("test message", key="value")

        assert o.getvalue() == ""
        assert e.getvalue() == ""


def test_get_logger_existing():
    expected = containerlog.Logger("test", manager=containerlog.manager)
    containerlog.manager.loggers["test"] = expected
    assert len(containerlog.manager.loggers) == 1

    logger = containerlog.get_logger("test")
    assert logger == expected
    assert len(containerlog.manager.loggers) == 1


def test_get_logger_new_with_name():
    assert len(containerlog.manager.loggers) == 0

    logger = containerlog.get_logger("test")
    assert logger.name == "test"
    assert logger.level == containerlog.DEBUG
    assert len(containerlog.manager.loggers) == 1


def test_get_logger_new_no_name():
    assert len(containerlog.manager.loggers) == 0

    logger = containerlog.get_logger()
    assert logger.name == "test_containerlog.test_get_logger_new_no_name"
    assert logger.level == containerlog.DEBUG
    assert len(containerlog.manager.loggers) == 1


def test_caller_name():
    name = containerlog._caller_name(skip=1)
    assert name == "test_containerlog.test_caller_name"


def test_set_level():
    containerlog.manager.loggers = {
        "test": containerlog.Logger("test", manager=containerlog.manager),
        "foo": containerlog.Logger("foo", manager=containerlog.manager),
    }
    assert containerlog.manager.level == containerlog.DEBUG
    for logger in containerlog.manager.loggers.values():
        assert logger.level == containerlog.DEBUG

    containerlog.set_level(containerlog.ERROR)
    assert containerlog.manager.level == containerlog.ERROR
    for logger in containerlog.manager.loggers.values():
        assert logger.level == containerlog.ERROR


def test_disable_glob():
    loggers = {
        "test": containerlog.Logger("test", manager=containerlog.manager),
        "foo": containerlog.Logger("foo", manager=containerlog.manager),
        "foo.bar": containerlog.Logger("foo.bar", manager=containerlog.manager),
        "other": containerlog.Logger("other", level=99, manager=containerlog.manager),
    }

    containerlog.manager.loggers = loggers
    containerlog.disable("foo*", "other")

    assert loggers["test"].level == containerlog.DEBUG
    assert loggers["test"].disabled is False
    assert loggers["foo"].level == 99
    assert loggers["foo"].disabled is True
    assert loggers["foo.bar"].level == 99
    assert loggers["foo.bar"].disabled is True
    assert loggers["other"].level == 99
    assert loggers["other"].disabled is True


def test_disable_all():
    loggers = {
        "test": containerlog.Logger("test", manager=containerlog.manager),
        "foo": containerlog.Logger("foo", manager=containerlog.manager),
        "foo.bar": containerlog.Logger("foo.bar", manager=containerlog.manager),
        "other": containerlog.Logger("other", level=99, manager=containerlog.manager),
    }

    containerlog.manager.loggers = loggers
    containerlog.disable()

    assert loggers["test"].level == 99
    assert loggers["test"].disabled is True
    assert loggers["foo"].level == 99
    assert loggers["foo"].disabled is True
    assert loggers["foo.bar"].level == 99
    assert loggers["foo.bar"].disabled is True
    assert loggers["other"].level == 99
    assert loggers["other"].disabled is True


def test_enable_glob():
    loggers = {
        "test": containerlog.Logger("test", level=99, manager=containerlog.manager),
        "foo": containerlog.Logger("foo", level=99, manager=containerlog.manager),
        "foo.bar": containerlog.Logger(
            "foo.bar", level=containerlog.INFO, manager=containerlog.manager
        ),
        "other": containerlog.Logger("other", level=99, manager=containerlog.manager),
    }

    containerlog.manager.loggers = loggers
    containerlog.enable("foo*", "other")

    assert loggers["test"].level == 99
    assert loggers["test"].disabled is True
    assert loggers["foo"].level == containerlog.DEBUG
    assert loggers["foo"].disabled is False
    assert loggers["foo.bar"].level == containerlog.INFO
    assert loggers["foo.bar"].disabled is False
    assert loggers["other"].level == containerlog.DEBUG
    assert loggers["other"].disabled is False


def test_enable_all():
    loggers = {
        "test": containerlog.Logger("test", level=99, manager=containerlog.manager),
        "foo": containerlog.Logger("foo", level=99, manager=containerlog.manager),
        "foo.bar": containerlog.Logger(
            "foo.bar", level=containerlog.INFO, manager=containerlog.manager
        ),
        "other": containerlog.Logger("other", level=99, manager=containerlog.manager),
    }

    containerlog.manager.loggers = loggers
    containerlog.enable()

    assert loggers["test"].level == containerlog.DEBUG
    assert loggers["test"].disabled is False
    assert loggers["foo"].level == containerlog.DEBUG
    assert loggers["foo"].disabled is False
    assert loggers["foo.bar"].level == containerlog.INFO
    assert loggers["foo.bar"].disabled is False
    assert loggers["other"].level == containerlog.DEBUG
    assert loggers["other"].disabled is False


@pytest.mark.skipif(sys.version_info < (3, 7), reason="contextvars requires py37+")
def test_enable_contextvars():

    assert len(containerlog.manager.context_processors) == 0
    containerlog.enable_contextvars()
    assert len(containerlog.manager.context_processors) == 1


@mock.patch("containerlog.enable")
@mock.patch("containerlog.disable")
@mock.patch("containerlog.set_level")
@mock.patch("containerlog.enable_contextvars")
def test_setup(
    mock_ctxvars: mock.Mock,
    mock_set_level: mock.Mock,
    mock_disable: mock.Mock,
    mock_enable: mock.Mock,
) -> None:

    containerlog.setup(
        enable=["foo"],
        disable=["bar"],
        level=containerlog.DEBUG,
        with_contextvars=True,
    )

    mock_enable.assert_called_once_with("foo")
    mock_disable.assert_called_once_with("bar")
    mock_set_level.assert_called_once_with(containerlog.DEBUG)
    mock_ctxvars.assert_called_once()
