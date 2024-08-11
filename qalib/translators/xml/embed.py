from __future__ import annotations

import re
from abc import ABC
from datetime import datetime
from typing import Optional, List, get_args, cast
from xml.etree import ElementTree

import discord
from discord.types import embed as embed_types

from qalib.translators.element.embed import EmbedAdapter
from qalib.translators.element.expansive import ExpansiveEmbedAdapter
from qalib.translators.element.types.embed import Author, Footer, make_colour, Field


def filter_tabs(text: Optional[str]) -> str:
    if not text:
        return ""
    lines = text.split("\n")
    for base_line in lines:
        match = re.match(r"(\s*).*", base_line)
        assert match is not None, "Invalid line."
        grp = match.group(1)
        if grp:
            return "\n".join(line.replace(grp, "", 1) for line in lines)

    return "\n".join(lines)


class XMLBaseEmbedAdapter(EmbedAdapter, ABC):
    def __init__(self, raw_embed: ElementTree.Element):
        self._raw_embed = raw_embed

    @staticmethod
    def get_element_text(element: Optional[ElementTree.Element]) -> str:
        """Renders the given ElementTree.Element by returning its text.

        Args:
            element (ElementTree.Element): The element to render.

        Returns (str): The rendered element.
        """
        return "" if element is None or element.text is None else element.text

    @property
    def type(self) -> embed_types.EmbedType:
        """Renders the type from an ElementTree.Element.

        Returns (embed_types.EmbedType): The type of the embed.
        """
        embed_type = self._raw_embed.find("type")
        if embed_type is None:
            return "rich"
        embed_type_str = self.get_element_text(embed_type)
        assert embed_type_str in get_args(embed_types.EmbedType), f"Invalid embed type: {embed_type_str}"
        return cast(embed_types.EmbedType, embed_type_str)

    @property
    def timestamp(self) -> Optional[datetime]:
        """Renders the timestamp from an ElementTree.Element. Element may contain an attribute "format" which will be
        used to parse the timestamp.

        Returns (Optional[datetime]): A datetime object containing the timestamp.
        """
        timestamp_element = self._raw_embed.find("timestamp")
        if timestamp_element is None:
            return None

        timestamp = self.get_element_text(timestamp_element)
        date_format = timestamp_element.get("format", "")
        if date_format == "":
            date_format = "%Y-%m-%d %H:%M:%S.%f"
        return datetime.strptime(timestamp, date_format) if timestamp != "" else None

    @property
    def author(self) -> Optional[Author]:
        """Renders the author from an ElementTree.Element.

        Returns (Optional[dict]): A dictionary containing the raw author.
        """
        author_element = self._raw_embed.find("author")
        if author_element is None:
            return None
        return {
            "name": self.get_element_text(author_element.find("name")),
            "url": self.get_element_text(author_element.find("url")),
            "icon_url": self.get_element_text(author_element.find("icon")),
        }

    @property
    def footer(self) -> Optional[Footer]:
        """Renders the footer from an ElementTree.Element.

        Returns (Optional[dict]): A dictionary containing the raw footer.
        """
        footer_element = self._raw_embed.find("footer")
        if footer_element is None:
            return None
        return {
            "text": self.get_element_text(footer_element.find("text")),
            "icon_url": self.get_element_text(footer_element.find("icon")),
        }

    @property
    def image(self) -> Optional[str]:
        """Renders the image from an ElementTree.Element.

        Returns (Optional[str]): A string containing the raw image.
        """
        return image.text if (image := self._raw_embed.find("image")) is not None else None

    @property
    def thumbnail(self) -> Optional[str]:
        """Renders the thumbnail from an ElementTree.Element.

        Returns (Optional[str]): A string containing the raw thumbnail.
        """
        return thumbnail.text if (thumbnail := self._raw_embed.find("thumbnail")) is not None else None

    @property
    def title(self) -> str:
        """Renders the title from an ElementTree.Element.

        Returns (Optional[str]): A string containing the raw title.
        """
        return self.get_element_text(self._raw_embed.find("title"))

    @property
    def description(self) -> Optional[str]:
        """Renders the description from an ElementTree.Element.

        Returns (Optional[str]): A string containing the raw description.
        """
        return self.get_element_text(self._raw_embed.find("description"))

    @property
    def colour(self) -> discord.Colour | int:
        """Renders the color from an ElementTree.Element.

        Returns (Optional[int]): An integer containing the raw color.
        """
        return make_colour(
            self.get_element_text(self._raw_embed.find("color"))
            or self.get_element_text(self._raw_embed.find("colour"))
        )


class XMLEmbedAdapter(XMLBaseEmbedAdapter, EmbedAdapter):
    @property
    def fields(self) -> List[Field]:
        """Renders the fields from an ElementTree.Element.

        Returns (List[dict]): A list of dictionaries containing the raw fields.
        """
        fields_element = self._raw_embed.find("fields")
        return (
            []
            if fields_element is None
            else [
                {
                    "name": filter_tabs(self.get_element_text(field.find("name"))),
                    "value": filter_tabs(self.get_element_text(field.find("value"))),
                    "inline": field.get("inline", "").lower() == "true",
                }
                for field in fields_element.findall("field")
            ]
        )


class XMLExpansiveEmbedAdapter(XMLBaseEmbedAdapter, ExpansiveEmbedAdapter):
    def __init__(self, embed: ElementTree.Element, page_number_key: Optional[str] = None):
        super().__init__(embed)
        ExpansiveEmbedAdapter.__init__(self, page_number_key)

    @property
    def fields(self) -> List[Field]:
        return [self.field]

    @property
    def field(self) -> Field:
        """Renders the field from an ElementTree.Element.

        Returns (dict): A dictionary containing the raw field.
        """
        field_element = self._raw_embed.find("field")
        assert field_element is not None, "Expansive embed must contain a field element."
        return {
            "name": filter_tabs(self.get_element_text(field_element.find("name"))),
            "value": filter_tabs(self.get_element_text(field_element.find("value"))),
            "inline": field_element.get("inline", "").lower() == "true",
        }
