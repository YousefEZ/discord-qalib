from . import RendererProtocol

from typing import Any, Callable, Dict, Optional, List

import discord
import jinja2

from qalib.renderers.file_renderers.jinja_renderer import JinjaXMLTemplate
from qalib.renderers.renderer_proxy import RendererProxy


class JinjaProxy(RendererProtocol):
    """Jinja Renderer for embeds"""

    __slots__ = ("_template", "_environment")

    def __init__(self, template: str, environment: jinja2.Environment):
        self._template = template
        self._environment = environment

    def render(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Callable]],
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> (discord.Embed, Optional[discord.ui.View]):
        if keywords is None:
            keywords = {}

        template: JinjaXMLTemplate = JinjaXMLTemplate(self._template, self._environment, keywords)
        template.render_components(identifier, callbacks, keywords)
        return template.render(identifier, keywords), self.render_view(identifier, callbacks, timeout,
                                                                       keywords, template)

    def render_view(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Callable]] = None,
            timeout: Optional[int] = 180,
            keywords: Optional[Dict[str, Any]] = None,
            template: Optional[JinjaXMLTemplate] = None
    ) -> Optional[discord.ui.View]:
        """Methods that renders a view from the Renderer

        Args:
            identifier (str): identifier of the embed
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view
            timeout (Optional[int]): timeout of the view
            keywords (Optional[Dict[str, Any]]): keywords that are used to format the components'
            template (Optional[JinjaXMLTemplate]): JinjaXMLTemplate object that is used to render the components

        Returns (Optional[discord.ui.View]): View object that is rendered from the Renderer
        """

        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        if template is None:
            template = JinjaXMLTemplate(self._template, self._environment, keywords)

        components: Optional[List[discord.ui.Item]] = template.render_components(identifier, callbacks, keywords)
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
