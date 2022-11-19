from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Callable

from discord import Embed
from discord.ui import Item


class Renderer(ABC):

    @abstractmethod
    def __init__(self, path: str):
        raise NotImplementedError

    @abstractmethod
    def render(self, identifier: str, **kwargs) -> Embed:
        raise NotImplementedError

    @abstractmethod
    def render_components(self, identifier: str, callables: Dict[str, Callable], **kwargs) -> Optional[List[Item]]:
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
