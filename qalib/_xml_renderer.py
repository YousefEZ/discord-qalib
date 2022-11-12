import xml.etree.ElementTree as ElementTree
from datetime import datetime
from typing import List, Optional

from discord import Embed

from qalib.utils import colours


class Renderer:
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    def __init__(self, path: str):
        """Initialisation of the Renderer

        Args:
            path (str): path to the xml file containing the template embed
        """
        self.root = ElementTree.parse(path).getroot()

    def get_raw_embed(self, identifier) -> ElementTree.Element:
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
    def render_element(element, **kwargs):
        if element is None:
            return ""
        return element.text.format(**kwargs)

    @staticmethod
    def render_attribute(element, attribute, **kwargs):
        if element.get(attribute) is None:
            return ""
        return element.get(attribute).format(**kwargs)

    def _render_timestamp(self, timestamp_element: ElementTree.Element, **kwargs) -> Optional[datetime]:
        if timestamp_element is not None:
            timestamp = self.render_element(timestamp_element, **kwargs)
            date_format = self.render_attribute(timestamp_element, "format", **kwargs)
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(timestamp, date_format) if timestamp != "" else None

    def _render_author(self, author_element: ElementTree.Element, **kwargs) -> Optional[dict]:
        return {
            "name": self.render_element(author_element.find("name"), **kwargs),
            "url": self.render_element(author_element.find("url"), **kwargs),
            "icon_url": self.render_element(author_element.find("icon"), **kwargs)
        }

    def _render_footer(self, footer_element: ElementTree.Element, **kwargs) -> Optional[dict]:
        return {
            "text": self.render_element(footer_element.find("text"), **kwargs),
            "icon_url": self.render_element(footer_element.find("icon"), **kwargs)
        }

    def _render_fields(self, fields_element: ElementTree.Element, **kwargs) -> List[dict]:
        return [{"name": self.render_attribute(field, "name", **kwargs),
                 "value": self.render_element(field).format(**kwargs),
                 "inline": self.render_attribute(field, "inline", **kwargs) == "True"}
                for field in fields_element.findall("field")]

    def render(self, identifier: str, **kwargs) -> Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           identifier (str): key name of the embed

        Returns:
            Embed: Embed Object, discord compatible.
        """

        raw_embed = self.get_raw_embed(identifier)

        def render(name: str):
            return self.render_element(raw_embed.find(name), **kwargs)

        embed = Embed(title=render("title"),
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

        embed.set_thumbnail(url=Renderer.render_element(raw_embed.find("thumbnail")))
        embed.set_image(url=Renderer.render_element(raw_embed.find("image")))

        if (author := raw_embed.find("author")) is not None:
            embed.set_author(**self._render_author(author, **kwargs))

        return embed


class MenuRenderer(Renderer):

    def __init__(self, path: str, identifier: str):
        super().__init__(path)

        for menu in self.root.findall("menu"):
            if menu.get("key") == identifier:
                self.root = menu
                break
        else:
            raise KeyError("Menu key not found")

    @property
    def number_of_pages(self) -> int:
        return len(self.root.findall("embed"))

    @property
    def keys(self) -> List[str]:
        return list(map(lambda element: element.get("key"), self.root.findall("embed")))
