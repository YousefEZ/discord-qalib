from enum import Enum
from typing import Callable, Union, Coroutine, Any

import discord

from qalib.translators.view import TimeoutEvent, CheckEvent, ErrorEvent


class ModalEvents(Enum):
    ON_TIMEOUT = "on_timeout"
    ON_ERROR = "on_cancel"
    ON_CHECK = "on_check"
    ON_SUBMIT = "on_submit"


SubmitEvent = Callable[[discord.Interaction], Coroutine[Any, Any, None]]
ModalEventsCallbacks = Union[TimeoutEvent, CheckEvent, ErrorEvent, SubmitEvent]
