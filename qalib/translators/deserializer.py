from __future__ import annotations

from enum import Enum
from typing import Dict, Protocol, Optional, Literal, TypeVar, Union

from discord.ui import Modal

from qalib.translators import Callback, Message
from qalib.translators.events import EventCallbacks
from qalib.translators.menu import Menu

Types = Literal["message", "menu", "modal", "expansive"]

ReturnType = Union[Message, Modal, Menu]

K_contra = TypeVar("K_contra", bound=str, contravariant=True)


class ElementTypes(Enum):
    """Enum that represents the types of elements that can be deserialized."""

    MESSAGE = "message"
    MENU = "menu"
    MODAL = "modal"
    EXPANSIVE = "expansive"

    @classmethod
    def from_str(cls, string: str) -> Optional[ElementTypes]:
        for element_type in cls:
            if element_type.value == string:
                return element_type
        return None


class Deserializer(Protocol[K_contra]):
    """Protocol that represents the deserializer. It is meant to be placed into a Renderer, and is responsible for
    deserializing the document into embeds and views."""

    def deserialize(
        self, source: str, key: K_contra, callables: Dict[str, Callback], events: EventCallbacks
    ) -> ReturnType:
        """This method is used to deserialize a document into an embed and a view.

        Parameters:
            source (str): document that is deserialized
            key (K_contra): key that is used to deserialize the document
            callables (Dict[str, Callback]): callables that are used to deserialize the document
            events (EventCallbacks): hooks that are called on events

        Returns (ReturnType): All possible deserialized types
        """
        raise NotImplementedError
