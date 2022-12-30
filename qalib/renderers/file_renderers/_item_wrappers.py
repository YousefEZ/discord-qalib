from typing import Dict, List, Optional, Union
from typing import Type

import discord.emoji
import discord.ui as ui
import discord.utils as utils
import emoji
from discord.ui.button import ButtonStyle

__all__ = (
    "T",
    "make_channel_types",
    "make_emoji",
    "create_button",
    "create_select",
    "create_channel_select",
    "create_type_select",
    "create_text_input"
)

T = Union[ui.RoleSelect, ui.UserSelect, ui.MentionableSelect]

CHANNEL_TYPES: Dict[str, discord.ChannelType] = {
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
    "forum": discord.ChannelType.forum
}

BUTTON_STYLES: Dict[str, ButtonStyle] = {
    "primary": ButtonStyle.primary,
    "secondary": ButtonStyle.secondary,
    "success": ButtonStyle.success,
    "danger": ButtonStyle.danger,
    "link": ButtonStyle.link
}

TEXT_STYLES: Dict[str, discord.TextStyle] = {
    "short": discord.TextStyle.short,
    "paragraph": discord.TextStyle.paragraph,
    "long": discord.TextStyle.long
}


def make_channel_types(types: List[str]) -> List[discord.ChannelType]:
    return list(map(CHANNEL_TYPES.get, types))


def make_emoji(raw_emoji: Optional[Union[str, dict]]) -> Optional[Union[str, discord.emoji.PartialEmoji]]:
    if raw_emoji is None:
        return None

    if all(k in raw_emoji for k in ("name", "id", "animated")):
        return discord.emoji.PartialEmoji.from_dict(raw_emoji)

    if "id" in raw_emoji:
        return f"<:{raw_emoji['name']}:{raw_emoji['id']}>"
    elif "name" in raw_emoji:
        if emoji.is_emoji(raw_emoji["name"]):
            return emoji.demojize(raw_emoji["name"])
        return raw_emoji["name"] if raw_emoji["name"].startswith(":") else f":{raw_emoji['name']}:"

    raise ValueError("Invalid Emoji Description Given")


def create_button(**kwargs) -> ui.Button:
    return ui.Button(
        style=BUTTON_STYLES.get(kwargs.get("style", "primary")),
        custom_id=kwargs.get("custom_id"),
        label=kwargs.get("label"),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        url=kwargs.get("url"),
        emoji=kwargs.get("emoji"),
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )


def create_channel_select(**kwargs) -> ui.ChannelSelect:
    return ui.ChannelSelect(
        custom_id=kwargs.get("custom_id", utils.MISSING),
        channel_types=kwargs.get("channel_types", utils.MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )


def create_select(**kwargs) -> ui.Select:
    return ui.Select(
        custom_id=kwargs.get("custom_id", utils.MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        options=kwargs.get("options", []),
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )


def create_type_select(select: Type[T], **kwargs) -> T:
    return select(
        custom_id=kwargs.get("custom_id", utils.MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )


def create_text_input(**kwargs) -> ui.TextInput:
    return ui.TextInput(
        label=kwargs.get("label"),
        custom_id=kwargs.get("custom_id", utils.MISSING),
        style=TEXT_STYLES.get(kwargs.get("style", "text")),
        placeholder=kwargs.get("placeholder"),
        default=kwargs.get("default"),
        min_length=int(kwargs.get("min_length", 0)),
        max_length=int(kwargs.get("max_length", 2000)),
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )
