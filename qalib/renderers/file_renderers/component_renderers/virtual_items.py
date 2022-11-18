from abc import ABC, abstractmethod

from discord.ui import Item, Button, Select


class VirtualItem(ABC):

    @abstractmethod
    def __init__(self, key: str):
        raise NotImplementedError

    @property
    @abstractmethod
    def key(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def render(self, **fields) -> Item:
        raise NotImplementedError


class VirtualButton(VirtualItem):

    def __init__(self, key: str):
        self._key = key

    @property
    def key(self) -> str:
        return self._key

    def render(self, **fields) -> Item:
        return Button(**fields)
