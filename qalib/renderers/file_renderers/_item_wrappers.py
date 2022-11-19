from typing import Optional, Union

from discord.ui import Button
from discord.ui.button import ButtonStyle
from discord.emoji import Emoji, PartialEmoji


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

    raise ValueError("Invalid button style")


def make_emoji(emoji: Optional[Union[str, dict]]) -> Optional[Union[str, Emoji, PartialEmoji]]:
    if emoji is None:
        return None
    elif isinstance(emoji, str):
        return emoji
    elif isinstance(emoji, dict):
        if "name" in emoji:
            return emoji["name"]
        elif "id" in emoji:
            return PartialEmoji(name=emoji["name"], id=emoji["id"], animated=emoji.get("animated", False))

    raise ValueError("Invalid emoji")


def create_button(**kwargs) -> Button:
    return Button(
        style=make_button_style(kwargs.get("style")),
        label=kwargs.get("label"),
        disabled=kwargs.get("disabled").lower() == "True",
        custom_id=kwargs.get("custom_id"),
        url=kwargs.get("url"),
        emoji=make_emoji(kwargs.get("emoji")),
        row=int(kwargs.get("row"))
    )
