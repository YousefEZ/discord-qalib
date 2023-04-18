from enum import Enum, auto
from typing import Any, Dict, Generic, List, Optional, cast

import discord.ui

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, Message
from qalib.translators.factory import DeserializerFactory, ParserFactory
from qalib.translators.message_parsing import ButtonComponent, create_button
from qalib.translators.parser import K, Parser


class RenderingOptions(Enum):
    """Options for the renderer."""

    PRE_TEMPLATE = auto()


def create_arrows(left: Optional[Message] = None, right: Optional[Message] = None, **kwargs) -> List[discord.ui.Button]:
    """This function creates the arrow buttons that are used to navigate between the pages.

    Args:
        left (Optional[Message]): embed and view of the left page
        right (Optional[Display]): embed and view of the right page

    Returns (List[discord.ui.Button]): list of the arrow buttons
    """

    def view(message: Message) -> Callback:
        async def callback(interaction: discord.Interaction):
            await interaction.response.edit_message(**{**message.dict(), **kwargs})

        return callback

    buttons: List[discord.ui.Button] = []

    def construct_button(display: Optional[Message], emoji: str):
        if display is None:
            return
        button: ButtonComponent = {"emoji": emoji, "style": "primary", "callback": view(display)}
        buttons.append(create_button(button))

    construct_button(left, "⬅️")
    construct_button(right, "➡️")

    return buttons


class Renderer(Generic[K]):
    """This object is responsible for rendering the embeds, views, and menus, by first using the templating engine to
    template the document, and then using the deserializer to deserialize the document into embeds and views.
    """

    __slots__ = ("_template_engine", "_parser", "_filename", "_deserializer")

    def __init__(self, template_engine: TemplateEngine, filename: str, *rendering_options: RenderingOptions):
        self._template_engine = template_engine
        self._parser: Optional[Parser[K]] = None
        if RenderingOptions.PRE_TEMPLATE not in rendering_options:
            self._parser = cast(Parser[K], ParserFactory.get_parser(filename))
        self._filename = filename
        self._deserializer = DeserializerFactory.get_deserializer(filename)

    def _pre_template(self, keywords: Dict[str, Any]) -> Parser[K]:
        """Pre-Template templates the document before further processing. It returns a Parser instance that contains
        the data that is used to render the embeds and views.

        Args:
            keywords (Dict[str, Any]): keywords that are passed to the templating engine to template the document.

        Returns (Parser): Parser instance that contains the data that is used to render the embeds and views.
        """
        if self._parser is None:
            with open(self._filename, "r", encoding="utf-8") as file:
                return cast(
                    Parser[K],
                    ParserFactory.get_parser(
                        self._filename,
                        source=self._template_engine.template(file.read(), keywords),
                    ),
                )
        return self._parser

    def render(
        self,
        key: K,
        callbacks: Optional[Dict[str, Callback]] = None,
        keywords: Optional[Dict[str, Any]] = None,
        timeout: int = 180,
    ) -> Message:
        """This method is used to render an embed and a view, and places it in a NamedTuple

        Args:
            key (K): key of the embed,
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view,
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text,
            timeout (int): timeout of the view

        Returns (Display): embed and view that can be sent for display.
        """
        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        embed = self._pre_template(keywords).template_message(key, self._template_engine, keywords)

        return self._deserializer.deserialize_into_message(embed, callbacks, timeout=timeout)

    def render_menu(
        self,
        key: K,
        callbacks: Optional[Dict[str, Callback]] = None,
        keywords: Optional[Dict[str, Any]] = None,
        timeout: Optional[int] = 180,
        **kwargs,
    ) -> Message:
        """This method is used to create a menu for the user to select from.

        Args:
            key (K): key of the menu
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view
            timeout (Optional[int]): timeout of the view
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text

        Returns (Display): Returns the NamedTuple Display, which contains the embed and the view that has arrow buttons
        that edit the embed and view
        """
        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        menu = self._pre_template(keywords).template_menu(key, self._template_engine, keywords)
        messages = self._deserializer.deserialize_into_menu(menu, callbacks, timeout=timeout)

        for i, message in enumerate(messages):
            arrow_left = messages[i - 1] if i > 0 else None
            arrow_right = messages[i + 1] if i + 1 < len(messages) else None

            view = discord.ui.View(timeout=timeout) if message.view is None else message.view
            for arrow in create_arrows(arrow_left, arrow_right, **kwargs):
                view.add_item(arrow)
            message.view = view

        return messages[0]

    def render_modal(
        self,
        key: K,
        methods: Optional[Dict[str, Callback]] = None,
        keywords: Optional[Dict[str, Any]] = None,
    ) -> discord.ui.Modal:
        if methods is None:
            methods = {}

        if keywords is None:
            keywords = {}

        modal = self._pre_template(keywords).template_modal(key, self._template_engine, keywords)
        return self._deserializer.deserialize_into_modal(modal, methods)
