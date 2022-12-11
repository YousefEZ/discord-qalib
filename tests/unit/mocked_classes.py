from typing import Optional

import discord.ui
from mock import Mock


class MockedView:

    def __init__(self, timeout: Optional[int] = 180):
        self.children = []
        self.timeout = timeout

    def add_item(self, item: discord.ui.Item):
        self.children.append(item)


class MessageMocked:

    def __init__(self, author=Mock(), channel=Mock(), content: str = "", embed: Optional[discord.Embed] = None,
                 view: Optional[discord.ui.View] = None):
        self.author = author
        self.channel = channel
        self.content = content
        self.embed = embed
        self.view = view
        self._state = Mock()

    async def edit(self, author=None, channel=None, content=None, embed: Optional[discord.Embed] = None,
                   view: Optional[discord.ui.View] = None):
        self.author = author
        self.channel = channel
        self.content = content
        self.embed = embed
        self.view = view


class BotMocked:

    def __init__(self):
        self.message = MessageMocked()

    def inject_message(self, message):
        self.message = message

    async def wait_for(self, event, timeout, check):
        message = MessageMocked(content="Hello World") if self.message is None else self.message
        if event == "message" and check(message):
            return message


class ContextMocked:

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
