import datetime
import unittest

from qalib.embed_manager import EmbedManager
from tests.unit.mocked_classes import ContextMocked, MessageMocked


class TestEmbedManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.ctx = ContextMocked()

    async def test_xml_embed_manager(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.xml")
        await embed_manager.display("Launch")
        self.assertEqual(self.ctx.message.embed.title, "Hello World")

    async def test_xml_get_message(self):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.xml")
        self.assertEqual(await embed_manager.get_message(), waiting_message.content)

    async def test_xml_display_message(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")

        await embed_manager.display("test_key", todays_date=datetime.datetime.now())
        self.assertEqual(self.ctx.message.embed.title, "Test")

        await embed_manager.display("test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(self.ctx.message.embed.title, "Test2")

    async def test_xml_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")

        await embed_manager.display("test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(len(self.ctx.message.view.children), 5)

    async def test_json_embed_manager(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.json")
        await embed_manager.display("Launch")
        self.assertEqual(self.ctx.message.embed.title, "Hello World")

    async def test_json_get_message(self):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.json")
        self.assertEqual(await embed_manager.get_message(), waiting_message.content)

    async def test_json_display_message(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.json")

        await embed_manager.display("test_key", todays_date=datetime.datetime.now())
        self.assertEqual(self.ctx.message.embed.title, "Test")

        await embed_manager.display("test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(self.ctx.message.embed.title, "Test2")

    async def test_json_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.json")

        await embed_manager.display("test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(len(self.ctx.message.view.children), 5)
