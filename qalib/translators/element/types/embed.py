from __future__ import annotations

import dataclasses
from datetime import datetime
from functools import cached_property

from typing import Literal, Dict, TypedDict, Union, cast, Protocol, Optional, Any

import discord
from discord.types import embed as embed_types
from typing_extensions import NotRequired

Colour = Literal[
    "teal",
    "dark_teal",
    "green",
    "dark_green",
    "blue",
    "dark_blue",
    "purple",
    "dark_purple",
    "magenta",
    "dark_magenta",
    "gold",
    "dark_gold",
    "orange",
    "dark_orange",
    "red",
    "dark_red",
    "lighter_grey",
    "dark_grey",
    "light_grey",
    "darker_grey",
    "blurple",
    "greyple",
]
COLOURS: Dict[Colour, int] = {
    "teal": 0x1ABC9C,
    "dark_teal": 0x11806A,
    "green": 0x2ECC71,
    "dark_green": 0x1F8B4C,
    "blue": 0x3498DB,
    "dark_blue": 0x206694,
    "purple": 0x9B59B6,
    "dark_purple": 0x71368A,
    "magenta": 0xE91E63,
    "dark_magenta": 0xAD1457,
    "gold": 0xF1C40F,
    "dark_gold": 0xC27C0E,
    "orange": 0xE67E22,
    "dark_orange": 0xA84300,
    "red": 0xE74C3C,
    "dark_red": 0x992D22,
    "lighter_grey": 0x95A5A6,
    "dark_grey": 0x607D8B,
    "light_grey": 0x979C9F,
    "darker_grey": 0x546E7A,
    "blurple": 0x7289DA,
    "greyple": 0x99AAB5,
}


class Field(TypedDict):
    name: str
    value: str
    inline: bool


class Footer(TypedDict):
    text: str
    icon_url: str


class Author(TypedDict):
    name: str
    url: str
    icon_url: str


class Emoji(TypedDict):
    """This class is used to represent the blueprint of an emoji."""

    name: str
    id: NotRequired[int]
    animated: NotRequired[bool]


def make_colour(colour: str) -> Union[discord.Colour, int]:
    """maps the name of a colour to its value
    Args:
        colour (str): the name of the colour, or it's rgb components.
    Returns:
        int: hexadecimal value of the colour.
    """
    colour = colour.replace(" ", "_")
    if colour in COLOURS:
        return COLOURS[cast(Colour, colour)]
    rgb = colour.split(",")
    return discord.Colour.from_rgb(*map(int, rgb))


class EmbedBaseAdapter(Protocol):

    @cached_property
    def title(self) -> str:
        raise NotImplementedError

    @cached_property
    def description(self) -> Optional[str]:
        raise NotImplementedError

    @cached_property
    def colour(self) -> Colour | int:
        raise NotImplementedError

    @cached_property
    def timestamp(self) -> Optional[datetime]:
        raise NotImplementedError

    @cached_property
    def footer(self) -> Optional[Footer]:
        raise NotImplementedError

    @cached_property
    def image(self) -> Optional[str]:
        raise NotImplementedError

    @cached_property
    def thumbnail(self) -> Optional[str]:
        raise NotImplementedError

    @cached_property
    def author(self) -> Optional[Author]:
        raise NotImplementedError

    @cached_property
    def type(self) -> embed_types.EmbedType:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EmbedBaseData:
    title: str
    colour: Colour | int
    type: embed_types.EmbedType = dataclasses.field(default="rich")
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    footer: Optional[Footer] = None
    image: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[Author] = None
