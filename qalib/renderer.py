from enum import Enum, auto
from typing import Optional, Any, Dict, List

import discord.ui
from discord.enums import ButtonStyle

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Display, Callback
from qalib.translators.factory import ParserFactory, DeserializerFactory
from qalib.translators.parser import Parser


class RenderingOptions(Enum):
    """Options for the renderer."""
    PRE_TEMPLATE = auto()


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


class Renderer:
    __slots__ = ("_template_engine", "_parser", "_filename", "_deserializer")

    def __init__(
            self,
            template_engine: TemplateEngine,
            filename: str,
            rendering_option: Optional[RenderingOptions] = None
    ):
        self._template_engine = template_engine
        self._parser: Optional[Parser] = None
        if rendering_option is None:
            self._parser = ParserFactory.get_parser(filename)
        self._filename = filename
        self._deserializer = DeserializerFactory.get_deserializer(filename)

    def _pre_template(self, keywords: Dict[str, Any]) -> Parser:
        if self._parser is None:
            with open(self._filename, "r") as file:
                return ParserFactory.get_parser(self._filename,
                                                source=self._template_engine.template(file.read(), keywords))
        return self._parser

    def render(
            self,
            key: str,
            callbacks: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: int = 180
    ) -> Display:
        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        embed = self._pre_template(keywords).template_embed(key, self._template_engine, keywords)

        return self._deserializer.deserialize(embed, callbacks, timeout=timeout)

    def render_menu(
            self,
            key: str,
            callbacks: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180,
            **kwargs
    ) -> Display:
        """This method is used to create a menu for the user to select from.

        Args:
            key (str): key of the menu
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view
            timeout (Optional[int]): timeout of the view
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
        """
        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        menu = self._pre_template(keywords).template_menu(key, self._template_engine, keywords)
        displays = self._deserializer.deserialize_into_menu(menu, callbacks, timeout=timeout)

        for i, display in enumerate(displays):
            arrow_left = displays[i - 1] if i > 0 else None
            arrow_right = displays[i + 1] if i + 1 < len(displays) else None

            for arrow in create_arrows(arrow_left, arrow_right, **kwargs):
                display.view.add_item(arrow)

        return displays[0]
