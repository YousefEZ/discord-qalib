from typing import NamedTuple, Callable, Awaitable

import discord.ui

Callback = Callable[[discord.Interaction], Awaitable[None]]


class Display(NamedTuple):
    """NamedTuple that represents the display of the message."""
    embed: discord.Embed
    view: discord.ui.View
