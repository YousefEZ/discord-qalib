from typing import Optional, Union

import discord.emoji
import discord.ui as ui
from discord.utils import MISSING
from discord.ui.button import ButtonStyle


def make_button_style(style: str) -> ButtonStyle:
    if style == "primary":
        return ButtonStyle.primary
    elif style == "secondary":
        return ButtonStyle.secondary
    elif style == "success":
        return ButtonStyle.success
    elif style == "danger":
        return ButtonStyle.danger
    elif style == "link":
        return ButtonStyle.link

    raise ValueError(f"{style} is Invalid button style")


def make_emoji(emoji: Optional[Union[str, dict]]) -> Optional[Union[str, discord.emoji.PartialEmoji]]:
    if emoji is None:
        return None
    return discord.emoji.PartialEmoji.from_dict(emoji)


def create_button(**kwargs) -> ui.Button:
    return ui.Button(
        style=make_button_style(kwargs.get("style")),
        custom_id=kwargs.get("custom_id"),
        label=kwargs.get("label"),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        url=kwargs.get("url"),
        emoji=kwargs.get("emoji"),
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )


def create_select(**kwargs) -> ui.Select:
    return ui.Select(
        custom_id=kwargs.get("custom_id", MISSING),
        placeholder=kwargs.get("placeholder"),
        min_values=int(kwargs.get("min_values", 1)),
        max_values=int(kwargs.get("max_values", 1)),
        disabled=kwargs.get("disabled", "false").lower() == "true",
        options=kwargs.get("options", []),
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )
