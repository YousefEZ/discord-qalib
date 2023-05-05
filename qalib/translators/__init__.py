from dataclasses import dataclass, fields
from typing import Any, Awaitable, Callable, Dict, Optional, Sequence, TypeVar, Union, TypedDict

import discord
from discord.abc import Snowflake
from typing_extensions import ParamSpec

V_co = TypeVar("V_co", bound=discord.ui.View, covariant=True)

M = TypeVar("M")
N = TypeVar("N")
P = ParamSpec("P")

Callback = Callable[[discord.Interaction], Awaitable[None]]
CallbackMethod = Callable[[discord.ui.Item[V_co], discord.Interaction], Awaitable[None]]


@dataclass
class DiscordIdentifier(Snowflake):
    # pylint: disable=invalid-name
    id: int


@dataclass
class Base:
    def dict(self) -> Dict[str, Any]:
        return {key.name: attr for key in fields(self) if (attr := getattr(self, key.name)) is not None}


@dataclass
class BaseEditMessage(Base):
    content: Optional[str] = None
    embed: Optional[discord.Embed] = None
    attachments: Optional[Sequence[Union[discord.Attachment, discord.File]]] = None
    delete_after: Optional[float] = None
    allowed_mentions: Optional[discord.AllowedMentions] = None
    view: Optional[discord.ui.View] = None


# pylint: disable= too-many-instance-attributes
@dataclass
class BaseMessage(Base):
    content: Optional[str] = None
    embed: Optional[discord.Embed] = None
    embeds: Optional[Sequence[discord.Embed]] = None
    file: Optional[discord.File] = None
    files: Optional[Sequence[discord.File]] = None
    view: Optional[discord.ui.View] = None
    tts: Optional[bool] = None
    ephemeral: Optional[bool] = None
    allowed_mentions: Optional[discord.AllowedMentions] = None
    suppress_embeds: Optional[bool] = None
    delete_after: Optional[float] = None

    def as_edit(self) -> BaseEditMessage:
        raise NotImplementedError


@dataclass
class EditContextMessage(BaseEditMessage):
    suppress: Optional[bool] = None


@dataclass
class ContextMessage(BaseMessage):
    stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]] = None
    nonce: Optional[Union[str, int]] = None
    reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]] = None
    mention_author: Optional[bool] = None

    def as_edit(self) -> EditContextMessage:
        return EditContextMessage(
            content=self.content,
            embed=self.embed,
            attachments=self.files,
            suppress=self.suppress_embeds,
            delete_after=self.delete_after,
            allowed_mentions=self.allowed_mentions,
            view=self.view
        )


@dataclass
class InteractionEditMessage(BaseEditMessage):
    pass


@dataclass
class InteractionMessage(BaseMessage):
    silent: Optional[bool] = None

    def as_edit(self) -> InteractionEditMessage:
        return InteractionEditMessage(
            content=self.content,
            embed=self.embed,
            attachments=self.files,
            delete_after=self.delete_after,
            allowed_mentions=self.allowed_mentions,
            view=self.view
        )


class MessageTyped(TypedDict):
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
    stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]]
    nonce: Optional[Union[str, int]]
    reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]]
    mention_author: Optional[bool]


# pylint: disable=too-many-instance-attributes
@dataclass
class Message(BaseMessage):
    """Dataclass that represents the display of the message.

    Look at https://discordpy.readthedocs.io/en/latest/api.html?highlight=send#discord.abc.Messageable.send
    """

    stickers: Optional[Sequence[Union[discord.GuildSticker, discord.StickerItem]]] = None
    nonce: Optional[Union[str, int]] = None
    reference: Optional[Union[discord.Message, discord.MessageReference, discord.PartialMessage]] = None
    mention_author: Optional[bool] = None
    silent: Optional[bool] = None

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

    def as_edit(self) -> InteractionEditMessage:
        raise NotImplementedError
