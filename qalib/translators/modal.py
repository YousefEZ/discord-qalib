from __future__ import annotations

from enum import Enum
from typing import Callable, Union, Coroutine, Any, Optional, cast, Dict

import discord
from discord import ui
from discord.utils import MISSING

from qalib.translators.view import TimeoutEvent, CheckEvent


class ModalEvents(Enum):
    ON_TIMEOUT = "on_timeout"
    ON_ERROR = "on_error"
    ON_CHECK = "on_check"
    ON_SUBMIT = "on_submit"


ErrorEvent = Callable[[ui.Modal, discord.Interaction, Exception], Coroutine[Any, Any, None]]
SubmitEvent = Callable[[ui.Modal, discord.Interaction], Coroutine[Any, Any, None]]
ModalEventsCallbacks = Union[TimeoutEvent, CheckEvent, ErrorEvent, SubmitEvent]


class QalibModal(ui.Modal):
    def __init__(
        self,
        title: Optional[str] = None,
        timeout: Optional[float] = 180,
        custom_id: Optional[str] = None,
        events: Optional[Dict[ModalEvents, ModalEventsCallbacks]] = None,
    ) -> None:
        super().__init__(
            title=MISSING if title is None else title,
            timeout=timeout,
            custom_id=MISSING if custom_id is None else custom_id,
        )
        self._events = {} if events is None else events

    async def on_timeout(self) -> None:
        if ModalEvents.ON_TIMEOUT in self._events:
            await cast(TimeoutEvent, self._events[ModalEvents.ON_TIMEOUT])(self)

    async def on_error(self, interaction: discord.Interaction, exception: Exception, /) -> None:
        if ModalEvents.ON_ERROR in self._events:
            await cast(ErrorEvent, self._events[ModalEvents.ON_ERROR])(self, interaction, exception)

    async def on_submit(self, interaction: discord.Interaction, /) -> None:
        if ModalEvents.ON_SUBMIT in self._events:
            await cast(SubmitEvent, self._events[ModalEvents.ON_SUBMIT])(self, interaction)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if ModalEvents.ON_CHECK in self._events:
            return await cast(CheckEvent, self._events[ModalEvents.ON_CHECK])(self, interaction)
        return True
