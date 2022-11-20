import json
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Union, cast

import discord
import discord.types.embed
import discord.ui as ui

from qalib.renderers.file_renderers._item_wrappers import create_button
from qalib.renderers.file_renderers.renderer import Renderer
from qalib.utils import colours


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
    def _render_attribute(element: Dict[str, str], attribute, **kwargs) -> str:
        if (value := element.get(attribute)) is None:
            return ""
        if isinstance(element[attribute], str):
            return value.format(**kwargs)
        return value

    def _render_timestamp(self, timestamp: Optional[Dict[str, str]], **kwargs) -> Optional[datetime]:
        if timestamp is not None:

            date = self._render_attribute(timestamp, "timestamp", **kwargs)
            date_format = self._render_attribute(timestamp, "format", **kwargs)
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(date, date_format) if date != "" else None

    def _render_author(self, author: Dict[str, str], **kwargs) -> Optional[dict]:
        return {
            "name": self._render_attribute(author, "name", **kwargs),
            "url": self._render_attribute(author, "url", **kwargs),
            "icon_url": self._render_attribute(author, "icon", **kwargs)
        }

    def _render_footer(self, footer: Dict[str, str], **kwargs) -> Optional[dict]:
        return {
            "text": self._render_attribute(footer, "text", **kwargs),
            "icon_url": self._render_attribute(footer, "icon", **kwargs)
        }

    def _render_fields(self, fields: List[Dict[str, str]], **kwargs) -> List[dict]:
        return [{"name": self._render_attribute(field, "name", **kwargs),
                 "value": self._render_attribute(field, "text").format(**kwargs),
                 "inline": self._render_attribute(field, "inline", **kwargs) == "True"}
                for field in fields]

    def set_menu(self, key: str):
        self._data = self._data[key]

    @property
    def size(self) -> int:
        return len(self._data)

    @property
    def keys(self) -> List[str]:
        return list(self._data.keys())

    @staticmethod
    def _render_emoji(emoji_element: Dict[str, str], **kwargs) -> Optional[Dict[str, str]]:
        emoji = {}
        if "name" in emoji_element:
            emoji["name"] = JSONRenderer._render_attribute(emoji_element, "name", **kwargs)
        if "id" in emoji_element:
            emoji["id"] = JSONRenderer._render_attribute(emoji_element, "id", **kwargs)
        if "animated" in emoji_element:
            animated = JSONRenderer._render_attribute(emoji_element, "animated", **kwargs)
            emoji["animated"] = animated if type(animated) == bool else animated.lower() == "true"
        return (None, emoji)[len(emoji) > 0]

    def _extract_attributes(self, element: Dict[str, Any], **kwargs) -> Dict[str, Union[str, Dict[str, str]]]:
        return {attribute: self._render_attribute(element, attribute, **kwargs) for attribute in element.keys()}

    def _render_button(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Callable],
            **kwargs
    ) -> ui.Item:

        emoji = self._render_emoji(component.pop("emoji"), **kwargs) if "emoji" in component else None

        attributes = self._extract_attributes(component, **kwargs)
        if emoji is not None:
            attributes["emoji"] = emoji

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def render_component(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Callable],
            **kwargs
    ) -> ui.Item:
        if (component_type := component.pop("type")) == "button":
            return self._render_button(component, callback, **kwargs)

        raise ValueError(f"Unknown component type: {component_type}")

    def render_components(self, identifier: str, callables: Dict[str, Callable], **kwargs) -> Optional[List[ui.Item]]:
        """

        Args:
            callables:
            identifier:
            **kwargs:

        Returns:

        """

        view = self._get_raw_embed(identifier).get("view")
        if view is None:
            return None

        return [self.render_component(component, callables.get(key), **kwargs) for key, component in view.items()]

    def render(self, identifier: str, **kwargs) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           identifier (str): key name of the embed

        Returns:
            Embed: Embed Object, discord compatible.
        """

        raw_embed = self._get_raw_embed(identifier)

        def render(attribute: str) -> str:
            return self._render_attribute(raw_embed, attribute, **kwargs)

        embed_type: discord.types.embed.EmbedType = "rich"
        if cast(discord.types.embed.EmbedType, given_type := render("type")) != "":
            embed_type = cast(discord.types.embed.EmbedType, given_type)

        embed = discord.Embed(title=render("title"),
                              colour=colours.get_colour(
                                  colour if (colour := render("colour")) != "" else render("color")),
                              type=embed_type,
                              url=render("url"),
                              description=render("description"),
                              timestamp=self._render_timestamp(raw_embed.get("timestamp"), **kwargs)
                              )

        for field in self._render_fields(raw_embed["fields"], **kwargs):
            embed.add_field(**field)

        if (footer := raw_embed.get("footer")) is not None:
            embed.set_footer(**self._render_footer(footer, **kwargs))

        embed.set_thumbnail(url=self._render_attribute(raw_embed, "thumbnail", **kwargs))
        embed.set_image(url=self._render_attribute(raw_embed, "image", **kwargs))

        if (author := raw_embed.get("author")) is not None:
            embed.set_author(**self._render_author(author, **kwargs))

        return embed
