"""Proxy logger for Python standard library logger."""

import fnmatch
import logging
import sys
from logging import Logger
from types import ModuleType
from typing import Union

import containerlog

__all__ = [
    'patch',
    'StdLoggerProxy',
]


def patch(*loggers: str) -> None:
    """Patch references to the specified loggers so they instead reference
    an instance of the StdLoggerProxy.

    The logging level for the logging.Logger instance is preserved in its
    corresponding StdLoggerProxy replacement.

    Note that by patching in the proxy class, any configuration specific
    to the logger, e.g. its log handlers and formatters, does not get
    honored by containerlog because containerlog has no notion of handlers
    and formatters.

    Loggers may be specified explicitly by name, e.g. 'foo', or using a
    glob match, e.g. 'foo.*'. Specified loggers will be updated in the
    logger.Manager. However, if a module has already loaded the named
    logger, it will hold a reference to the logging.Logger locally, so
    this method will also search all currently loaded non-builtin modules
    for objects in that module's globals which match the id of the
    logging.Logger object being replaced.

    If no loggers are specified by name, this will patch all instanced of
    logging.Logger currently being tracked within the logging.Manager and
    sets the Manager's loggingClass to StdLoggerProxy so that any loggers
    loaded later on will automatically be an instance of the proxy class.
    In this case, a global module search for loggers does not happen, so
    any loggers already loaded into a module's locals will not be updated.

    Args:
        loggers: The glob-names of the loggers to patch. May be left
            unspecified to patch all logging.Logger instances managed
            by the logging.Manager.
    """
    if len(loggers) == 0:
        _patch_all()
    else:
        for logger_glob in loggers:
            filtered = fnmatch.filter(Logger.manager.loggerDict.keys(), logger_glob)  # type: ignore
            for name in filtered:
                _patch_logger(name)


def _patch_all() -> None:
    """Patch all present and future loggers managed by the logger.Manager
    to use the StdLoggerProxy.

    See the docstring for ``patch`` for additional details.
    """
    # Set the StdLoggerProxy as the logging class to use for std logger. This
    # ensures that any new loggers loaded later on (e.g. if they were initialized
    # as a logging.PlaceHolder) are loaded as this proxy class and not the regular
    # logging.Logger.
    Logger.manager.loggerClass = StdLoggerProxy  # type: ignore

    # Replace all already initialized Logger instances with their corresponding
    # StdLoggerProxy.
    for name in Logger.manager.loggerDict.keys():  # type: ignore
        logger = Logger.manager.loggerDict[name]  # type: ignore

        # Need to check that it is a Logger, as it may be a PlaceHolder.
        if isinstance(logger, logging.Logger):
            level = _map_level(logger.level)

            new_logger = StdLoggerProxy(name)
            new_logger.level = level
            Logger.manager.loggerDict[name] = new_logger  # type: ignore


def _patch_logger(name: str) -> None:
    """Patch out the logging.Logger referenced by name and replace it with
    a corresponding StdLoggerProxy.

    See the docstring for ``patch`` for additional details.

    Args:
        name: The name of the logging.Logger to patch globally.
    """
    std = logging.getLogger(name)
    new_log = StdLoggerProxy(name)
    if std:
        # This really is Schrödinger's code here.. I am simultaneously
        # deeply ashamed and proud of it.
        for mod_name in list(sys.modules.keys()):
            mod = sys.modules[mod_name]
            if mod_name not in sys.builtin_module_names:
                if isinstance(mod, ModuleType):
                    for module_member_name, module_member in mod.__dict__.items():
                        if module_member is std:
                            new_log.setLevel(module_member.level)
                            mod.__dict__[module_member_name] = new_log

    # After patching the logging.Logger instance globally, patch it out
    # of the logging.Manager.
    Logger.manager.loggerDict[name] = new_log  # type: ignore


def _map_level(level: Union[int, str]) -> int:
    """Map the logging level to the containerlog level.

    Note: If a package is using custom levels, we have no way to
    effectively map it here. Instead of mapping to some arbitrary
    log level, we set the logger to disabled by using a value of 90.
    Generally, 99 is used for disabling, so checking for level 90
    would be indicative of custom log levels.

    Args:
        level: The Python standard logger log level.

    Returns:
        The corresponding containerlog log level.
    """
    level = _normalize_level(level)
    return {
        logging.DEBUG: containerlog.DEBUG,
        logging.INFO: containerlog.INFO,
        logging.WARNING: containerlog.WARN,
        logging.ERROR: containerlog.ERROR,
        logging.CRITICAL: containerlog.CRITICAL,
        logging.NOTSET: 99,  # effective disabled
    }.get(level, 90)


def _normalize_level(level: Union[str, int]) -> int:
    """Normalize the logging level which may be a string or int to its
    integer representation.

    Args:
        level: The logging level to normalize.

    Returns:
        The corresponding integer log level.
    """
    if isinstance(level, int):
        rv = level
    elif str(level) == level:
        if level.upper() not in logging._nameToLevel:
            raise ValueError(f'Unknown logging level: {level}')
        rv = logging._nameToLevel[level.upper()]
    else:
        raise TypeError(f'Level not an integer or a valid string: {level}')
    return rv


class StdLoggerProxy(Logger):
    """A proxy for a logging.Logger which uses a containerlog.Logger.

    This proxy implements the logging interface for a logging.Logger, but
    logs to an underlying containerlog.Logger. This effectively allows an
    application to replace existing logging.Logger instances (e.g. from
    project dependencies) with a containerlog.Logger so all application
    logging is consistent.

    This must be a subclass of logging.Logger so it can be set as a valid
    loggerClass on the logging.Manager.
    """

    def __init__(self, name: str) -> None:
        self.containerlog = containerlog.get_logger(name)
        super(StdLoggerProxy, self).__init__(name)

    def setLevel(self, level: Union[int, str]) -> None:
        self.level = _normalize_level(level)
        self.containerlog.level = _map_level(level)

    @property
    def writeout(self):
        return self.containerlog.writeout

    @writeout.setter
    def writeout(self, fn):
        self.containerlog.writeout = fn

    @property
    def writeerr(self):
        return self.containerlog.writeerr

    @writeerr.setter
    def writeerr(self, fn):
        self.containerlog.writeerr = fn

    def debug(self, msg, *args, **kwargs):
        """Log a message at DEBUG level."""
        extras = {}
        if 'extra' in kwargs:
            extras = kwargs['extra']
        if args:
            msg = msg % args
        self.containerlog.debug(msg, **extras)

    def info(self, msg, *args, **kwargs):
        """Log a message at INFO level."""
        extras = {}
        if 'extra' in kwargs:
            extras = kwargs['extra']
        if args:
            msg = msg % args
        self.containerlog.info(msg, **extras)

    def warning(self, msg, *args, **kwargs):
        """Log a message at WARN level."""
        extras = {}
        if 'extra' in kwargs:
            extras = kwargs['extra']
        if args:
            msg = msg % args
        self.containerlog.warn(msg, **extras)

    warn = warning

    def error(self, msg, *args, **kwargs):
        """Log a message at ERROR level."""
        extras = {}
        if 'extra' in kwargs:
            extras = kwargs['extra']
        if args:
            msg = msg % args
        self.containerlog.error(msg, **extras)

    def exception(self, msg, *args, **kwargs):
        """Log a message at ERROR level with exception traceback."""
        extras = {}
        if 'extra' in kwargs:
            extras = kwargs['extra']
        if args:
            msg = msg % args
        self.containerlog.exception(msg, **extras)

    def critical(self, msg, *args, **kwargs):
        """Log a message at CRITICAL level."""
        extras = {}
        if 'extra' in kwargs:
            extras = kwargs['extra']
        if args:
            msg = msg % args
        self.containerlog.critical(msg, **extras)

    fatal = critical

    def log(self, level, msg, *args, **kwargs):
        """Log a message at the specified level."""
        name = logging._levelToName.get(level)
        if not name:
            return
        getattr(self, name.lower())(msg, *args, **kwargs)
