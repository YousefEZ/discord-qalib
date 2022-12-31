from abc import ABC, abstractmethod
from typing import Any, Optional, List, Dict, Coroutine

import discord
import discord.ui as ui


class Renderer(ABC):

    @abstractmethod
    def render(self, identifier: str, keywords: Optional[Dict[str, Any]] = None) -> discord.Embed:
        ...

    @abstractmethod
    def render_components(
            self,
            identifier: str,
            callables: Dict[str, Coroutine],
            keywords: Dict[str, Any]
    ) -> Optional[List[ui.Item]]:
        ...

    @abstractmethod
    def set_root(self, key: str):
        ...

    @property
    @abstractmethod
    def size(self):
        ...

    @property
    @abstractmethod
    def keys(self):
        ...
