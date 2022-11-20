from datetime import datetime
from typing import Optional, List, Dict, Callable, Any
from xml.etree import ElementTree as ElementTree

import discord
import discord.ui as ui

from qalib.renderers.file_renderers._item_wrappers import create_button
from qalib.renderers.file_renderers.renderer import Renderer
from qalib.utils import colours


class XMLRenderer(Renderer):
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    __slots__ = ("root",)

    def __init__(self, path: str):
        """Initialisation of the Renderer

        Args:
            path (str): path to the xml file containing the template embed
        """
        self.root = ElementTree.parse(path).getroot()

    def _get_raw_embed(self, identifier) -> ElementTree.Element:
        """Finds the embed specified by the identifier

        Args:
            identifier (str): name of the embed

        Returns:
            ElementTree.Element: the raw embed specified by the identifier
        """

        for embed in self.root.findall('embed'):
            if embed.get("key") == identifier:
                return embed

        raise KeyError("Embed key not found")

    @staticmethod
    def _render_element(element, **kwargs):
        if element is None:
            return ""
        return element.text.format(**kwargs)

    @staticmethod
    def _render_attribute(element: ElementTree.Element, attribute: str, **kwargs):
        if (value := element.get(attribute)) is None:
            return ""
        return value.format(**kwargs)

    def _render_timestamp(self, timestamp_element: ElementTree.Element, **kwargs) -> Optional[datetime]:
        if timestamp_element is not None:
            timestamp = self._render_element(timestamp_element, **kwargs)
            date_format = self._render_attribute(timestamp_element, "format", **kwargs)
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(timestamp, date_format) if timestamp != "" else None

    def _render_author(self, author_element: ElementTree.Element, **kwargs) -> Optional[dict]:
        return {
            "name": self._render_element(author_element.find("name"), **kwargs),
            "url": self._render_element(author_element.find("url"), **kwargs),
            "icon_url": self._render_element(author_element.find("icon"), **kwargs)
        }

    def _render_footer(self, footer_element: ElementTree.Element, **kwargs) -> Optional[dict]:
        return {
            "text": self._render_element(footer_element.find("text"), **kwargs),
            "icon_url": self._render_element(footer_element.find("icon"), **kwargs)
        }

    def _render_fields(self, fields_element: ElementTree.Element, **kwargs) -> List[dict]:
        return [{"name": self._render_attribute(field, "name", **kwargs),
                 "value": self._render_element(field).format(**kwargs),
                 "inline": self._render_attribute(field, "inline", **kwargs) == "True"}
                for field in fields_element.findall("field")]

    @property
    def size(self) -> int:
        return len(self.root.findall("embed"))

    @property
    def keys(self) -> List[str]:
        return list(map(lambda element: element.get("key"), self.root.findall("embed")))

    def set_menu(self, key: str):
        for menu in self.root.findall("menu"):
            if menu.get("key") == key:
                self.root = menu
                break
        else:
            raise KeyError("Menu key not found")

    @staticmethod
    def _render_emoji(emoji_element: ElementTree.Element, **kwargs) -> Optional[Dict[str, str]]:
        emoji = {}
        if (name := emoji_element.find("name")) is not None:
            emoji["name"] = XMLRenderer._render_element(name, **kwargs)
        if (id := emoji_element.find("id")) is not None:
            emoji["id"] = XMLRenderer._render_element(id, **kwargs)
        if (animated := emoji_element.find("animated")) is not None:
            emoji["animated"] = XMLRenderer._render_element(animated, **kwargs) == "True"
        return (None, emoji)[len(emoji) > 0]

    def _extract_elements(self, tree: ElementTree.Element, **kwargs) -> Dict[str, Any]:
        return {element.tag: self._render_element(element, **kwargs) for element in tree}

    def _render_button(self, component: ElementTree.Element, callback: Optional[Callable], **kwargs) -> ui.Button:
        component.remove(emoji_component := component.find("emoji"))

        attributes = self._extract_elements(component, **kwargs)
        if emoji_component is not None:
            attributes["emoji"] = self._render_emoji(emoji_component, **kwargs)

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def render_component(self, component: ElementTree.Element, callback: Optional[Callable], **kwargs) -> ui.Item:

        if component.tag == "button":
            return self._render_button(component, callback, **kwargs)

        raise ValueError(f"Unknown component type: {component.tag}")

    def render_components(self, identifier: str, callables: Dict[str, Callable], **kwargs) -> Optional[List[ui.Item]]:
        """

        Args:
            callables:
            identifier:

        Returns:

        """
        view = self._get_raw_embed(identifier).find("view")
        if view is None:
            return None

        return [
            self.render_component(
                component,
                callables.get(key) if (key := self._render_attribute(component, "key", **kwargs)) else None,
                **kwargs
            )
            for component in view
        ]

    def render(self, identifier: str, **kwargs) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           identifier (str): key name of the embed

        Returns:
            Embed: Embed Object, discord compatible.
        """

        raw_embed = self._get_raw_embed(identifier)

        def render(name: str):
            return self._render_element(raw_embed.find(name), **kwargs)

        embed = discord.Embed(title=render("title"),
                              colour=colours.get_colour(render("colour")),
                              type=embed_type if (embed_type := render("type")) != "" else "rich",
                              url=render("url"),
                              description=render("description"),
                              timestamp=self._render_timestamp(raw_embed.find("timestamp"), **kwargs)
                              )

        for field in self._render_fields(raw_embed.find("fields"), **kwargs):
            embed.add_field(**field)

        if (footer := raw_embed.find("footer")) is not None:
            embed.set_footer(**self._render_footer(footer, **kwargs))

        embed.set_thumbnail(url=self._render_element(raw_embed.find("thumbnail"), **kwargs))
        embed.set_image(url=self._render_element(raw_embed.find("image"), **kwargs))

        if (author := raw_embed.find("author")) is not None:
            embed.set_author(**self._render_author(author, **kwargs))

        return embed
