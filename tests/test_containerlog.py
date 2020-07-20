"""Unit tests for containerlog."""

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
        logger = containerlog.Logger(name='test')
        manager.set_levels()

        # Verify that the manager level is ERROR
        assert manager.level == containerlog.ERROR

        # Verify that a Logger not registered with the manager
        # did not get the Manager's log level.
        assert logger.level == containerlog.DEBUG

    def test_set_levels_with_loggers(self):
        logger = containerlog.Logger(name='test')
        manager = containerlog.Manager(level=containerlog.ERROR)
        manager.loggers = {'test': logger}

        assert logger.level == containerlog.DEBUG
        assert manager.level == containerlog.ERROR

        manager.set_levels()

        assert logger.level == containerlog.ERROR
        assert manager.level == containerlog.ERROR


class TestLogger:

    def test_init(self):
        logger = containerlog.Logger(name='test', level=containerlog.INFO)
        assert logger.name == 'test'
        assert logger.level == containerlog.INFO

    def test_init_default_level(self):
        logger = containerlog.Logger(name='test')
        assert logger.name == 'test'
        assert logger.level == containerlog.DEBUG

    def test_disable(self):
        logger = containerlog.Logger(name='test')
        assert logger.level == containerlog.DEBUG

        logger.disable()
        assert logger.level == 99

    @pytest.mark.parametrize(
        'loglevel,msg,kwargs,out,err',
        [
            (
                0,  # trace
                'test msg',
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='trace' event='test msg' \n",  # noqa
                '',
            ),
            (
                1,  # debug
                "msg 'foo'",
                {},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='msg \\'foo\\'' \n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'a': 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a=1\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'a': 'foo'},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a='foo'\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'a': [1, 2]},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a=[1, 2]\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'a': (2, 3)},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a=(2, 3)\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'a': {2, 3}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a={2, 3}\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'a': {'x': 1}},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' a={'x': 1}\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'timestamp': 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _timestamp=1\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'logger': 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _logger=1\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'level': 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _level=1\n",  # noqa
                '',
            ),
            (
                2,  # info
                'msg',
                {'event': 1},
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='msg' _event=1\n",  # noqa
                '',
            ),
            (
                4,  # error
                'msg',
                {'a': 1, 'b': 2},
                '',
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='msg' a=1 b=2\n",  # noqa
            ),
            (
                5,  # critical
                'msg',
                {'a': 1, 'b': 2},
                '',
                "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='msg' a=1 b=2\n",  # noqa
            ),
        ],
    )
    def test_log(self, loglevel, msg, kwargs, out, err, logger):
        logger.level = loglevel
        logger._log(loglevel, msg, **kwargs)

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == out
        assert logger.err.getvalue() == err

    def test_trace(self, logger):
        logger.level = containerlog.TRACE
        logger.trace('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == "timestamp='2020-01-01T00:00:00Z' logger='test' level='trace' event='test message' key='value'\n"  # noqa
        assert logger.err.getvalue() == ''

    def test_trace_nolog(self, logger):
        logger.level = 99
        logger.trace('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == ''

    def test_debug(self, logger):
        logger.level = containerlog.DEBUG
        logger.debug('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == "timestamp='2020-01-01T00:00:00Z' logger='test' level='debug' event='test message' key='value'\n"  # noqa
        assert logger.err.getvalue() == ''

    def test_debug_nolog(self, logger):
        logger.level = 99
        logger.debug('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == ''

    def test_info(self, logger):
        logger.level = containerlog.INFO
        logger.info('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == "timestamp='2020-01-01T00:00:00Z' logger='test' level='info' event='test message' key='value'\n"  # noqa
        assert logger.err.getvalue() == ''

    def test_info_nolog(self, logger):
        logger.level = 99
        logger.info('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == ''

    def test_warn(self, logger):
        logger.level = containerlog.WARN
        logger.warn('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == "timestamp='2020-01-01T00:00:00Z' logger='test' level='warn' event='test message' key='value'\n"  # noqa
        assert logger.err.getvalue() == ''

    def test_warn_nolog(self, logger):
        logger.level = 99
        logger.warn('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == ''

    def test_error(self, logger):
        logger.level = containerlog.ERROR
        logger.error('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == "timestamp='2020-01-01T00:00:00Z' logger='test' level='error' event='test message' key='value'\n"  # noqa

    def test_error_nolog(self, logger):
        logger.level = 99
        logger.error('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == ''

    def test_critical(self, logger):
        logger.level = containerlog.CRITICAL
        logger.critical('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == "timestamp='2020-01-01T00:00:00Z' logger='test' level='critical' event='test message' key='value'\n"  # noqa

    def test_critical_nolog(self, logger):
        logger.level = 99
        logger.critical('test message', key='value')

        # .out and .err monkey-patched in at fixture
        assert logger.out.getvalue() == ''
        assert logger.err.getvalue() == ''


def test_get_logger_existing():
    expected = containerlog.Logger('test')
    containerlog.manager.loggers['test'] = expected
    assert len(containerlog.manager.loggers) == 1

    logger = containerlog.get_logger('test')
    assert logger == expected
    assert len(containerlog.manager.loggers) == 1


def test_get_logger_new_with_name():
    assert len(containerlog.manager.loggers) == 0

    logger = containerlog.get_logger('test')
    assert logger.name == 'test'
    assert logger.level == containerlog.DEBUG
    assert len(containerlog.manager.loggers) == 1


def test_get_logger_new_no_name():
    assert len(containerlog.manager.loggers) == 0

    logger = containerlog.get_logger()
    assert logger.name == 'test_containerlog.test_get_logger_new_no_name'
    assert logger.level == containerlog.DEBUG
    assert len(containerlog.manager.loggers) == 1


def test_caller_name():
    name = containerlog._caller_name(skip=1)
    assert name == 'test_containerlog.test_caller_name'


def test_set_level():
    containerlog.manager.loggers = {
        'test': containerlog.Logger('test'),
        'foo': containerlog.Logger('foo'),
    }
    assert containerlog.manager.level == containerlog.DEBUG
    for logger in containerlog.manager.loggers.values():
        assert logger.level == containerlog.DEBUG

    containerlog.set_level(containerlog.ERROR)
    assert containerlog.manager.level == containerlog.ERROR
    for logger in containerlog.manager.loggers.values():
        assert logger.level == containerlog.ERROR
