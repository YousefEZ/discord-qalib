from __future__ import annotations

from typing import Any, Dict, List, Protocol

import discord.ui

from qalib.translators import Callback, Message


class Deserializer(Protocol):
    """Protocol that represents the deserializer. It is meant to be placed into a Renderer, and is responsible for
    deserializing the document into embeds and views."""

    def deserialize_into_message(self, source: str, callables: Dict[str, Callback], **kw: Any) -> Message:
        """This method is used to deserialize a document into an embed and a view.

        Parameters:
            source (str): document that is deserialized
            callables (Dict[str, Callback]): callables that are used to deserialize the document
            **kw (Any: additional arguments that are used to deserialize the document

        Returns (Display): NamedTuple containing the embed and view.
        """
        raise NotImplementedError

    def deserialize_into_menu(self, source: str, callables: Dict[str, Callback], **kw: Any) -> List[Message]:
        """This method is used to deserialize a document into a list of NamedTuple Displays, that are connected by
        arrows in their views.

        Args:
            source (str): document that is deserialized
            callables (Dict[str, Callback]): callables that are used to deserialize the document
            **kw (Any): additional arguments that are used to deserialize the document

        Returns (List[Display]): list of NamedTuple Displays, that are connected by arrows in their views.
        """
        raise NotImplementedError

    def deserialize_into_modal(self, source: str, methods: Dict[str, Callback], **kw: Any) -> discord.ui.Modal:
        """This method is used to deserialize a document into a modal.

        Args:
            source (str): document that is deserialized
            methods (Dict[str, Callback]): methods that are used to deserialize the document
            **kw (Any): additional arguments that are used to deserialize the document

        Returns (discord.ui.Modal): modal that is deserialized from the document.
        """
        raise NotImplementedError
