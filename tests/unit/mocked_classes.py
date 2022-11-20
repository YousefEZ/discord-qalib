from typing import Optional

import discord.ui


class MockedView:

    def __init__(self, timeout: Optional[int] = 180):
        self.children = []
        self.timeout = timeout

    def add_item(self, item: discord.ui.Item):
        self.children.append(item)


class MessageMocked:

    def __init__(self, author=None, channel=None, content=None, embed: Optional[discord.Embed] = None,
                 view: Optional[discord.ui.View] = None):
        self.author = author
        self.channel = channel
        self.content = content
        self.embed = embed
        self.view = view

    async def edit(self, embed=None):
        self.embed = embed


class BotMocked:

    def __init__(self):
        self.message = None

    def inject_message(self, message):
        self.message = message

    async def wait_for(self, event, timeout, check):
        message = MessageMocked(content="Hello World") if self.message is None else self.message
        if event == "message" and check(message):
            return message


class ContextMocked:

    def __init__(self):
        self.message = None
        self.bot = BotMocked()

    async def send(
            self,
            embed: Optional[discord.Embed] = None,
            view: Optional[discord.ui.View] = None
    ) -> MessageMocked:
        self.message = MessageMocked(embed=embed, view=view)
        return self.message
