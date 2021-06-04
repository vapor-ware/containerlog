"""Methods providing support for context-local state in asynchronous code.

This uses the Python standard library's `contextvars` package (see:
https://docs.python.org/3/library/contextvars.html), introduced in
Python 3.7.
"""

import contextlib
import contextvars
from typing import Any, Dict

from .types import ContextProcessor, EventContext

CTXVAR_PREFIX: str = "containerlog_"
_PREFIX_SIZE: int = len(CTXVAR_PREFIX)
_CTXVARS: Dict[str, contextvars.ContextVar[Any]] = {}


def merge(event: EventContext) -> None:
    """Merge the contextvar state with the provided event context dict.

    This mutates the event dict.

    Args:
        event: The event context to add context-local fields to.
    """

    ctx = contextvars.copy_context()
    for key in ctx:
        if key.name.startswith(CTXVAR_PREFIX) and ctx[key] is not Ellipsis:
            event.setdefault(
                key.name[_PREFIX_SIZE:],
                ctx[key],
            )


def bind(**kwargs: Any) -> None:
    """Bind key-value context to the async-aware contextvar state.

    Args:
        kwargs: The key-value pairs to bind as event context.
    """

    for k, v in kwargs.items():
        key = f"{CTXVAR_PREFIX}{k}"
        try:
            var = _CTXVARS[key]
        except KeyError:
            var = contextvars.ContextVar(key, default=Ellipsis)
            _CTXVARS[key] = var

        var.set(v)


def unbind(*keys: str) -> None:
    """Unbind keys from the async-aware contextvar state.

    Args:
        keys: The keys of previously bound context to remove from the
            event context.
    """

    for k in keys:
        key = f"{CTXVAR_PREFIX}{k}"
        if key in _CTXVARS:
            _CTXVARS[key].set(Ellipsis)


@contextlib.contextmanager
def context_binding(**kwargs):
    """A context manager to support binding/unbinding of key-value pairs to
    the async-aware contextvar state.

    Args:
        kwargs: The key-value pairs to bind as event context.
    """
    bind(**kwargs)
    try:
        yield
    finally:
        print("•••••••••••••••••••••••")
        print(f"unbinding: {kwargs.keys()}")
        print("•••••••••••••••••••••••")
        unbind(*kwargs.keys())

        print(_CTXVARS)


def clear() -> None:
    """Clear contextvar state."""

    ctx = contextvars.copy_context()
    for key in ctx:
        if key.name.startswith(CTXVAR_PREFIX):
            key.set(Ellipsis)


class Processor(ContextProcessor):
    """A processor to add contextvar-tracked state to log event contexts."""

    def merge(self, event: EventContext) -> None:
        merge(event)

    def bind(self, **kwargs: Any) -> None:
        bind(**kwargs)

    def unbind(self, *keys: str) -> None:
        unbind(*keys)

    def clear(self) -> None:
        clear()
