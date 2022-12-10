from typing import Protocol, Optional, Dict, Callable, Any, List

import discord.ui


class RendererProtocol(Protocol):

    def render(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Callable]],
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> (discord.Embed, Optional[discord.ui.View]):
        raise NotImplementedError

    def set_menu(self, key: str):
        raise NotImplementedError

    @property
    def size(self) -> int:
        raise NotImplementedError

    @property
    def keys(self) -> List[str]:
        raise NotImplementedError
