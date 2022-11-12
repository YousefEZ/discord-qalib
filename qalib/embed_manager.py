import discord.ext

from qalib._response_manager import ResponseManager
from qalib._xml_renderer import Renderer


class EmbedManager(ResponseManager):
    """EmbedManager object is responsible for handling messages that are to be sent to the client."""

    def __init__(self, ctx: discord.ext.commands.context, embed_xml: str):
        super().__init__(ctx, Renderer(embed_xml))
