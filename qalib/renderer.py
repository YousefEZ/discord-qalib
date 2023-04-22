from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, Generic, List, Optional, cast, Callable, Union

import discord.ui
from discord.ui import Modal
from typing_extensions import ParamSpec, Concatenate

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, Message
from qalib.translators.deserializer import ElementTypes
from qalib.translators.factory import DeserializerFactory, ParserFactory
from qalib.translators.message_parsing import ButtonComponent, create_button
from qalib.translators.parser import K, Parser

P = ParamSpec("P")


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


def render_menu_from_messages(messages: List[Message], timeout: int, **kwargs) -> Message:
    for i, message in enumerate(messages):
        arrow_up = messages[i - 1] if i > 0 else None
        arrow_down = messages[i + 1] if i + 1 < len(messages) else None

        view = discord.ui.View(timeout=timeout) if message.view is None else message.view
        for arrow in create_arrows(arrow_up, arrow_down, **kwargs):
            view.add_item(arrow)
        message.view = view

    return messages[0]


class Renderer(Generic[K]):
    """This object is responsible for rendering the embeds, views, and menus, by first using the templating engine to
    template the document, and then using the deserializer to deserialize the document into embeds and views.
    """

    __slots__ = "_methods", "_template_engine", "_parser", "_filename", "_deserializer"

    def __init__(self, template_engine: TemplateEngine, filename: str, *rendering_options: RenderingOptions):
        self._template_engine = template_engine
        self._parser: Optional[Parser[K]] = None
        if RenderingOptions.PRE_TEMPLATE not in rendering_options:
            self._parser = cast(Parser[K], ParserFactory.get_parser(filename))
        self._filename = filename
        self._deserializer = DeserializerFactory.get_deserializer(filename)

        self._methods: Dict[
            ElementTypes, Callable[Concatenate[str, Dict[str, Callback], int, P], Union[Message, Modal]]
        ] = {
            ElementTypes.MESSAGE.value: self._deserializer.deserialize_into_message,
            ElementTypes.MENU.value: self._render_menu,
            ElementTypes.MODAL.value: self._deserializer.deserialize_into_modal,
            ElementTypes.EXPANSIVE.value: self._render_expansive,
        }

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

    def _render_expansive(self, source: str, callbacks: Dict[str, Callback], timeout: int, **kwargs) -> Message:
        messages = self._deserializer.deserialize_into_expansive(source, callbacks)
        return render_menu_from_messages(messages, timeout, **kwargs)

    def _render_menu(self, source: str, callbacks: Dict[str, Callback], timeout: int, **kwargs) -> Message:
        messages = self._deserializer.deserialize_into_menu(source, callbacks, timeout=timeout)
        return render_menu_from_messages(messages, timeout, **kwargs)

    def render(
        self,
        key: K,
        callbacks: Optional[Dict[str, Callback]] = None,
        keywords: Optional[Dict[str, Any]] = None,
        timeout: int = 180,
    ) -> Union[Message, Modal]:
        """This method is used to render an embed and a view, and places it in a NamedTuple

        Args:
            key (K): key of the embed,
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view,
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text,
            timeout (int): timeout of the view

        Returns (Message): embed and view that can be sent for display.
        """
        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        source = self._pre_template(keywords).template(key, self._template_engine, keywords)
        element_type: ElementTypes = self._deserializer.get_type(source)
        return self._methods[element_type](source, callbacks, timeout, **keywords)
