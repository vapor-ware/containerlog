"""Unit tests for containerlog's StdLoggerProxy."""

import logging
import sys
from unittest import mock

import pytest

import containerlog
from containerlog.proxy import std


class TestStdLoggerProxy:
    def test_init(self):
        logger = std.StdLoggerProxy("foo")
        assert isinstance(logger, logging.Logger)
        assert logger.containerlog is not None
        assert logger.containerlog.name == "foo"

    def test_set_level(self):
        logger = std.StdLoggerProxy("foo")
        assert logger.containerlog.level == containerlog.DEBUG

        logger.setLevel(logging.WARN)
        assert logger.level == logging.WARN
        assert logger.containerlog.level == containerlog.WARN

    def test_get_set_writeout(self):
        logger = std.StdLoggerProxy("foo")

        def placeholder():
            pass

        assert logger.writeout == sys.stdout.write
        assert logger.containerlog.writeout == sys.stdout.write

        logger.writeout = placeholder
        assert logger.writeout == placeholder
        assert logger.containerlog.writeout == placeholder

    def test_get_set_writeerr(self):
        logger = std.StdLoggerProxy("foo")

        def placeholder():
            pass

        assert logger.writeerr == sys.stderr.write
        assert logger.containerlog.writeerr == sys.stderr.write

        logger.writeerr = placeholder
        assert logger.writeerr == placeholder
        assert logger.containerlog.writeerr == placeholder

    @pytest.mark.parametrize(
        "msg,args,kwargs,out",
        [
            (
                "message",
                [],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='message' \n",
            ),
            (
                "message %s",
                ["value"],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='message value' \n",
            ),
            (
                "message",
                [],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='message' something='else'\n",
            ),
            (
                "message %s",
                ["value"],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='message value' something='else'\n",
            ),
            (
                "message",
                [],
                {"unknown": True, "values": "foobar"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='message' \n",
            ),
        ],
    )
    def test_debug(self, msg, args, kwargs, out, std_proxy_logger):
        std_proxy_logger.setLevel(logging.DEBUG)
        std_proxy_logger.debug(msg, *args, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == out
        assert std_proxy_logger.err.getvalue() == ""

    @pytest.mark.parametrize(
        "msg,args,kwargs,out",
        [
            (
                "message",
                [],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='message' \n",
            ),
            (
                "message %s",
                ["value"],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='message value' \n",
            ),
            (
                "message",
                [],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='message' something='else'\n",
            ),
            (
                "message %s",
                ["value"],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='message value' something='else'\n",
            ),
            (
                "message",
                [],
                {"unknown": True, "values": "foobar"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='message' \n",
            ),
        ],
    )
    def test_info(self, msg, args, kwargs, out, std_proxy_logger):
        std_proxy_logger.setLevel(logging.INFO)
        std_proxy_logger.info(msg, *args, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == out
        assert std_proxy_logger.err.getvalue() == ""

    @pytest.mark.parametrize(
        "msg,args,kwargs,out",
        [
            (
                "message",
                [],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='message' \n",
            ),
            (
                "message %s",
                ["value"],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='message value' \n",
            ),
            (
                "message",
                [],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='message' something='else'\n",
            ),
            (
                "message %s",
                ["value"],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='message value' something='else'\n",
            ),
            (
                "message",
                [],
                {"unknown": True, "values": "foobar"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='message' \n",
            ),
        ],
    )
    def test_warning(self, msg, args, kwargs, out, std_proxy_logger):
        std_proxy_logger.setLevel(logging.WARNING)
        std_proxy_logger.warning(msg, *args, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == out
        assert std_proxy_logger.err.getvalue() == ""

    @pytest.mark.parametrize(
        "msg,args,kwargs,out",
        [
            (
                "message",
                [],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message' \n",
            ),
            (
                "message %s",
                ["value"],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message value' \n",
            ),
            (
                "message",
                [],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message' something='else'\n",
            ),
            (
                "message %s",
                ["value"],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message value' something='else'\n",
            ),
            (
                "message",
                [],
                {"unknown": True, "values": "foobar"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message' \n",
            ),
        ],
    )
    def test_error(self, msg, args, kwargs, out, std_proxy_logger):
        std_proxy_logger.setLevel(logging.ERROR)
        std_proxy_logger.error(msg, *args, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == ""
        assert std_proxy_logger.err.getvalue() == out

    @pytest.mark.parametrize(
        "msg,args,kwargs,out",
        [
            (
                "message",
                [],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message' \nNoneType: None\n",  # noqa
            ),
            (
                "message %s",
                ["value"],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message value' \nNoneType: None\n",  # noqa
            ),
            (
                "message",
                [],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message' something='else'\nNoneType: None\n",  # noqa
            ),
            (
                "message %s",
                ["value"],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message value' something='else'\nNoneType: None\n",  # noqa
            ),
            (
                "message",
                [],
                {"unknown": True, "values": "foobar"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='message' \nNoneType: None\n",  # noqa
            ),
        ],
    )
    def test_exception(self, msg, args, kwargs, out, std_proxy_logger):
        std_proxy_logger.setLevel(logging.ERROR)
        std_proxy_logger.exception(msg, *args, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == ""
        assert std_proxy_logger.err.getvalue() == out

    @pytest.mark.parametrize(
        "msg,args,kwargs,out",
        [
            (
                "message",
                [],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='message' \n",
            ),
            (
                "message %s",
                ["value"],
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='message value' \n",
            ),
            (
                "message",
                [],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='message' something='else'\n",
            ),
            (
                "message %s",
                ["value"],
                {"extra": {"something": "else"}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='message value' something='else'\n",  # noqa
            ),
            (
                "message",
                [],
                {"unknown": True, "values": "foobar"},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='message' \n",
            ),
        ],
    )
    def test_critical(self, msg, args, kwargs, out, std_proxy_logger):
        std_proxy_logger.setLevel(logging.CRITICAL)
        std_proxy_logger.critical(msg, *args, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == ""
        assert std_proxy_logger.err.getvalue() == out

    def test_log(self, std_proxy_logger):
        std_proxy_logger.setLevel(logging.DEBUG)
        std_proxy_logger.log(logging.INFO, "message")

        # .out and .err monkey-patched in at fixture
        assert (
            std_proxy_logger.out.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='message' \n"
        )  # noqa
        assert std_proxy_logger.err.getvalue() == ""

    def test_log_below_debug(self, std_proxy_logger):
        std_proxy_logger.setLevel(logging.NOTSET)
        std_proxy_logger.log(5, "message")

        # .out and .err monkey-patched in at fixture
        assert (
            std_proxy_logger.out.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='trace' event='message' \n"
        )  # noqa
        assert std_proxy_logger.err.getvalue() == ""

    def test_log_above_critical(self, std_proxy_logger):
        std_proxy_logger.setLevel(logging.DEBUG)
        std_proxy_logger.log(30000, "message")

        # .out and .err monkey-patched in at fixture
        assert std_proxy_logger.out.getvalue() == ""
        assert (
            std_proxy_logger.err.getvalue()
            == "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='message' \n"
        )  # noqa


@mock.patch("containerlog.proxy.std._patch_all")
def test_patch_no_loggers(mock_patch):
    std.patch()

    mock_patch.assert_called_once()


@mock.patch("containerlog.proxy.std._patch_logger")
def test_patch_with_loggers(mock_patch):
    # put some loggers into the manager for the test.
    logging.Logger.manager.loggerDict["test-logger-abc"] = logging.Logger("test-logger-abc")
    logging.Logger.manager.loggerDict["test-logger-def"] = logging.Logger("test-logger-def")

    std.patch("test-logger-abc", "test-logger-def")

    mock_patch.assert_has_calls(
        [
            mock.call("test-logger-abc"),
            mock.call("test-logger-def"),
        ]
    )


@mock.patch("containerlog.proxy.std._patch_logger")
def test_patch_with_glob_loggers(mock_patch):
    # put some loggers into the manager for the test.
    logging.Logger.manager.loggerDict["test-logger-abc"] = logging.Logger("test-logger-abc")
    logging.Logger.manager.loggerDict["test-logger-def"] = logging.Logger("test-logger-def")

    std.patch("test-logger-*")

    mock_patch.assert_has_calls(
        [
            mock.call("test-logger-abc"),
            mock.call("test-logger-def"),
        ]
    )


@pytest.mark.usefixtures("reset_logging_manager")
def test_patch_all():
    # we need to create some loggers since this uses a fresh instance of
    # a logging.Manager
    logging.getLogger("foo")
    logging.getLogger("foo.bar.baz")
    logging.getLogger("new-logger")

    # Verify starting assumptions
    assert logging.Logger.manager.loggerClass is None
    # 3 loggers defined above, plus the PlaceHolder for 'foo.bar'
    assert len(logging.Logger.manager.loggerDict) == 4
    for logger in logging.Logger.manager.loggerDict.values():
        if isinstance(logger, logging.PlaceHolder):
            continue
        assert isinstance(logger, logging.Logger)

    # Patch
    std._patch_all()

    # Check that the patch worked
    assert logging.Logger.manager.loggerClass == std.StdLoggerProxy
    # 3 loggers defined above, plus the PlaceHolder for 'foo.bar'
    assert len(logging.Logger.manager.loggerDict) == 4
    for logger in logging.Logger.manager.loggerDict.values():
        if isinstance(logger, logging.PlaceHolder):
            continue
        assert isinstance(logger, std.StdLoggerProxy)


global_logger_for_test = logging.getLogger("test-patch-logger")
global_logger_for_test.setLevel(logging.INFO)


def test_patch_logger():
    # Verify the starting assumptions. We have a standard logger in this module
    # and in the logging manager, and it is a logging.Logger.
    assert isinstance(global_logger_for_test, logging.Logger)
    assert global_logger_for_test.level == logging.INFO
    assert "test-patch-logger" in logging.Logger.manager.loggerDict
    assert isinstance(logging.Logger.manager.loggerDict["test-patch-logger"], logging.Logger)

    # Patch the logger to use the StdLoggerProxy.
    std._patch_logger("test-patch-logger")

    # Check that it was patched.
    assert global_logger_for_test.__class__ == std.StdLoggerProxy
    assert isinstance(global_logger_for_test, std.StdLoggerProxy)
    assert global_logger_for_test.level == logging.INFO
    assert global_logger_for_test.containerlog.level == containerlog.INFO
    assert "test-patch-logger" in logging.Logger.manager.loggerDict
    assert isinstance(logging.Logger.manager.loggerDict["test-patch-logger"], std.StdLoggerProxy)


@pytest.mark.parametrize(
    "level,expected",
    [
        (-1, containerlog.TRACE),
        (logging.NOTSET, containerlog.TRACE),
        (5, containerlog.TRACE),
        (logging.DEBUG, containerlog.DEBUG),
        (logging.INFO, containerlog.INFO),
        (logging.WARN, containerlog.WARN),
        (logging.WARNING, containerlog.WARN),
        (logging.ERROR, containerlog.ERROR),
        (logging.CRITICAL, containerlog.CRITICAL),
        (logging.FATAL, containerlog.CRITICAL),
        (1234, containerlog.CRITICAL),
        (25, 90),
    ],
)
def test_map_level(level, expected):
    assert expected == std._map_level(level)


@pytest.mark.parametrize(
    "level,expected",
    [
        (0, "trace"),
        (5, "trace"),
        (logging.DEBUG, "debug"),
        (logging.INFO, "info"),
        (logging.WARN, "warning"),
        (logging.WARNING, "warning"),
        (logging.ERROR, "error"),
        (logging.FATAL, "critical"),
        (logging.CRITICAL, "critical"),
        (60, "critical"),
    ],
)
def test_get_level_name(level, expected):
    assert std._get_level_name(level) == expected
