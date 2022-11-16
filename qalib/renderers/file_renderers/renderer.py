from abc import ABC, abstractmethod

from discord import Embed


class Renderer(ABC):

    @abstractmethod
    def __init__(self, path: str):
        raise NotImplementedError

    @abstractmethod
    def render(self, identifier: str, **kwargs) -> Embed:
        raise NotImplementedError

    @abstractmethod
    def set_menu(self, key: str):
        raise NotImplementedError

    @property
    @abstractmethod
    def size(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def keys(self):
        raise NotImplementedError
