from typing import Optional, Union

import discord.emoji
import discord.ui as ui
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

    if "name" in emoji and "id" not in emoji:
        return emoji["name"]
    elif "id" in emoji:
        return discord.emoji.PartialEmoji(name=emoji["name"],
                                          id=emoji["id"],
                                          animated=emoji.get("animated", "False") == "True")

    raise ValueError("Invalid emoji")


def create_button(**kwargs) -> discord.ui.Button:
    return discord.ui.Button(
        style=make_button_style(kwargs.get("style")),
        label=kwargs.get("label"),
        disabled=kwargs.get("disabled", "False").lower() == "True",
        custom_id=kwargs.get("custom_id"),
        url=kwargs.get("url"),
        emoji=make_emoji(kwargs.get("emoji")),
        row=int(row) if (row := kwargs.get("row")) is not None else None
    )
