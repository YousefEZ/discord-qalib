from typing import NamedTuple, Callable, Awaitable

import discord.ui

Callback = Callable[[discord.Interaction], Awaitable[None]]


class Message(NamedTuple):
    """NamedTuple that represents the display of the message."""
    embed: discord.Embed
    view: discord.ui.View
