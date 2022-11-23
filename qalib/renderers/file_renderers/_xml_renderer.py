from datetime import datetime
from typing import Optional, List, Dict, Callable, Any, cast
from xml.etree import ElementTree as ElementTree

import discord
import discord.types.embed
import discord.ui as ui

from qalib.renderers.file_renderers._item_wrappers import create_button, create_select
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
    def _render_element(element: ElementTree.Element, keywords: Dict[str, Any]):
        if element is None:
            return ""
        return element.text.format(**keywords)

    @staticmethod
    def _render_attribute(element: ElementTree.Element, attribute: str, keywords: Dict[str, Any]):
        if (value := element.get(attribute)) is None:
            return ""
        return value.format(**keywords)

    def _render_timestamp(self, timestamp_element: ElementTree.Element, keywords: Dict[str, Any]) -> Optional[datetime]:
        if timestamp_element is not None:
            timestamp = self._render_element(timestamp_element, keywords)
            date_format = self._render_attribute(timestamp_element, "format", keywords)
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(timestamp, date_format) if timestamp != "" else None

    def _render_author(self, author_element: ElementTree.Element, keywords: Dict[str, Any]) -> Optional[dict]:
        return {
            "name": self._render_element(author_element.find("name"), keywords),
            "url": self._render_element(author_element.find("url"), keywords),
            "icon_url": self._render_element(author_element.find("icon"), keywords)
        }

    def _render_footer(self, footer_element: ElementTree.Element, keywords: Dict[str, Any]) -> Optional[dict]:
        return {
            "text": self._render_element(footer_element.find("text"), keywords),
            "icon_url": self._render_element(footer_element.find("icon"), keywords)
        }

    def _render_fields(self, fields_element: ElementTree.Element, keywords: Dict[str, Any]) -> List[dict]:
        return [{"name": self._render_attribute(field, "name", keywords),
                 "value": self._render_element(field, keywords),
                 "inline": self._render_attribute(field, "inline", keywords) == "True"}
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
    def _pop_component(component: ElementTree.Element, key: str) -> Optional[ElementTree.Element]:
        component.remove(child_component := component.find(key))
        return child_component

    @staticmethod
    def _render_emoji(emoji_element: ElementTree.Element, keywords) -> Optional[Dict[str, str]]:
        emoji = {}
        if (name := emoji_element.find("name")) is not None:
            emoji["name"] = XMLRenderer._render_element(name, keywords)
        if (identifier := emoji_element.find("id")) is not None:
            emoji["id"] = XMLRenderer._render_element(identifier, keywords)
        if (animated := emoji_element.find("animated")) is not None:
            emoji["animated"] = XMLRenderer._render_element(animated, keywords) == "True"
        return (None, emoji)[len(emoji) > 0]

    def _extract_elements(self, tree: ElementTree.Element, keywords) -> Dict[str, Any]:
        return {element.tag: self._render_element(element, keywords) for element in tree}

    def _render_button(
            self,
            component: ElementTree.Element,
            callback: Optional[Callable],
            keywords: Dict[str, Any]
    ) -> ui.Button:
        """Renders a button based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The button to render, contains the template.
            callback (Optional[Callable]): The callback to use if the user interacts with this button.
            keywords (Dict[str, Any]): The values to format the template with.

        Returns (ui.Button): The rendered button.
        """
        emoji_component = self._pop_component(component, "emoji")
        attributes = self._extract_elements(component, keywords)
        if emoji_component is not None:
            attributes["emoji"] = self._render_emoji(emoji_component, keywords)

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def _render_options(self, raw_options: ElementTree.Element, keywords: Dict[str, Any]) -> List[discord.SelectOption]:
        """Renders a list of options based on the template in the element, and formatted values given by the keywords.

        Args:
            raw_options (ElementTree.Element): The options to render, contains the template.
            keywords (Dict[str, Any]): The values to format the template with.

        Returns (List[discord.SelectOption]): The rendered options.
        """
        options = []
        for option in raw_options:
            emoji_component = self._pop_component(raw_options, "emoji")
            option_attributes = self._extract_elements(option, keywords)
            if emoji_component is not None:
                option_attributes["emoji"] = self._render_emoji(emoji_component, keywords)
            options.append(discord.SelectOption(**option_attributes))
        return options

    def _render_select(
            self,
            component: ElementTree.Element,
            callback: Optional[Callable],
            keywords: Dict[str, Any]
    ) -> ui.Select:
        """Renders a select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The select to render, contains the template.
            callback (Optional[Callable]): The callback to use if the user interacts with this select.
            keywords (Dict[str, Any]): The values to format the template with.

        Returns (ui.Select): The rendered select.
        """
        options = self._render_options(self._pop_component(component, "options"), keywords)

        attributes = self._extract_elements(component, keywords)
        attributes["options"] = options

        select: ui.Select = create_select(**attributes)
        select.callback = callback
        return select

    def render_component(
            self,
            component: ElementTree.Element,
            callback: Optional[Callable],
            keywords: Dict[str, Any]
    ) -> ui.Item:
        """Renders a component based on the tag in the element.

        Args:
            component (ElementTree.Element): The component to render, contains all template.
            callback (Optional[Callable]): The callback to use if the user interacts with this component.
            keywords (Dict[str, Any]): The keywords to use to format the component before rendering.

        Returns (discord.ui.Item): The rendered component.
        """

        return {
            "button": self._render_button,
            "select": self._render_select
        }[component.tag](component, callback, keywords)

    def render_components(
            self,
            identifier: str,
            callables: Dict[str, Callable],
            keywords: Optional[Dict[str, Any]] = None
    ) -> Optional[List[ui.Item]]:
        """Renders a list of components based on the identifier given.

        Args:
            keywords (Optional[Dict[str, Any]]): The keywords to use to format the components before rendering.
            callables (Dict[str, Callable]): The callbacks to use if the user interacts with the components.
            identifier (str): The identifier of the components to render.

        Returns (Optional[List[discord.ui.Item]]): The rendered components.
        """
        view = self._get_raw_embed(identifier).find("view")
        if view is None:
            return None

        return [
            self.render_component(
                component,
                callables.get(key) if (key := self._render_attribute(component, "key", keywords)) else None,
                keywords
            )
            for component in view
        ]

    def render(self, identifier: str, keywords: Optional[Dict[str, Any]] = None) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance.

        Args:
           identifier (str): key name of the embed.
           keywords (Optional[Dict[str, Any]]): keywords to format the template with.

        Returns:
            Embed: Embed Object, discord compatible.
        """

        raw_embed = self._get_raw_embed(identifier)

        def render(name: str):
            return self._render_element(raw_embed.find(name), keywords)

        embed_type: discord.types.embed.EmbedType = "rich"
        if cast(discord.types.embed.EmbedType, given_type := render("type")) != "":
            embed_type = cast(discord.types.embed.EmbedType, given_type)

        embed = discord.Embed(
            title=render("title"),
            colour=colours.get_colour(render("colour")),
            type=embed_type,
            url=render("url"),
            description=render("description"),
            timestamp=self._render_timestamp(raw_embed.find("timestamp"), keywords)
        )

        for field in self._render_fields(raw_embed.find("fields"), keywords):
            embed.add_field(**field)

        if (footer := raw_embed.find("footer")) is not None:
            embed.set_footer(**self._render_footer(footer, keywords))

        embed.set_thumbnail(url=self._render_element(raw_embed.find("thumbnail"), keywords))
        embed.set_image(url=self._render_element(raw_embed.find("image"), keywords))

        if (author := raw_embed.find("author")) is not None:
            embed.set_author(**self._render_author(author, keywords))

        return embed
