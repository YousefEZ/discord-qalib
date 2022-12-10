from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Callable

import discord
import discord.ui as ui


class Renderer(ABC):

    @abstractmethod
    def __init__(self, path: str):
        ...

    @abstractmethod
    def render(self, identifier: str, keywords: Optional[Dict[str, Any]] = None) -> discord.Embed:
        ...

    @abstractmethod
    def render_components(
            self,
            identifier: str,
            callables: Dict[str, Callable],
            keywords: Dict[str, Any]
    ) -> Optional[List[ui.Item]]:
        ...

    @abstractmethod
    def set_menu(self, key: str):
        ...

    @property
    @abstractmethod
    def size(self):
        ...

    @property
    @abstractmethod
    def keys(self):
        ...
