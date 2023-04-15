from typing import TYPE_CHECKING, List, Literal, Optional, cast

import discord.ext.commands
import discord.ui
from mock import Mock

raw_data = {
    "id": 0,
    "custom_id": "",
    "type": 3,
    "component_type": 2,
    "application_id": 10,
    "token": "token",
    "version": 1,
}

if TYPE_CHECKING:
    from discord.types.interactions import Interaction as InteractionPayload


class MockedInteraction(discord.Interaction):
    def __init__(self):
        super().__init__(data=cast(InteractionPayload, raw_data) if TYPE_CHECKING else raw_data, state=Mock())


class MessageMocked:
    def __init__(
            self,
            author=Mock(),
            channel=Mock(),
            content: str = "",
            embed: Optional[discord.Embed] = None,
            view: Optional[discord.ui.View] = None,
            **kwargs,
    ):
        self.author = author
        self.channel = channel
        self.content = content
        self.embed = embed
        self.view = view
        self._state = Mock()


class BotMocked:
    def __init__(self):
        self.message = MessageMocked()

    def inject_message(self, message):
        self.message = message

    async def wait_for(self, event, timeout, check):
        message = MessageMocked(content="Hello World") if self.message is None else self.message
        if event == "message" and check(message):
            return message


class ContextMocked(discord.ext.commands.Context):
    def __init__(self):
        self.message = MessageMocked()
        self.bot = BotMocked()
        self.view = None
        self.args = None
        self.kwargs = None
        self.prefix = None
        self.command = None
        self.invoked_with = None
        self.invoked_parents = None
        self.invoked_subcommand = None
        self.subcommand_passed = None
        self.command_failed = None
        self.current_parameter = None
        self.current_argument = None
        self.interaction = None
