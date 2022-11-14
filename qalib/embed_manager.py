import discord.ext

from qalib._response_manager import ResponseManager
from qalib.renderers.embed_renderer import EmbedRenderer


class EmbedManager(ResponseManager):
    """EmbedManager object is responsible for handling messages that are to be sent to the client."""

    def __init__(self, ctx: discord.ext.commands.context, path: str):
        super().__init__(ctx, EmbedRenderer(path))
