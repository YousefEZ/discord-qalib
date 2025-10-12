from typing import Optional, cast, Callable, Any, TYPE_CHECKING

import discord.ext.commands
import discord.ui
from mock import Mock

from qalib import Coro

button_message_component = {
    "custom_id": "custom_id",
    "component_type": 2,
}

raw_data = {
    "id": 0,
    "application_id": 10,
    "token": "token",
    "version": 1,
    "type": 3,
    "data": button_message_component,
    "attachment_size_limit": 1,
}


class MockedInteraction(discord.Interaction):
    def __init__(self):
        if TYPE_CHECKING:
            from discord.types.interactions import Interaction as InteractionPayload

            super().__init__(data=cast(InteractionPayload, raw_data), state=Mock())

        else:
            super().__init__(data=raw_data, state=Mock())


class MessageMocked:
    def __init__(
        self,
        author: str = "",
        channel: int = 0,
        content: str = "",
        embed: Optional[discord.Embed] = None,
        view: Optional[discord.ui.View] = None,
    ):
        self.author = author
        self.channel = channel
        self.content = content
        self.embed = embed
        self.view = view
        self._state = Mock()


class BotMocked(discord.ext.commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        self.message: discord.Message = cast(discord.Message, MessageMocked())

    def inject_message(self, message: discord.Message):
        self.message = message

    def wait_for(
        self,
        event: str,
        /,
        *,
        check: Optional[Callable[..., bool]] = None,
        timeout: Optional[float] = None,
    ) -> Coro[Any]:
        async def get_message() -> discord.Message:
            message = (
                cast(discord.Message, MessageMocked(content="Hello World"))
                if self.message is None
                else self.message
            )
            assert event == "message" and (check is None or check(message))
            return message

        return get_message()
