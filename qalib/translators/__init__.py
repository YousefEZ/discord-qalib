from typing import NamedTuple

import discord.ui


class Display(NamedTuple):
    """NamedTuple that represents the display of the message."""
    embed: discord.Embed
    view: discord.ui.View
