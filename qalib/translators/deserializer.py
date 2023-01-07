from __future__ import annotations

from typing import Protocol, Dict, List

from qalib.translators import Display, Callback


class Deserializer(Protocol):

    def deserialize(self, source: str, callables: Dict[str, Callback], **kw) -> Display:
        ...

    def deserialize_into_menu(self, source: str, callables: Dict[str, Callback], **kw) -> List[Display]:
        ...
