import json
from datetime import datetime
from functools import partial
from typing import Dict, List, Optional, Coroutine, Any, Union, cast, Type

import discord
import discord.types.embed
import discord.ui as ui

import qalib.renderers.file_renderers._item_wrappers
from qalib.renderers.file_renderers._item_wrappers import *
from qalib.renderers.file_renderers.renderer import Renderer


class JSONRenderer(Renderer):
    __slots__ = ("_data",)

    def __init__(self, path: str):
        with open(path, "r") as file:
            self._data: Dict[str, Any] = json.load(file)

    def _get_raw_embed(self, identifier) -> Dict[str, Any]:
        """Finds the embed specified by the identifier

        Args:
            identifier (str): name of the embed

        Returns:
            ElementTree.Element: the raw embed specified by the identifier
        """
        return self._data[identifier]

    @staticmethod
    def _render_attribute(element: Dict[str, str], attribute, keywords: Dict[str, Any]) -> str:
        if (value := element.get(attribute)) is None:
            return ""
        if isinstance(element[attribute], str):
            return value.format(**keywords)
        return value

    def _render_timestamp(self, timestamp: Optional[Dict[str, str]], keywords: Dict[str, Any]) -> Optional[datetime]:
        if timestamp is not None:

            date = self._render_attribute(timestamp, "timestamp", keywords)
            date_format = self._render_attribute(timestamp, "format", keywords)
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(date, date_format) if date != "" else None

    def _render_author(self, author: Dict[str, str], keywords: Dict[str, Any]) -> Optional[dict]:
        return {
            "name": self._render_attribute(author, "name", keywords),
            "url": self._render_attribute(author, "url", keywords),
            "icon_url": self._render_attribute(author, "icon", keywords)
        }

    def _render_footer(self, footer: Dict[str, str], keywords: Dict[str, Any]) -> Optional[dict]:
        return {
            "text": self._render_attribute(footer, "text", keywords),
            "icon_url": self._render_attribute(footer, "icon", keywords)
        }

    def _render_fields(self, fields: List[Dict[str, str]], keywords: Dict[str, Any]) -> List[dict]:
        return [{
            "name": self._render_attribute(field, "name", keywords),
            "value": self._render_attribute(field, "text", keywords),
            "inline": self._render_attribute(field, "inline", keywords).lower() == "true"}
            for field in fields
        ]

    def set_root(self, key: str):
        self._data = self._data[key]

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def keys(self) -> List[str]:
        return list(self._data.keys())

    @staticmethod
    def _render_emoji(emoji_element: Dict[str, str], keywords: Dict[str, Any]) -> Optional[Dict[str, str]]:
        emoji = {}
        if "name" in emoji_element:
            emoji["name"] = JSONRenderer._render_attribute(emoji_element, "name", keywords)
        if "id" in emoji_element:
            emoji["id"] = JSONRenderer._render_attribute(emoji_element, "id", keywords)
        if "animated" in emoji_element:
            animated = JSONRenderer._render_attribute(emoji_element, "animated", keywords)
            emoji["animated"] = animated if type(animated) == bool else animated.lower() == "true"
        return (None, emoji)[len(emoji) > 0]

    @staticmethod
    def _extract_attributes(element: Dict[str, Any], keywords: Dict[str, Any]) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            attribute: JSONRenderer._render_attribute(element, attribute, keywords) for attribute in element.keys()
        }

    def _render_button(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Coroutine],
            keywords: Dict[str, Any]
    ) -> ui.Button:
        """Renders a button from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Coroutine]): the callback to be called when the button is pressed
            keywords (Dict[str, Any]): the keywords to be used when rendering the button's attributes

        Returns (ui.Item): the rendered button
        """

        emoji = self._render_emoji(component.pop("emoji"), keywords) if "emoji" in component else None

        attributes = self._extract_attributes(component, keywords)
        if emoji is not None:
            attributes["emoji"] = make_emoji(emoji)

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def _render_options(
            self,
            raw_options: List[Dict[str, Union[str, str]]],
            keywords: Dict[str, Any]
    ) -> List[discord.SelectOption]:
        """Renders the options for a select menu

        Args:
            raw_options (List[Dict[str, Union[str, str]]]): the raw options to be rendered
            keywords (Dict[str, Any]): the keywords to be used when rendering the options' attributes

        Returns (List[discord.SelectOption]): the rendered options
        """
        options = []
        for option in raw_options:
            emoji = self._render_emoji(option.pop("emoji"), keywords) if "emoji" in option else None
            attributes = self._extract_attributes(option, keywords)

            if emoji is not None:
                attributes["emoji"] = make_emoji(emoji)

            options.append(discord.SelectOption(**attributes))
        return options

    def _render_channel_select(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Coroutine],
            keywords: Dict[str, Any]
    ) -> ui.ChannelSelect:
        """Renders a select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Coroutine]): the callback to be called when the select menu is pressed
            keywords (Dict[str, Any]): the keywords to be used when rendering the select menu's attributes

        Returns (ui.Item): the rendered channel select menu
        """

        channel_types: List[str] = component.pop("channel_types")

        attributes: Dict[str, Any] = self._extract_attributes(component, keywords)
        if channel_types is not None:
            attributes["channel_types"] = make_channel_types(channel_types)

        select: ui.ChannelSelect = create_channel_select(**attributes)
        select.callback = callback
        return select

    def _render_select(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Coroutine],
            keywords: Dict[str, Any]
    ) -> ui.Select:
        """Renders a select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Coroutine]): the callback to be called when the select menu is pressed
            keywords (Dict[str, Any]): the keywords to be used when rendering the select menu's attributes

        Returns (ui.Item): the rendered select menu
        """

        options = self._render_options(component.pop("options"), keywords)
        attributes: Dict[str, Any] = self._extract_attributes(component, keywords)
        attributes["options"] = options

        select: ui.Select = create_select(**attributes)
        select.callback = callback
        return select

    def _render_type_select(
            self,
            select_type: Type[T],
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Coroutine],
            keywords: Dict[str, Any]
    ) -> T:
        """Renders a type select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Coroutine]): the callback to be called it is selected from the select menu
            keywords (Dict[str, Any]): the keywords to be used when rendering the select menu's attributes

        Returns (ui.Item): the rendered role select menu
        """

        attributes: Dict[str, Any] = self._extract_attributes(component, keywords)

        select: T = create_type_select(select_type, **attributes)
        select.callback = callback
        return select

    def _render_text_input(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Coroutine],
            keywords: Dict[str, Any]
    ) -> ui.TextInput:
        """Renders a text input form the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Coroutine]): the callback to be called when the text is submitted
            keywords (Dict[str, Any]): the keywords to be used when rendering te text input.

        Returns (ui.TextInput): the rendered text input block.
        """

        attributes: Dict[str, Any] = self._extract_attributes(component, keywords)

        text_input: ui.TextInput = create_text_input(**attributes)
        text_input.callback = callback
        return text_input

    def render_component(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Coroutine],
            keywords: Dict[str, Any]
    ) -> ui.Item:
        """ Renders a component from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Coroutine]): the callback to be called when the user interacts with the component
            keywords (Dict[str, Any]): the keywords to be used when rendering the component's attributes

        Returns (ui.Item): the rendered component
        """
        return {
            "button": self._render_button,
            "select": self._render_select,
            "channel_select": self._render_channel_select,
            "role_select": partial(self._render_type_select, ui.RoleSelect),
            "user_select": partial(self._render_type_select, ui.UserSelect),
            "mentionable_select": partial(self._render_type_select, ui.MentionableSelect),
            "text_input": self._render_text_input
        }[component.pop("type")](component, callback, keywords)

    def render_components(
            self,
            identifier: str,
            callables: Dict[str, Coroutine],
            keywords: Dict[str, Any]
    ) -> Optional[List[ui.Item]]:
        """Renders the components specified by the identifier

        Args:
            identifier (str): the name of the embed containing the components to be rendered
            callables (Dict[str, Coroutine]): the callbacks to be called when the user interacts with the components
            keywords (Optional[Dict[str, Any]]): the keywords to be used when rendering the components' attributes

        Returns (Optional[List[ui.Item]]): the rendered components
        """

        view = self._get_raw_embed(identifier).get("view")
        if view is None:
            return None

        return [self.render_component(component, callables.get(key, ui.Item.callback), keywords) for key, component in
                view.items()]

    def render(self, identifier: str, keywords: Optional[Dict[str, Any]] = None) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           identifier (str): key name of the embed
           keywords (Optional[Dict[str, Any]]): keywords to be used when rendering the embed to format text.

        Returns:
            Embed: Embed Object, discord compatible.
        """

        raw_embed = self._get_raw_embed(identifier)

        def render(attribute: str) -> str:
            return self._render_attribute(raw_embed, attribute, keywords)

        embed_type: discord.types.embed.EmbedType = "rich"
        if cast(discord.types.embed.EmbedType, given_type := render("type")) != "":
            embed_type = cast(discord.types.embed.EmbedType, given_type)

        embed = discord.Embed(
            title=render("title"),
            colour=qalib.renderers.file_renderers._item_wrappers.make_colour(
                colour if (colour := render("colour")) != "" else render("color")),
            type=embed_type,
            url=render("url"),
            description=render("description"),
            timestamp=self._render_timestamp(raw_embed.get("timestamp"), keywords)
        )

        for field in self._render_fields(raw_embed["fields"], keywords):
            embed.add_field(**field)

        if (footer := raw_embed.get("footer")) is not None:
            embed.set_footer(**self._render_footer(footer, keywords))

        embed.set_thumbnail(url=self._render_attribute(raw_embed, "thumbnail", keywords))
        embed.set_image(url=self._render_attribute(raw_embed, "image", keywords))

        if (author := raw_embed.get("author")) is not None:
            embed.set_author(**self._render_author(author, keywords))

        return embed
