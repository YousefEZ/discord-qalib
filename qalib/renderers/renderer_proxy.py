from typing import Any, List, Dict, Callable, Optional

import discord.ui

from . import RendererProtocol
from .file_renderers.renderer_factory import RendererFactory


class RendererProxy(RendererProtocol):
    __slots__ = ("_renderer",)

    def __init__(self, path: str):
        self._renderer = RendererFactory.get_renderer(path)

    def render(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Callable]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> (discord.Embed, Optional[discord.ui.View]):

        return self.render_embed(identifier, keywords), self.render_view(identifier, callbacks, timeout, keywords)

    def render_embed(self, identifier: str, keywords: Optional[Dict[str, Any]] = None):
        if keywords is None:
            keywords = {}

        return self._renderer.render(identifier, keywords)

    def render_view(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Callable]] = None,
            timeout: Optional[int] = 180,
            keywords: Optional[Dict[str, Any]] = None
    ) -> Optional[discord.ui.View]:
        """Methods that renders a view from the Renderer

        Args:
            identifier (str): identifier of the embed
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view
            timeout (Optional[int]): timeout of the view
            keywords (Optional[Dict[str, Any]]): keywords that are used to format the components

        Returns (Optional[discord.ui.View]): View object that is rendered from the Renderer
        """

        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        components: Optional[List[discord.ui.Item]] = self._renderer.render_components(identifier, callbacks, keywords)
        if components is None:
            return None

        view = discord.ui.View(timeout=timeout)
        for component in components:
            view.add_item(component)
        return view

    @property
    def size(self) -> int:
        return self._renderer.size

    @property
    def keys(self) -> List[str]:
        return self._renderer.keys
