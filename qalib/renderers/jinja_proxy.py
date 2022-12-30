from typing import Any, Coroutine, Dict, Optional, List

import discord
import jinja2

from qalib.renderers.file_renderers.jinja_renderer import JinjaXMLTemplate
from . import RendererProtocol


class JinjaProxy(RendererProtocol):
    """Jinja Renderer for embeds"""

    __slots__ = ("_template", "_environment")

    def __init__(self, template: str, environment: jinja2.Environment):
        self._template = template
        self._environment = environment

    def template(self, keywords: Optional[Dict[str, Any]] = None) -> JinjaXMLTemplate:
        if keywords is None:
            keywords = {}

        return JinjaXMLTemplate(self._template, self._environment, keywords)

    def render(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Coroutine]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> (discord.Embed, Optional[discord.ui.View]):

        template = self.template(keywords)
        return self.render_embed(identifier, keywords, template), self.render_view(identifier, callbacks, timeout,
                                                                                   keywords, template)

    def render_embed(
            self,
            identifier: str,
            keywords: Optional[Dict[str, Any]] = None,
            template: JinjaXMLTemplate = None
    ) -> discord.Embed:
        """Method that renders an embed from the Renderer

        Args:
            identifier (str): identifier of the embed
            keywords (Optional[Dict[str, Any]]): keywords that are used to format the embed

        Returns (discord.Embed): Embed object that is rendered from the Renderer
        """

        if template is None:
            template = self.template(keywords)

        return template.render(identifier)

    def render_view(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Coroutine]] = None,
            timeout: Optional[int] = 180,
            keywords: Optional[Dict[str, Any]] = None,
            template: Optional[JinjaXMLTemplate] = None
    ) -> Optional[discord.ui.View]:
        """Methods that renders a view from the Renderer

        Args:
            identifier (str): identifier of the embed
            callbacks (Optional[Dict[str, Coroutine]]): callbacks that are attached to the components of the view
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

    def size(self, keywords: Optional[Dict[str, Any]] = None) -> int:
        return self.template(keywords).size

    def keys(self, keywords: Optional[Dict[str, Any]] = None) -> List[str]:
        return self.template(keywords).keys
