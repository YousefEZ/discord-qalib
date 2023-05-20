from __future__ import annotations

from copy import deepcopy
from enum import Enum
from typing import List, Optional, Dict, Any, Callable

import discord.ui.button
from discord import ui

from qalib.translators import Message, Callback
from qalib.translators.message_parsing import ButtonComponent, create_button


class MenuEvents(Enum):
    ON_CHANGE = "on_change"


class MenuActions(Enum):
    """Enum that represents the types of actions that can be performed by the buttons."""

    NEXT = "next"
    PREVIOUS = "previous"


PreviousButton: ButtonComponent = {"emoji": "⬅️", "style": "primary"}
NextButton: ButtonComponent = {"emoji": "➡️", "style": "primary"}
DefaultButtons: Dict[MenuActions, ButtonComponent] = {
    MenuActions.NEXT: NextButton,
    MenuActions.PREVIOUS: PreviousButton
}


class Menu:
    """Class that represents a menu. It is used to store the pages of the menu, as well as the buttons that are used"""

    __slots__ = "_pages", "_timeout", "_arrows", "_events", "_active_page", "_front_page", "_linked"

    def __init__(
            self,
            pages: List[Message],
            timeout: Optional[float] = None,
            arrows: Optional[Dict[MenuActions, ButtonComponent]] = None,
            events: Optional[Dict[MenuEvents, Callable[[Menu], Any]]] = None
    ) -> None:
        self._pages = pages
        self._timeout = timeout
        self._arrows = arrows
        self._events = {} if events is None else {event_type: [callback] for event_type, callback in events.items()}
        self._active_page = 0
        self._front_page = 0
        self._link()

    def add_event(self, event: MenuEvents, callback: Callable[[Menu], Any]) -> None:
        """This method is used to add an event to the menu.

        Args:
            event (MenuEvents): event that is added
            callback (Callable[[Menu], Any]): callback that is called when the event is triggered
        """
        if event not in self._events:
            self._events[event] = [callback]
            return
        self._events[event].append(callback)

    def call_event(self, event: MenuEvents) -> None:
        for action in self._events[event]:
            action(self)

    def _create_arrows(
            self,
            left: Optional[int] = None,
            right: Optional[int] = None
    ) -> List[discord.ui.Button]:
        """This function creates the arrow buttons that are used to navigate between the pages.

        Args:
            left (Optional[Message]): embed and view of the left page
            right (Optional[Display]): embed and view of the right page

        Returns (List[discord.ui.Button]): list of the arrow buttons
        """

        def create_view(index: int) -> Callback:
            async def callback(interaction: discord.Interaction):
                await interaction.response.edit_message(
                    **self._pages[index].convert_to_interaction_message().as_edit().dict()
                )

                self._active_page = index
                self.call_event(MenuEvents.ON_CHANGE)

            return callback

        buttons: List[discord.ui.Button] = []

        def construct_button(display: Optional[int], action: MenuActions) -> None:
            if display is None:
                return
            button = deepcopy(
                self._arrows[action] if self._arrows is not None and action in self._arrows else DefaultButtons[action])
            button["callback"] = create_view(display)
            buttons.append(create_button(button))

        construct_button(left, MenuActions.PREVIOUS)
        construct_button(right, MenuActions.NEXT)

        return buttons

    def _link(self) -> None:
        for i, message in enumerate(self._pages):
            left = i - 1 if i > 0 else None
            right = i + 1 if i + 1 < len(self._pages) else None

            if message.view is None:
                message.view = ui.View(timeout=self._timeout)

            for arrow in self._create_arrows(left, right):
                message.view.add_item(arrow)

    def __len__(self) -> int:
        return len(self._pages)

    def __getitem__(self, item: int) -> Message:
        return self._pages[item]

    def current_page(self) -> Message:
        return self[self._active_page]

    @property
    def index(self) -> int:
        return self._active_page

    @property
    def front(self) -> Message:
        return self._pages[self._front_page]

    @front.setter
    def front(self, index: int) -> None:
        if index >= len(self._pages):
            raise IndexError("Index out of bounds")
        self._front_page = index
