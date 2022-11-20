from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Callable

import discord
import discord.ui as ui


class Renderer(ABC):

    @abstractmethod
    def __init__(self, path: str):
        raise NotImplementedError

    @abstractmethod
    def render(self, identifier: str, **kwargs) -> discord.Embed:
        raise NotImplementedError

    @abstractmethod
    def render_components(self, identifier: str, callables: Dict[str, Callable], **kwargs) -> Optional[List[ui.Item]]:
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
