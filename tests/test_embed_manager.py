import unittest

from qalib.embed_manager import EmbedManager
from tests.mocked_classes import ContextMocked, MessageMocked

import datetime

class TestEmbedManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.ctx = ContextMocked()

    async def test_embed_manager(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.xml")
        await embed_manager.display("Launch")
        self.assertEqual(self.ctx.message.embed.title, "Hello World")

    async def test_get_message(self):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.xml")
        self.assertEqual(await embed_manager.get_message(), waiting_message.content)

    async def test_display_message(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")
        await embed_manager.display("test_key", todays_date=datetime.datetime.now())
        self.assertEqual(self.ctx.message.embed.title, "Test")
        await embed_manager.display("test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(self.ctx.message.embed.title, "Test2")
