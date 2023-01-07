from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Optional, List, Dict, Coroutine, Any, cast, Type
from xml.etree import ElementTree as ElementTree

import discord
import discord.types.embed
import discord.ui as ui

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Display
from qalib.translators.deserializer import Deserializer
from qalib.translators.parser import Parser
from qalib.translators.utils import *


class XMLParser(Parser):

    def __init__(self, source: str):
        """Initialisation of the XML Parser

        Keyword Arguments:
            source (str): the text of the XML file
        """
        self.root = ElementTree.fromstring(source)

    def get_embed(self, identifier: str) -> str:
        for embed in self.root.findall("embed"):
            if embed.get("key") == identifier:
                return ElementTree.tostring(embed, encoding='unicode', method='xml')
        raise KeyError(f"Embed with key {identifier} not found")

    def get_menu(self, identifier: str) -> str:
        for menu in self.root.findall("menu"):
            if menu.get("key") == identifier:
                return ElementTree.tostring(menu, encoding='unicode', method='xml')
        raise KeyError(f"Menu with key {identifier} not found")

    def template_embed(self, key: str, templater: TemplateEngine, keywords: Dict[str, Any]) -> str:
        return templater.template(self.get_embed(key), keywords)

    def template_menu(self, key: str, templater: TemplateEngine, keywords: Dict[str, Any]) -> str:
        return templater.template(self.get_menu(key), keywords)


class XMLDeserializer(Deserializer):
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    def deserialize(self, source: str, callables: Dict[str, Coroutine], **kw) -> Display:
        return self.compile_embed(ElementTree.fromstring(source), callables, kw)

    def compile_embed(
            self,
            embed_tree: ElementTree.Element,
            callables: Dict[str, Coroutine],
            kw: Dict[str, Any]
    ) -> Display:
        view_tree: ElementTree.Element = embed_tree.find("view")
        embed = self.render(embed_tree)
        view = ui.View(**kw) if view_tree is None else self._render_view(view_tree, callables, kw)
        return Display(embed, view)

    def deserialize_into_menu(self, source: str, callables: Dict[str, Coroutine], **kw) -> List[Display]:
        menu_tree: ElementTree = ElementTree.fromstring(source)
        return [self.compile_embed(embed, callables, kw) for embed in menu_tree.findall("embed")]

    def _render_view(
            self,
            raw_view: ElementTree.Element,
            callables: Dict[str, Coroutine],
            kw: Dict[str, Any]
    ) -> ui.View:
        view = ui.View(**kw)
        for component in self.render_components(raw_view, callables):
            view.add_item(component)
        return view

    @staticmethod
    def _render_element(element: ElementTree.Element) -> str:
        return "" if element is None else element.text

    @staticmethod
    def _render_attribute(element: ElementTree.Element, attribute: str) -> str:
        return "" if (value := element.get(attribute)) is None else value

    def _render_timestamp(self, timestamp_element: ElementTree.Element) -> Optional[datetime]:
        if timestamp_element is not None:
            timestamp = self._render_element(timestamp_element)
            date_format = self._render_attribute(timestamp_element, "format")
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(timestamp, date_format) if timestamp != "" else None

    def _render_author(self, author_element: ElementTree.Element) -> Optional[dict]:
        return {
            "name": self._render_element(author_element.find("name")),
            "url": self._render_element(author_element.find("url")),
            "icon_url": self._render_element(author_element.find("icon"))
        }

    def _render_footer(self, footer_element: ElementTree.Element) -> Optional[dict]:
        return {
            "text": self._render_element(footer_element.find("text")),
            "icon_url": self._render_element(footer_element.find("icon"))
        }

    def _render_fields(self, fields_element: ElementTree.Element) -> List[dict]:
        return [{"name": self._render_element(field.find("name")),
                 "value": self._render_element(field.find("value")),
                 "inline": self._render_attribute(field, "inline").lower() == "true"}
                for field in fields_element.findall("field")]

    def _pop_component(self, component: ElementTree.Element, key: str) -> Optional[ElementTree.Element]:
        """Pops a component from the given element, and returns it.

        Args:
            component (ElementTree.Element): The element to pop the component from.
            key (str): The key of the component to pop.

        Returns (Optional[ElementTree.Element]): The popped component, or None if it doesn't exist.
        """
        if (child_component := component.find(key)) is not None:
            component.remove(child_component)
        return child_component

    def _render_emoji(self, emoji_element: Optional[ElementTree.Element]) -> Optional[Dict[str, str]]:
        if emoji_element is None:
            return

        emoji = {}
        if (name := emoji_element.find("name")) is not None:
            emoji["name"] = self._render_element(name)
        if (identifier := emoji_element.find("id")) is not None:
            emoji["id"] = self._render_element(identifier)
        if (animated := emoji_element.find("animated")) is not None:
            emoji["animated"] = self._render_element(animated) == "True"
        return (None, emoji)[len(emoji) > 0]

    def _extract_elements(self, tree: ElementTree.Element) -> Dict[str, Any]:
        return {element.tag: self._render_element(element) for element in tree}

    def _render_button(self, component: ElementTree.Element, callback: Optional[Coroutine]) -> ui.Button:
        """Renders a button based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The button to render, contains the template.
            callback (Optional[Coroutine]): The callback to use if the user interacts with this button.

        Returns (ui.Button): The rendered button.
        """
        emoji_component = self._pop_component(component, "emoji")
        attributes = self._extract_elements(component)
        attributes["emoji"] = make_emoji(self._render_emoji(emoji_component))

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def _render_options(self, raw_options: Optional[ElementTree.Element]) -> List[discord.SelectOption]:
        """Renders a list of options based on the template in the element, and formatted values given by the keywords.

        Args:
            raw_options (ElementTree.Element): The options to render, contains the template.

        Returns (List[discord.SelectOption]): The rendered options.
        """
        options = []
        for option in (raw_options or []):
            emoji_component = self._pop_component(option, "emoji")
            option_attributes = self._extract_elements(option)
            option_attributes["emoji"] = make_emoji(self._render_emoji(emoji_component))
            options.append(discord.SelectOption(**option_attributes))
        return options

    def _render_select(
            self,
            component: ElementTree.Element,
            callback: Optional[Coroutine],
    ) -> ui.Select:
        """Renders a select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The select to render, contains the template.
            callback (Optional[Coroutine]): The callback to use if the user interacts with this select.

        Returns (ui.Select): The rendered select.
        """
        options = self._render_options(self._pop_component(component, "options"))

        attributes = self._extract_elements(component)
        attributes["options"] = options

        select: ui.Select = create_select(**attributes)
        select.callback = callback
        return select

    def _render_channel_select(self, component: ElementTree.Element, callback: Optional[Coroutine]) -> ui.ChannelSelect:
        """Renders a channel select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The channel select to render, contains the template.
            callback (Optional[Coroutine]): The callback to use if the user interacts with this channel select.

        Returns (ui.ChannelSelect): The rendered channel select.
        """
        channel_types: ElementTree.Element = self._pop_component(component, "channel_types")

        attributes = self._extract_elements(component)
        if channel_types is not None:
            attributes["channel_types"] = make_channel_types(list(map(
                lambda element: self._render_element(element),
                channel_types.findall("channel_type")
            )))

        select: ui.ChannelSelect = create_channel_select(**attributes)
        select.callback = callback
        return select

    def _render_type_select(
            self,
            select_type: Type[T],
            component: ElementTree.Element,
            callback: Optional[Coroutine],
    ) -> T:
        """Renders a type select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The type select to render, contains the template.
            callback (Optional[Coroutine]): The callback to use if the user interacts with this role select.

        Returns (ui.RoleSelect): The rendered role select.
        """
        attributes = self._extract_elements(component)

        select: ui.RoleSelect = create_type_select(select_type, **attributes)
        select.callback = callback
        return select

    def _render_text_input(self, component: ElementTree.Element, callback: (Optional[Coroutine])) -> ui.TextInput:
        """Renders a text input based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The text input to render, contains the template.
            callback (Optional[Coroutine]): The callback to use if the user interacts with this text input.

        Returns (ui.TextInput): The rendered text input.
        """
        attributes = self._extract_elements(component)

        text_input: ui.TextInput = create_text_input(**attributes)
        text_input.callback = callback
        return text_input

    def render_component(self, component: ElementTree.Element, callback: Optional[Coroutine]) -> ui.Item:
        """Renders a component based on the tag in the element.

        Args:
            component (ElementTree.Element): The component to render, contains all template.
            callback (Optional[Coroutine]): The callback to use if the user interacts with this component.

        Returns (discord.ui.Item): The rendered component.
        """

        return {
            "button": self._render_button,
            "select": self._render_select,
            "channel_select": self._render_channel_select,
            "text_input": self._render_text_input,
            "role_select": partial(self._render_type_select, ui.RoleSelect),
            "mentionable_select": partial(self._render_type_select, ui.MentionableSelect),
            "user_select": partial(self._render_type_select, ui.UserSelect),
        }[component.tag](component, callback)

    def render_components(
            self,
            view: ElementTree.Element,
            callables: Dict[str, Coroutine]
    ) -> List[ui.Item]:
        """Renders a list of components based on the identifier given.

        Args:
            view (ui.View): The raw view.
            callables (Dict[str, Coroutine]): The callbacks to use if the user interacts with the components.

        Returns (Optional[List[discord.ui.Item]]): The rendered components.
        """
        return [
            self.render_component(
                component,
                callables.get(self._render_attribute(component, "key"), ui.Item.callback),
            )
            for component in view
        ]

    def render(self, raw_embed: ElementTree.Element) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance.

        Args:
           raw_embed(ElementTree.Element): The element to render the embed from.

        Returns:
            Embed: Embed Object, discord compatible.
        """

        def render(name: str):
            return self._render_element(raw_embed.find(name))

        embed_type: discord.types.embed.EmbedType = "rich"
        if cast(discord.types.embed.EmbedType, given_type := render("type")) != "":
            embed_type = cast(discord.types.embed.EmbedType, given_type)

        embed = discord.Embed(
            title=render("title"),
            colour=make_colour(render("colour")),
            type=embed_type,
            url=render("url"),
            description=render("description"),
            timestamp=self._render_timestamp(raw_embed.find("timestamp"))
        )

        for field in self._render_fields(raw_embed.find("fields")):
            embed.add_field(**field)

        if (footer := raw_embed.find("footer")) is not None:
            embed.set_footer(**self._render_footer(footer))

        embed.set_thumbnail(url=self._render_element(raw_embed.find("thumbnail")))
        embed.set_image(url=self._render_element(raw_embed.find("image")))

        if (author := raw_embed.find("author")) is not None:
            embed.set_author(**self._render_author(author))

        return embed
