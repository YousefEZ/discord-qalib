from __future__ import annotations

from typing import Dict, TypeVar, Iterable, List, Literal, Optional, Type, TypedDict, Union, cast, Callable, Any, Tuple

import discord
import discord.emoji
import discord.partial_emoji
import emoji
from discord import ui, utils
from typing_extensions import NotRequired, Concatenate, ParamSpec

from qalib.translators import Callback, CallbackMethod, Message, M, N

P = ParamSpec("P")
T = TypeVar("T")

__all__ = (
    "CustomSelects",
    "make_channel_types",
    "make_emoji",
    "make_colour",
    "apply",
    "create_button",
    "create_select",
    "create_channel_select",
    "create_type_select",
    "create_text_input",
    "make_expansive_embeds",
    "create_arrows",
    "attach_views",
    "bind_menu",
    "make_menu",
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
MAX_CHAR = 1024


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
        return raw_emoji

    if "name" not in raw_emoji:
        raise ValueError("Missing Emoji Name")

    if emoji.is_emoji(raw_emoji["name"]):
        return raw_emoji["name"]

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


def split_text(text: str) -> List[str]:
    start = 0
    lines = [string.strip() for string in text.strip().split("\n")]

    values: List[str] = []

    def compile_lines(end: Optional[int] = None) -> str:
        if end is None:
            return "\n".join([string.replace("\\n", "\n") for string in lines[start:]])
        return "\n".join([string.replace("\\n", "\n") for string in lines[start: end]])

    for i in range(len(lines)):
        if sum(map(len, lines[start: i + 1])) > MAX_CHAR:
            values.append(compile_lines(i))
            start = i

    values.append(compile_lines())
    return values


def replace_with_page(value: str, replacement_key: str, page_number: str) -> str:
    return value.replace(replacement_key, page_number)


# pylint: disable= too-many-arguments
def make_expansive_embed(
        name: str,
        value: str,
        page_number: str,
        replacement_key: Optional[str],
        raw_embed: Any,
        embed_renderer: Callable[..., discord.Embed]
) -> discord.Embed:
    if replacement_key is not None:
        replacement: Tuple[str, str] = (replacement_key, page_number)
        embed = embed_renderer(raw_embed, replacement)
        embed.add_field(name=replace_with_page(name, *replacement) if replacement_key is not None else name,
                        value=replace_with_page(value, *replacement) if replacement_key is not None else value,
                        inline=False)
    else:
        embed = embed_renderer(raw_embed)
        embed.add_field(name=name, value=value, inline=False)
    return embed


def make_expansive_embeds(
        name: str,
        text: str,
        replacement_key: Optional[str],
        raw_embed: T,
        embed_renderer: Callable[Concatenate[T, P], discord.Embed]
) -> List[discord.Embed]:
    return [make_expansive_embed(name, value, str(i + 1), replacement_key, raw_embed, embed_renderer)
            for i, value in enumerate(split_text(text))]


def attach_views(messages: List[Message], timeout: Optional[float]) -> None:
    for message in messages:
        if message.view is None:
            message.view = ui.View()
        message.view.timeout = timeout


def create_arrows(left: Optional[Message] = None, right: Optional[Message] = None) -> List[discord.ui.Button]:
    """This function creates the arrow buttons that are used to navigate between the pages.

    Args:
        left (Optional[Message]): embed and view of the left page
        right (Optional[Display]): embed and view of the right page

    Returns (List[discord.ui.Button]): list of the arrow buttons
    """

    def view(message: Message) -> Callback:
        async def callback(interaction: discord.Interaction):
            await interaction.response.edit_message(**message.convert_to_interaction_message().as_edit().dict())

        return callback

    buttons: List[discord.ui.Button] = []

    def construct_button(display: Optional[Message], emoji_string: str):
        if display is None:
            return
        button: ButtonComponent = {"emoji": emoji_string, "style": "primary", "callback": view(display)}
        buttons.append(create_button(button))

    construct_button(left, "⬅️")
    construct_button(right, "➡️")

    return buttons


def make_menu(messages: List[Message]) -> Message:
    for i, message in enumerate(messages):
        arrow_up = messages[i - 1] if i > 0 else None
        arrow_down = messages[i + 1] if i + 1 < len(messages) else None

        if message.view is None:
            message.view = ui.View()

        for arrow in create_arrows(arrow_up, arrow_down):
            message.view.add_item(arrow)

    return messages[0]


def bind_menu(
        method: Callable[[T, Dict[str, Callback]], List[Message]]
) -> Callable[[T, Dict[str, Callback]], Message]:
    def wrapper(message: T, callbacks: Dict[str, Callback]) -> Message:
        return make_menu(method(message, callbacks))

    return wrapper


def apply(
        element: Optional[M],
        func: Callable[Concatenate[M, P], N],
        *args: P.args,
        **keyword_args: P.kwargs,
) -> Optional[N]:
    if element is None:
        return None
    return func(element, *args, **keyword_args)
