from __future__ import annotations

from enum import Enum
from typing import Callable, Union, TYPE_CHECKING, Optional, Coroutine, Any, TypeVar, cast

import discord
from discord import ui

if TYPE_CHECKING:
    from qalib.translators.events import EventCallbacks


class ViewEvents(Enum):
    ON_TIMEOUT = "on_timeout"
    ON_ERROR = "on_cancel"
    ON_CHECK = "on_check"


View = TypeVar("View", bound=ui.View, covariant=True)
TimeoutEvent = Callable[[View], Coroutine[Any, Any, None]]
CheckEvent = Callable[[View, discord.Interaction], Coroutine[Any, Any, bool]]
ErrorEvent = Callable[[View, discord.Interaction, Exception, discord.ui.Item], Coroutine[Any, Any, None]]
ViewEventsCallbacks = Union[TimeoutEvent, CheckEvent, ErrorEvent]


class QalibView(ui.View):
    def __init__(self, events: EventCallbacks, timeout: Optional[float] = 180) -> None:
        super().__init__(timeout=timeout)
        self._events = events

    async def on_timeout(self) -> None:
        if ViewEvents.ON_TIMEOUT in self._events:
            await cast(TimeoutEvent, self._events[ViewEvents.ON_TIMEOUT])(self)

    async def on_error(self, interaction: discord.Interaction, exception: Exception, item: discord.ui.Item) -> None:
        if ViewEvents.ON_ERROR in self._events:
            await cast(ErrorEvent, self._events[ViewEvents.ON_ERROR])(self, interaction, exception, item)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if ViewEvents.ON_CHECK in self._events:
            return await cast(CheckEvent, self._events[ViewEvents.ON_CHECK])(self, interaction)
        return True
