from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Callable

import discord
import discord.ui as ui


class Renderer(ABC):

    @abstractmethod
    def __init__(self, path: str):
        raise NotImplementedError

    @abstractmethod
    def render(self, identifier: str, keywords: Optional[Dict[str, Any]] = None) -> discord.Embed:
        raise NotImplementedError

    @abstractmethod
    def render_components(
            self,
            identifier: str,
            callables: Dict[str, Callable],
            keywords: Dict[str, Any]
    ) -> Optional[List[ui.Item]]:
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
