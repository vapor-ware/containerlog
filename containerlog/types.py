""""""

import sys
from typing import Any, MutableMapping

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, runtime_checkable  # pragma: nocover
else:
    from typing import Protocol, runtime_checkable  # pragma: nocover


__all__ = [
    "ContextProcessor",
    "EventContext",
]

# EventContext contains the key-value pairs providing contextualized information
# for a log event.
EventContext = MutableMapping[str, Any]


@runtime_checkable
class ContextProcessor(Protocol):
    """A context processor defines an interface for 'processors', which are used
    to augment a logger's event context during a log event.
    """

    def merge(self, event: EventContext) -> None:
        ...  # pragma: nocover

    def bind(self, **kwargs: Any) -> None:
        ...  # pragma: nocover

    def unbind(self, *keys: str) -> None:
        ...  # pragma: nocover

    def clear(self) -> None:
        ...  # pragma: nocover
