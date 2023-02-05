from dataclasses import dataclass
from typing import Callable, Awaitable, Optional, Sequence, Union

import discord.ui
from discord import Embed, File, GuildSticker, StickerItem, AllowedMentions, MessageReference, PartialMessage, Message
from discord.utils import MISSING

Callback = Callable[[discord.Interaction], Awaitable[None]]


@dataclass
class Message:
    """NamedTuple that represents the display of the message.

    Look at https://discordpy.readthedocs.io/en/latest/api.html?highlight=send#discord.abc.Messageable.send
    """
    content: Optional[str] = MISSING
    tts: bool = MISSING
    embed: Optional[Embed] = MISSING
    embeds: Optional[Sequence[Embed]] = MISSING
    file: Optional[File] = MISSING
    files: Optional[Sequence[File]] = MISSING
    stickers: Optional[Sequence[Union[GuildSticker, StickerItem]]] = MISSING
    delete_after: Optional[float] = MISSING
    nonce: Optional[Union[str, int]] = MISSING
    allowed_mentions: Optional[AllowedMentions] = MISSING
    reference: Optional[Union[Message, MessageReference, PartialMessage]] = MISSING
    mention_author: Optional[bool] = MISSING
    view: Optional[discord.ui.View] = MISSING
    suppress_embeds: bool = MISSING
    ephemeral: bool = MISSING

    def __iter__(self):
        # Order is preserved in Python 3.7+: https://mail.python.org/pipermail/python-dev/2017-December/151283.html
        for value in self.__dict__.values():
            if value is MISSING:
                continue
            yield value

    def keys(self):
        for key, value in self.__dict__.items():
            if value is MISSING:
                continue
            yield key

    def __getitem__(self, item):
        return getattr(self, item)
