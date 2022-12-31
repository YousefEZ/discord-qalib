from typing import Any, Coroutine, Dict, Optional, List, Callable

import discord
import jinja2

from qalib.renderers.file_renderers.jinja_renderer import JinjaXMLTemplate
from . import RendererProtocol, Display, create_arrows


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
    ) -> Display:

        template = self.template(keywords)
        return Display(self.render_embed(identifier, keywords, template),
                       self.render_view(identifier, callbacks, timeout, keywords, template))

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

    def render_menu(self, callbacks: Optional[Dict[str, Callable]], keywords: Optional[Dict[str, Any]] = None,
                    timeout: Optional[int] = 180, **kwargs) -> Display:
        """This method is used to create a menu for the user to select from.

        Args:
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view
            timeout (Optional[int]): timeout of the view
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
        """
        template = JinjaXMLTemplate(self._template, self._environment, keywords)

        keys = template.keys

        def create_display_with_default_view(identifier: str) -> Display:
            embed = self.render_embed(identifier, template=template)
            view = self.render_view(identifier, callbacks, timeout, template=template)
            return Display(embed, discord.ui.View() if view is None else view)

        displays = [create_display_with_default_view(key) for key in keys]

        for i, display in enumerate(displays):
            arrow_left = displays[i - 1] if i > 0 else None
            arrow_right = displays[i + 1] if i + 1 < len(displays) else None

            for arrow in create_arrows(arrow_left, arrow_right, **kwargs):
                display.view.add_item(arrow)

        return displays[0]
