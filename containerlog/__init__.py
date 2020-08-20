"""An optimized, opinionated, zero-config structured logging package.

This minimalistic logging library is optimized for performance and is
intended for, but not limited to, application which run inside of a
container.
"""

import datetime
import inspect
import io
import sys
import traceback
from typing import Dict, Optional

# Project attributes
__title__ = 'containerlog'
__version__ = '0.2.3'
__description__ = 'Optimized, opinionated structured logging for containerized applications.'
__author__ = 'Erick Daniszewski'
__author_email__ = 'erick@vapor.io'
__url__ = 'https://github.com/vapor-ware/containerlog'
__license__ = 'GNU General Public License v3.0'

# Log levels are defined as integers. This allows quick and easy level
# comparisons (greater than, less than, equal to).
TRACE = 0
DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4
CRITICAL = 5


class Logger:
    """A named logging channel.

    A "logging channel" can generally be considered an area of an application,
    with no strict definition of "area". The channel is identified by name.

    Args:
        name: The name of the logger. This is how loggers are referenced
            (e.g. via `get_logger`) and is the name that appears under the
            "logger" key in the log output.
        level: The log level to use for the logger. If no level is set, it
            defaults to DEBUG (1) - better to collect more logs than no logs.
            This can be modified on the logger instance itself, or the logging
            level may be set for all loggers globally via `set_level`.
    """

    _level_lookup = {
        0: 'trace',
        1: 'debug',
        2: 'info',
        3: 'warn',
        4: 'error',
        5: 'critical',
    }

    def __init__(self, name: str, level: Optional[int] = None) -> None:
        self.name = name
        self.level = level or DEBUG

        # Proxy module functions being used into the class scope. This
        # speeds things up by making what would otherwise be a LOAD_GLOBAL
        # (plus any additional LOAD_ATTRs) into a LOAD_FAST.
        self.utcnow = datetime.datetime.utcnow
        self.writeout = sys.stdout.write
        self.writeerr = sys.stderr.write

    def disable(self) -> None:
        """Disable the logger.

        Instead of setting a "disabled" flag, the logger can be disabled without
        any additional code paths by setting the log level to something higher
        than the supported log levels.
        """
        self.level = 99

    def _log(self, loglevel: int, msg: str, exc: bool = False, **kwargs) -> None:
        """Log a message to console.

        The underlying log function. All higher-level convenience methods
        (debug, info, error, ...) call this to do the actual logging.

        Args:
            loglevel: The level to log the message at.
            msg: The message to log.
            exc: Whether or not to include an exception traceback.
            **kwargs: Additional structured data to add to the log entry.
        """
        # Since log message are output in the format: event='message', any single
        # quotes within the message should be escaped.
        if "'" in msg:
            msg = msg.replace("'", "\\'")

        # If any of the reserved keys are in the kwargs, update the kwargs
        # dict so the colliding key is prefixed with an underscore. This is
        # done one at a time instead of a loop, as this was measured to be
        # slightly more performant.
        if 'timestamp' in kwargs:
            kwargs['_timestamp'] = kwargs['timestamp']
            del kwargs['timestamp']
        if 'logger' in kwargs:
            kwargs['_logger'] = kwargs['logger']
            del kwargs['logger']
        if 'level' in kwargs:
            kwargs['_level'] = kwargs['level']
            del kwargs['level']
        if 'event' in kwargs:
            kwargs['_event'] = kwargs['event']
            del kwargs['event']

        # For extra kv items, if the value is a string, wrap it in single quotes.
        # Otherwise let the object's __str__ or __repr__ deal with it.
        def fmt_val(v):
            if isinstance(v, str):
                return f"'{v}'"
            return v

        # Format the log message entry.
        extras = ' '.join(f"{k}={fmt_val(v)}" for k, v in kwargs.items())
        entry = f"timestamp='{self.utcnow().isoformat('T')}Z' logger='{self.name}' level='{self._level_lookup[loglevel]}' event='{msg}' {extras}\n"  # noqa

        if exc:
            exc_info = sys.exc_info()
            buf = io.StringIO()
            traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], None, buf)
            s = buf.getvalue()
            buf.close()
            if s[-1] != '\n':
                s += '\n'
            entry += s

        # Log to stderr if at level error or greater, otherwise log to stdout.
        (loglevel >= 4 and self.writeerr(entry)) or self.writeout(entry)

    def trace(self, msg, **kwargs):
        """Log a message at TRACE level.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 0 and self._log(0, msg, **kwargs)

    def debug(self, msg, **kwargs):
        """Log a message at DEBUG level.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 1 and self._log(1, msg, **kwargs)

    def info(self, msg, **kwargs):
        """Log a message at INFO level.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 2 and self._log(2, msg, **kwargs)

    def warn(self, msg, **kwargs):
        """Log a message at WARN level.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 3 and self._log(3, msg, **kwargs)

    warning = warn

    def error(self, msg, **kwargs):
        """Log a message at ERROR level.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 4 and self._log(4, msg, **kwargs)

    def critical(self, msg, **kwargs):
        """Log a message at CRITICAL level.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 5 and self._log(5, msg, **kwargs)

    def exception(self, msg, **kwargs):
        """Log a message at ERROR level with an exception stack trace.

        Args:
            msg: The message to log.
            **kwargs: Additional structured data to add to the log entry.
        """
        self.level <= 4 and self._log(4, msg, exc=True, **kwargs)


class Manager:
    """Manages instances of Loggers.

    This acts as a container for existing Loggers and allows global
    operations on those configured loggers.

    Args:
        level: The global log level to apply to all Loggers on initialization.
    """

    def __init__(self, level: int = DEBUG) -> None:
        self.level: int = level
        self.loggers: Dict[str, Logger] = {}

    def set_levels(self) -> None:
        """Set the log level for each tracked logger."""
        for logger in self.loggers.values():
            logger.level = self.level


# A global manager instance. This should be the only place Manager
# is used so there is a central authority on all logger instances.
manager = Manager()


def set_level(level: int) -> None:
    """Set the global logging level for all Loggers.

    Args:
        level: The log level to set.
    """
    manager.level = level
    manager.set_levels()


def _caller_name(skip=2):
    """Get the name of the module for the caller of the function.

    Args:
        skip: The number of stack frames to skip when looking back.
            By default this is 2 so we skip the frame for this function
            and the frame for the function that called it, getting the
            frame of the caller.

                caller() -> some_func() -> _caller_name()
                       * <- skip frame  <- skip frame

    Returns:
        The full module name for the caller of a function.
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
        return ''
    pframe = stack[start][0]

    name = []
    mod = inspect.getmodule(pframe)
    if mod:
        name.append(mod.__name__)
    if 'self' in pframe.f_locals:
        name.append(pframe.f_locals['self'].__class__.__name__)
    codename = pframe.f_code.co_name
    if codename != '<module>':
        name.append(codename)
    del pframe
    return '.'.join(name)


def get_logger(name: Optional[str] = None) -> Logger:
    """Get the Logger for the given name.

    If no name is provided, the module path will be used. If no
    logger with the name exists, a new one will be created and
    tracked by the Manager.

    Args:
        name: The name of the logger to get.

    Returns:
        A Logger matching the provided name.
    """
    name = name or _caller_name()
    logger = manager.loggers.get(name, None)
    if not logger:
        logger = Logger(
            name=name,
            level=manager.level,
        )
        manager.loggers[name] = logger

    return logger
