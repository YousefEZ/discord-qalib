from __future__ import annotations

from typing import Dict, Iterable, List, Literal, Optional, Type, TypedDict, Union, cast

import discord
import discord.emoji
import discord.partial_emoji
import emoji
from discord import ui, utils

__all__ = (
    "CustomSelects",
    "make_channel_types",
    "make_emoji",
    "make_colour",
    "create_button",
    "create_select",
    "create_channel_select",
    "create_type_select",
    "create_text_input",
    "TextStyle",
    "ButtonStyle",
    "ChannelType",
    "Emoji",
    "ButtonComponent",
    "TextInputRaw",
    "TextInputComponent",
    "Field",
    "Author",
    "Footer",
)

from typing_extensions import NotRequired

from qalib.translators import Callback, CallbackMethod

CustomSelects = Union[ui.RoleSelect, ui.UserSelect, ui.MentionableSelect]

ChannelType = Literal[
    "text",
    "private",
    "voice",
    "group",
    "category",
    "news",
    "news_thread",
    "public_thread",
    "private_thread",
    "stage_voice",
    "forum",
]

CHANNEL_TYPES: Dict[ChannelType, discord.ChannelType] = {
    "text": discord.ChannelType.text,
    "private": discord.ChannelType.private,
    "voice": discord.ChannelType.voice,
    "group": discord.ChannelType.group,
    "category": discord.ChannelType.category,
    "news": discord.ChannelType.news,
    "news_thread": discord.ChannelType.news_thread,
    "public_thread": discord.ChannelType.public_thread,
    "private_thread": discord.ChannelType.private_thread,
    "stage_voice": discord.ChannelType.stage_voice,
    "forum": discord.ChannelType.forum,
}

ButtonStyle = Literal["primary", "secondary", "success", "danger", "link"]

BUTTON_STYLES: Dict[ButtonStyle, discord.enums.ButtonStyle] = {
    "primary": discord.enums.ButtonStyle.primary,
    "secondary": discord.enums.ButtonStyle.secondary,
    "success": discord.enums.ButtonStyle.success,
    "danger": discord.enums.ButtonStyle.danger,
    "link": discord.enums.ButtonStyle.link,
}

TextStyle = Literal["short", "paragraph", "long"]

TEXT_STYLES: Dict[TextStyle, discord.TextStyle] = {
    "short": discord.TextStyle.short,
    "paragraph": discord.TextStyle.paragraph,
    "long": discord.TextStyle.long,
}

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

SelectTypes = Type[Union[ui.RoleSelect, ui.UserSelect, ui.MentionableSelect]]


class Emoji(TypedDict):
    """This class is used to represent the blueprint of an emoji."""

    name: str
    id: NotRequired[int]
    animated: NotRequired[bool]


class Component(TypedDict):
    custom_id: NotRequired[str]
    row: NotRequired[int]


class ButtonComponent(Component):
    style: NotRequired[ButtonStyle]
    label: NotRequired[str]
    disabled: NotRequired[bool]
    url: NotRequired[str]
    emoji: NotRequired[Union[str, Emoji]]
    callback: NotRequired[Callback]


class TextInputRaw(Component):
    label: NotRequired[str]
    style: NotRequired[TextStyle]
    placeholder: NotRequired[str]
    default: NotRequired[str]
    min_length: NotRequired[int]
    max_length: NotRequired[int]


class TextInputComponent(TextInputRaw):
    callback: NotRequired[Callback]


def make_a_method_from_callback(callback: Callback) -> CallbackMethod:
    """This function creates a method from a callback.

    Args:
        callback (Callback): the callback to be used.

    Returns:
        Callable: the method.
    """

    async def method(_, interaction: discord.Interaction):
        await callback(interaction)

    return method


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


def make_channel_types(channel_types: Iterable[ChannelType]) -> List[discord.ChannelType]:
    return [CHANNEL_TYPES[channel_type] for channel_type in channel_types]


def make_emoji(raw_emoji: Optional[Union[str, Emoji]]) -> Optional[str]:
    if raw_emoji is None:
        return None

    if isinstance(raw_emoji, str):
        return "{}".format(raw_emoji)

    if "name" not in raw_emoji:
        raise ValueError("Missing Emoji Name")

    if "id" not in raw_emoji:
        return emoji.emojize(":" + raw_emoji["name"] + ":")

    string = f"a:{raw_emoji['name']}:" if raw_emoji.get("animated", False) else f":{raw_emoji['name']}:"
    return string + str(raw_emoji["id"]) if "id" in raw_emoji else string


def create_button(component: ButtonComponent) -> ui.Button:
    button: Type[ui.Button] = ui.Button
    if "callback" in component:
        button = cast(
            Type[ui.Button],
            type(ui.Button.__name__, (ui.Button,), {"callback": make_a_method_from_callback(component["callback"])}),
        )

    return button(
        style=BUTTON_STYLES[component.get("style", "primary")],
        custom_id=component.get("custom_id"),
        label=component.get("label"),
        disabled=component.get("disabled", False),
        url=component.get("url"),
        emoji=make_emoji(component["emoji"]) if "emoji" in component else None,
        row=int(component["row"]) if "row" in component else None,
    )


def create_channel_select(**kwargs) -> ui.ChannelSelect:
    channel_select: Type[ui.ChannelSelect] = ui.ChannelSelect
    if kwargs.get("callback") is not None:
        channel_select = cast(
            Type[ui.ChannelSelect],
            type(
                ui.ChannelSelect.__name__,
                (ui.ChannelSelect,),
                {"callback": make_a_method_from_callback(kwargs["callback"])},
            ),
        )
    return channel_select(
        custom_id=kwargs.get("custom_id", utils.MISSING),
        channel_types=kwargs.get("channel_types", utils.MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        row=int(row) if (row := kwargs.get("row")) is not None else None,
    )


def create_select(**kwargs) -> ui.Select:
    select: Type[ui.Select] = ui.Select
    if kwargs.get("callback") is not None:
        select = cast(
            Type[ui.Select],
            type(ui.Select.__name__, (ui.Select,), {"callback": make_a_method_from_callback(kwargs["callback"])}),
        )

    return select(
        custom_id=kwargs.get("custom_id", utils.MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs["disabled"].lower() == "true" if "disabled" in kwargs else False,
        options=kwargs.get("options", []),
        row=int(row) if (row := kwargs.get("row")) is not None else None,
    )


def create_type_select(select: SelectTypes, **kwargs) -> Union[ui.RoleSelect, ui.UserSelect, ui.MentionableSelect]:
    if kwargs.get("callback") is not None:
        select = cast(
            SelectTypes,
            type(select.__name__, (select,), {"callback": make_a_method_from_callback(kwargs["callback"])}),
        )

    return select(
        custom_id=kwargs.get("custom_id", utils.MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        row=int(row) if (row := kwargs.get("row")) is not None else None,
    )


def create_text_input(text_input_component: TextInputComponent) -> ui.TextInput:
    text_input: Type[ui.TextInput] = ui.TextInput
    if "callback" in text_input_component:
        text_input = cast(
            Type[ui.TextInput],
            type(
                ui.TextInput.__name__,
                (ui.TextInput,),
                {"callback": make_a_method_from_callback(text_input_component["callback"])},
            ),
        )
    return text_input(
        label=text_input_component.get("label", ""),
        custom_id=text_input_component.get("custom_id", utils.MISSING),
        style=TEXT_STYLES[text_input_component.get("style", "short")],
        placeholder=text_input_component.get("placeholder"),
        default=text_input_component.get("default"),
        min_length=int(text_input_component.get("min_length", 0)),
        max_length=int(text_input_component.get("max_length", 2000)),
        row=int(row) if (row := text_input_component.get("row")) is not None else None,
    )


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
