from typing import Any, List, Dict, Callable, Optional

import discord.ui

from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class RendererProxy:
    __slots__ = ("_renderer",)

    def __init__(self, path):
        self._renderer = RendererFactory.get_renderer(path)

    def render(self, key: str, keywords: Optional[Dict[str, Any]] = None) -> discord.Embed:
        if keywords is None:
            keywords = {}
        return self._renderer.render(key, keywords)

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
