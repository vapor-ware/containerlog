"""Methods providing support for context-local state in asynchronous code.

This uses the Python standard library's `contextvars` package (see:
https://docs.python.org/3/library/contextvars.html), introduced in
Python 3.7.
"""

import contextvars
from typing import Any, Dict

_CTX: contextvars.ContextVar[Dict[str, Any]] = contextvars.ContextVar(
    "containerlog_ctx",
)

# FIXME (etd): Do we want to have a single "context" type set for the logger or
#   do we want to be able to support multiple kinds? e.g. use contextvars and a
#   logger-local context. This would differentiate binding to the logger vs binding
#   to the contextvar in this case. Seems like it could be useful, but is it ultimately
#   any different? Need to examine the performance of a local bind/unbind (e.g. dict?)
#   vs bind/unbind with a contextvar


def _get_context() -> Dict[Any, Any]:
    """"""
    try:
        return _CTX.get()
    except LookupError:
        _CTX.set({})
        return _CTX.get()


def get() -> Dict[Any, Any]:
    """"""

    return _get_context()


def bind(**kwargs: Any) -> None:
    """"""

    _get_context().update(kwargs)


def unbind(*keys: str) -> None:
    """"""

    ctx = _get_context()
    # FIXME (etd): pop or del? which is more performant?
    for key in keys:
        ctx.pop(key, None)


def clear() -> None:
    """"""

    _get_context().clear()


class AsyncContext:
    """"""

    @staticmethod
    def get() -> Dict[Any, Any]:
        return get()

    @staticmethod
    def bind(**kwargs: Any) -> None:
        bind(**kwargs)

    @staticmethod
    def unbind(*keys: str) -> None:
        unbind(*keys)

    @staticmethod
    def clear() -> None:
        clear()
