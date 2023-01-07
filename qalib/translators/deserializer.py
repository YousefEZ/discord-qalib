from __future__ import annotations

from typing import Protocol, Coroutine, Dict, List

from qalib.translators import Display


class Deserializer(Protocol):

    def deserialize(self, source: str, callables: Dict[str, Coroutine], **kw) -> Display:
        ...

    def deserialize_into_menu(self, source: str, callables: Dict[str, Coroutine], **kw) -> List[Display]:
        ...
