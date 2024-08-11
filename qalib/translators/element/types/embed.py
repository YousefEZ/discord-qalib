from __future__ import annotations

import dataclasses
from datetime import datetime
from typing import Literal, Dict, TypedDict, Union, cast, Protocol, Optional

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

COLOURS: Dict[Colour, discord.Colour] = {
    "teal": discord.Colour.teal(),
    "dark_teal": discord.Colour.dark_teal(),
    "green": discord.Colour.green(),
    "dark_green": discord.Colour.dark_green(),
    "blue": discord.Colour.blue(),
    "dark_blue": discord.Colour.dark_blue(),
    "purple": discord.Colour.purple(),
    "dark_purple": discord.Colour.dark_purple(),
    "magenta": discord.Colour.magenta(),
    "dark_magenta": discord.Colour.dark_magenta(),
    "gold": discord.Colour.gold(),
    "dark_gold": discord.Colour.dark_gold(),
    "orange": discord.Colour.orange(),
    "dark_orange": discord.Colour.dark_orange(),
    "red": discord.Colour.red(),
    "dark_red": discord.Colour.dark_red(),
    "lighter_grey": discord.Colour.lighter_grey(),
    "dark_grey": discord.Colour.dark_grey(),
    "light_grey": discord.Colour.light_grey(),
    "darker_grey": discord.Colour.darker_grey(),
    "blurple": discord.Colour.blurple(),
    "greyple": discord.Colour.greyple(),
}


class Field(TypedDict):
    name: str
    value: str
    inline: NotRequired[bool]


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
    @property
    def title(self) -> str:
        raise NotImplementedError

    @property
    def description(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def colour(self) -> discord.Colour | int:
        raise NotImplementedError

    @property
    def timestamp(self) -> Optional[datetime]:
        raise NotImplementedError

    @property
    def footer(self) -> Optional[Footer]:
        raise NotImplementedError

    @property
    def image(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def thumbnail(self) -> Optional[str]:
        raise NotImplementedError

    @property
    def author(self) -> Optional[Author]:
        raise NotImplementedError

    @property
    def type(self) -> embed_types.EmbedType:
        raise NotImplementedError


@dataclasses.dataclass(frozen=True)
class EmbedBaseData:
    title: str
    colour: discord.Colour | int
    type: embed_types.EmbedType = dataclasses.field(default="rich")
    description: Optional[str] = None
    timestamp: Optional[datetime] = None
    footer: Optional[Footer] = None
    image: Optional[str] = None
    thumbnail: Optional[str] = None
    author: Optional[Author] = None
