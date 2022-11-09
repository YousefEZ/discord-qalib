import xml.etree.ElementTree as ElementTree

from discord import Embed

from qalib.utils import colours


class Renderer:
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    def __init__(self, path: str):
        """Initialisation of the Renderer

        Args:
            path (str): path to the xml file containing the template embed
        """
        self.tree = ElementTree.parse(path)

    def get_raw_embed(self, identifier) -> ElementTree.Element:
        """Finds the embed specified by the identifier

        Args:
            identifier (str): name of the embed

        Returns:
            ElementTree.Element: the raw embed specified by the identifier
        """
        root = self.tree.getroot()

        for embed in root.findall('embed'):
            if embed.get("key") == identifier:
                return embed

        raise KeyError("Embed key not found")

    @staticmethod
    def extract_element(element):
        if element is None:
            return ""
        return element.text

    def render(self, identifier: str, **kwargs) -> Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           identifier (str): key name of the embed

        Returns:
            Embed: Embed Object, discord compatible.
        """

        raw_embed = self.get_raw_embed(identifier)

        colour = colours.get_colour(Renderer.extract_element(raw_embed.find("colour")).format(**kwargs))
        embed = Embed(title=Renderer.extract_element(raw_embed.find("title")).format(**kwargs), colour=colour)
        fields = raw_embed.find("fields")

        for field in fields.findall("field"):
            inline = field.get("inline") == "True"
            name = field.get("name").format(**kwargs)
            value = Renderer.extract_element(field).format(**kwargs)

            embed.add_field(name=name, value=value, inline=inline)

        embed.set_footer(text=Renderer.extract_element(raw_embed.find("footer_text")),
                         icon_url=Renderer.extract_element(raw_embed.find("footer_icon")))
        embed.set_thumbnail(url=Renderer.extract_element(raw_embed.find("thumbnail")))
        embed.set_image(url=Renderer.extract_element(raw_embed.find("image")))

        return embed
