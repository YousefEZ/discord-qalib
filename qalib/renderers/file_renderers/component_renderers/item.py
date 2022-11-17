from abc import ABC
from typing import Optional, Callable, Type


class Item(ABC):

    def __init__(self, item_id: str = None):
        self._item_id: Optional[str] = item_id
        self._callback: Optional[Callable] = None

    def set_callback(self, callback: Callable):
        self._callback = callback

    @property
    def callback(self) -> Optional[Callable]:
        return self._callback


class VirtualItem:

    def __init__(self, key: str, component: Type[Item]):
        self._key: str = key
        self._component = component

    @property
    def key(self) -> str:
        return self._key

    @property
    def component(self) -> Type[Item]:
        return self._component

    def render(self, callable: Optional[Callable] = None, **kwargs):
        return self._component(self._key)
