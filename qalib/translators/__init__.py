from dataclasses import dataclass, asdict
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


@dataclass
class BaseMessage:
    content: Optional[str]
    embed: Optional[discord.Embed]
    embeds: Optional[Sequence[discord.Embed]]
    file: Optional[discord.File]
    files: Optional[Sequence[discord.File]]
    view: Optional[discord.ui.View]
    tts: Optional[bool]
    ephemeral: Optional[bool]
    allowed_mentions: Optional[discord.AllowedMentions]
    suppress_embeds: Optional[bool]
    silent: Optional[bool]
    delete_after: Optional[float]

    def dict(self) -> Dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if value is not None}

    def __iter__(self):
        # Order is preserved in Python 3.7+: https://mail.python.org/pipermail/python-dev/2017-December/151283.html
        for value in self.__dict__.values():
            if value is None:
                continue
            yield value


@dataclass
class ContextMessage(BaseMessage):
    stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]]
    nonce: Optional[Union[str, int]]
    reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]]
    mention_author: Optional[bool]


@dataclass
class InteractionMessage(BaseMessage):
    silent: Optional[bool]


# pylint: disable=too-many-instance-attributes
@dataclass
class Message(BaseMessage):
    """Dataclass that represents the display of the message.

    Look at https://discordpy.readthedocs.io/en/latest/api.html?highlight=send#discord.abc.Messageable.send
    """
    stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]]
    nonce: Optional[Union[str, int]]
    reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]]
    mention_author: Optional[bool]
    silent: Optional[bool]

    def convert_to_context_message(self) -> ContextMessage:
        return ContextMessage(
            content=self.content,
            embed=self.embed,
            embeds=self.embeds,
            file=self.file,
            files=self.files,
            view=self.view,
            tts=self.tts,
            ephemeral=self.ephemeral,
            allowed_mentions=self.allowed_mentions,
            suppress_embeds=self.suppress_embeds,
            silent=self.silent,
            delete_after=self.delete_after,
            stickers=self.stickers,
            nonce=self.nonce,
            reference=self.reference,
            mention_author=self.mention_author,
        )

    def convert_to_interaction_message(self) -> InteractionMessage:
        return InteractionMessage(
            content=self.content,
            embed=self.embed,
            embeds=self.embeds,
            file=self.file,
            files=self.files,
            view=self.view,
            tts=self.tts,
            ephemeral=self.ephemeral,
            allowed_mentions=self.allowed_mentions,
            suppress_embeds=self.suppress_embeds,
            silent=self.silent,
            delete_after=self.delete_after,
        )