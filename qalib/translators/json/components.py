from __future__ import annotations

from typing import Literal, TypedDict, List, Union, Dict, Optional, TypeVar

import discord
import discord.types
import discord.types.embed
from typing_extensions import NotRequired

from qalib.translators.deserializer import Types
from qalib.translators.element.types.embed import Emoji, Field, Footer, Author
from qalib.translators.message_parsing import ButtonStyle, ChannelType, TextInputRaw, ButtonComponent

ComponentTypes = Literal[
    "button",
    "select",
    "channel_select",
    "role_select",
    "user_select",
    "mentionable_select",
    "text_input",
]


class Option(TypedDict):
    """This class is used to represent the blueprint of a select menu option."""

    label: str
    value: str
    description: str
    emoji: NotRequired[Emoji]
    default: bool


class Component(TypedDict):
    type: ComponentTypes


class Button(Component):
    """This class is used to represent the blueprint of a button."""

    custom_id: NotRequired[str]
    id: NotRequired[str]
    label: NotRequired[str]
    style: NotRequired[ButtonStyle]
    emoji: NotRequired[Emoji]
    url: NotRequired[str]
    disabled: NotRequired[bool]
    row: NotRequired[int]


class Select(Component):
    """This class is used to represent the blueprint of a select menu."""

    custom_id: NotRequired[str]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    options: NotRequired[List[Option]]
    row: NotRequired[int]


class CustomSelect(Component):
    """This class is used to represent the blueprint of a mentionable select menu."""

    custom_id: NotRequired[str]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    options: NotRequired[List[Option]]
    row: NotRequired[int]


class ChannelSelect(Component):
    """This class is used to represent the blueprint of a channel select menu."""

    custom_id: NotRequired[str]
    channel_types: NotRequired[List[ChannelType]]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    options: NotRequired[List[Option]]
    row: NotRequired[int]


class TextInput(TextInputRaw):
    type: ComponentTypes


ComponentType = Union[Button, Select, CustomSelect, ChannelSelect, TextInput]
Components = Dict[str, ComponentType]


class Timestamp(TypedDict):
    """This class is used to represent object's timestamp."""

    date: str
    format: NotRequired[str]


class Embed(TypedDict):
    title: str
    colour: NotRequired[str]
    color: NotRequired[str]
    fields: List[Field]
    description: NotRequired[str]
    type: NotRequired[discord.types.embed.EmbedType]
    url: NotRequired[str]
    timestamp: NotRequired[Timestamp]
    footer: NotRequired[Footer]
    image: NotRequired[str]
    thumbnail: NotRequired[str]
    author: NotRequired[Author]


class ExpansiveEmbed(Embed):
    field: Field
    page_number_key: NotRequired[str]


class File(TypedDict):
    """This class is used to represent the blueprint of a file."""

    filename: str
    spoiler: NotRequired[bool]
    description: NotRequired[str]


class AllowedMentions(TypedDict):
    """This class is used to represent the blueprint of allowed mentions."""

    everyone: NotRequired[bool]
    users: NotRequired[Union[bool, List[int]]]
    roles: NotRequired[Union[bool, List[int]]]
    replied_user: NotRequired[bool]


class MessageReference(TypedDict):
    """This class is used to represent the blueprint of a message reference."""

    message_id: int
    channel_id: int
    guild_id: NotRequired[int]


class View(TypedDict):
    timeout: NotRequired[Optional[float]]
    components: Components


class Element(TypedDict):
    type: Types


class BaseMessage(Element):
    view: NotRequired[View]
    timeout: NotRequired[float]
    content: NotRequired[str]
    embeds: NotRequired[List[Embed]]
    tts: NotRequired[bool]
    nonce: NotRequired[int]
    delete_after: NotRequired[float]
    suppress_embeds: NotRequired[bool]
    file: NotRequired[File]
    files: NotRequired[List[File]]
    allowed_mentions: NotRequired[AllowedMentions]
    message_reference: NotRequired[MessageReference]
    mention_author: NotRequired[bool]
    ephemeral: NotRequired[bool]
    silent: NotRequired[bool]


class RegularMessage(BaseMessage):
    """This class is used to represent the blueprint of a message."""

    embed: NotRequired[Embed]


class Arrows(TypedDict):
    previous: ButtonComponent
    next: ButtonComponent


class ExpansiveMessage(BaseMessage):
    embed: ExpansiveEmbed
    arrows: NotRequired[Arrows]
    page_number_key: NotRequired[str]


Page = Union[RegularMessage, ExpansiveMessage]


class MenuMessage(Element):
    timeout: NotRequired[Optional[float]]
    pages: List[Union[str, Page]]
    arrows: NotRequired[Arrows]


class Modal(Element):
    title: str
    timeout: NotRequired[Optional[float]]
    custom_id: NotRequired[str]
    components: Components


OBJ = TypeVar("OBJ")
Elements = Union[RegularMessage, ExpansiveMessage, MenuMessage, Modal]
Document = Dict[str, Elements]
