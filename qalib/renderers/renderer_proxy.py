from typing import Any, List, Dict, Coroutine, Optional, Callable

import discord.ui

from . import RendererProtocol, Display, create_arrows
from .file_renderers.renderer_factory import RendererFactory


class RendererProxy(RendererProtocol):
    __slots__ = ("_renderer",)

    def __init__(self, path: str, root: Optional[str] = None):
        self._renderer = RendererFactory.get_renderer(path)
        if root is not None:
            self.set_root(root)

    def render(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Coroutine]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> Display:
        return Display(self.render_embed(identifier, keywords),
                       self.render_view(identifier, callbacks, timeout, keywords))

    def set_root(self, key: str):
        self._renderer.set_root(key)

    def render_embed(self, identifier: str, keywords: Optional[Dict[str, Any]] = None):
        if keywords is None:
            keywords = {}

        return self._renderer.render(identifier, keywords)

    def render_view(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Coroutine]] = None,
            timeout: Optional[int] = 180,
            keywords: Optional[Dict[str, Any]] = None
    ) -> Optional[discord.ui.View]:
        """Methods that renders a view from the Renderer

        Args:
            identifier (str): identifier of the embed
            callbacks (Optional[Dict[str, Coroutine]]): callbacks that are attached to the components of the view
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

    def render_menu(
            self,
            callbacks: Optional[Dict[str, Callable]],
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180,
            **kwargs
    ) -> Display:
        """This method is used to create a menu for the user to select from.

        Args:
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view
            timeout (Optional[int]): timeout of the view
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
        """

        def create_display_with_default_view(identifier: str) -> Display:
            embed = self.render_embed(identifier, keywords)
            view = self.render_view(identifier, callbacks, timeout, keywords)
            return Display(embed, discord.ui.View() if view is None else view)

        keys = self._renderer.keys
        displays = [create_display_with_default_view(key) for key in keys]

        for i, display in enumerate(displays):
            arrow_left = displays[i - 1] if i > 0 else None
            arrow_right = displays[i + 1] if i + 1 < len(displays) else None

            for arrow in create_arrows(arrow_left, arrow_right, **kwargs):
                display.view.add_item(arrow)

        return displays[0]
