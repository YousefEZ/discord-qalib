from typing import Protocol, Optional, Dict, Any, List, NamedTuple, Coroutine

import discord.ui
from discord.enums import ButtonStyle


class Display(NamedTuple):
    """NamedTuple that represents the display of the message."""
    embed: discord.Embed
    view: Optional[discord.ui.View]


def create_arrows(left: Optional[Display], right: Optional[Display], **kwargs) -> List[discord.ui.Button]:
    """This function creates the arrow buttons that are used to navigate between the pages.

    Args:
        left (Optional[Display]): embed and view of the left page
        right (Optional[Display]): embed and view of the right page

    Returns (List[discord.ui.Button]): list of the arrow buttons
    """

    def view(display: List):
        async def callback(interaction):
            await interaction.response.edit_message(embed=display[0], view=display[1], **kwargs)

        return callback

    buttons = []

    def construct_button(display: Optional[List], emoji: str):
        if display is None:
            return
        buttons.append(discord.ui.Button(style=ButtonStyle.grey, emoji=emoji))
        buttons[-1].callback = view(display)

    construct_button(left, "⬅️")
    construct_button(right, "➡️")

    return buttons


class RendererProtocol(Protocol):

    def render(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Coroutine]],
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> Display:
        ...

    def render_menu(
            self,
            callbacks: Optional[Dict[str, Coroutine]],
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> Display:
        ...

    def set_root(self, key: str):
        ...
