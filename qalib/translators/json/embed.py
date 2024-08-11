from abc import ABC
from datetime import datetime
from typing import Optional, Union, List

import discord.types.embed

from qalib.translators.element.embed import EmbedAdapter
from qalib.translators.element.expansive import ExpansiveEmbedAdapter
from qalib.translators.element.types.embed import EmbedBaseAdapter, make_colour
from qalib.translators.json import components


class JSONEmbedBaseAdapter(EmbedBaseAdapter, ABC):
    def __init__(self, embed: components.Embed):
        self._embed = embed

    @property
    def title(self) -> str:
        return self._embed["title"]

    @property
    def description(self) -> Optional[str]:
        return self._embed.get("description")

    @property
    def type(self) -> discord.types.embed.EmbedType:
        return self._embed["type"] if "type" in self._embed else "rich"

    @property
    def colour(self) -> Union[discord.Colour, int]:
        if "colour" in self._embed:
            return make_colour(self._embed["colour"])
        if "color" in self._embed:
            return make_colour(self._embed["color"])
        raise ValueError("Missing colour/color value")

    @property
    def timestamp(self) -> Optional[datetime]:
        """Method to render a timestamp element into a datetime object

        Returns (Optional[datetime]): A datetime object
        """
        timestamp = self._embed.get("timestamp")
        if timestamp is None:
            return None

        date = timestamp["date"]
        date_format = timestamp.get("format", "%Y-%m-%d %H:%M:%S.%f")
        return datetime.strptime(date, date_format)

    @property
    def footer(self) -> Optional[components.Footer]:
        return self._embed.get("footer")

    @property
    def image(self) -> Optional[str]:
        return self._embed.get("image")

    @property
    def thumbnail(self) -> Optional[str]:
        return self._embed.get("thumbnail")

    @property
    def author(self) -> Optional[components.Author]:
        return self._embed.get("author")


class JSONEmbedAdapter(JSONEmbedBaseAdapter, EmbedAdapter):
    @property
    def fields(self) -> List[components.Field]:
        return self._embed.get("fields", [])


class JSONExpansiveEmbedAdapter(JSONEmbedBaseAdapter, ExpansiveEmbedAdapter):
    _embed: components.ExpansiveEmbed

    def __init__(self, embed: components.ExpansiveEmbed, page_number_key: Optional[str] = None):
        super().__init__(embed)
        ExpansiveEmbedAdapter.__init__(self, page_number_key)

    @property
    def field(self) -> components.Field:
        return self._embed["field"]
