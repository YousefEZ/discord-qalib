from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, Optional, Sequence, TypeVar, Union

import discord
from discord.abc import Snowflake

V_co = TypeVar("V_co", bound=discord.ui.View, covariant=True)

Callback = Callable[[discord.Interaction], Awaitable[None]]
CallbackMethod = Callable[[discord.ui.Item[V_co], discord.Interaction], Awaitable[None]]


@dataclass
class DiscordIdentifier(Snowflake):
    # pylint: disable=invalid-name
    id: int


# pylint: disable=too-many-instance-attributes
@dataclass
class Message:
    """Dataclass that represents the display of the message.

    Look at https://discordpy.readthedocs.io/en/latest/api.html?highlight=send#discord.abc.Messageable.send
    """

    content: Optional[str]
    tts: Optional[bool]
    embed: Optional[discord.Embed]
    embeds: Optional[Sequence[discord.Embed]]
    file: Optional[discord.File]
    files: Optional[Sequence[discord.File]]
    stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]]
    delete_after: Optional[float]
    nonce: Optional[Union[str, int]]
    allowed_mentions: Optional[discord.AllowedMentions]
    reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]]
    mention_author: Optional[bool]
    view: Optional[discord.ui.View]
    suppress_embeds: Optional[bool]
    ephemeral: Optional[bool]

    def dict(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if value is not None}

    def __iter__(self):
        # Order is preserved in Python 3.7+: https://mail.python.org/pipermail/python-dev/2017-December/151283.html
        for value in self.__dict__.values():
            if value is None:
                continue
            yield value
