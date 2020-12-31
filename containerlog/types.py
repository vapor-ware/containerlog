""""""

import sys
from typing import Any, Dict

if sys.version_info < (3, 8):
    from typing_extensions import Protocol, runtime_checkable
else:
    from typing import Protocol, runtime_checkable


@runtime_checkable
class Context(Protocol):
    """"""

    def get(self) -> Dict[Any, Any]:
        ...

    def bind(self, **kwargs: Any) -> None:
        ...

    def unbind(self, *keys: str) -> None:
        ...

    def clear(self) -> None:
        ...
