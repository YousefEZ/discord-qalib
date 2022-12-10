import datetime
import unittest

import discord.ext.commands

from qalib import EmbedManager
from qalib import embed_manager as embed_decorator
from tests.unit.mocked_classes import ContextMocked, MessageMocked

discord.ext.commands.Context = ContextMocked


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

        await embed_manager.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(self.ctx.message.embed.title, "Test")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(self.ctx.message.embed.title, "Test2")

    async def test_xml_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
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

        await embed_manager.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(self.ctx.message.embed.title, "Test")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(self.ctx.message.embed.title, "Test2")

    async def test_json_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.json")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(self.ctx.message.view.children), 5)

    def test_decorator(self):
        f = embed_decorator("tests/routes/simple_embeds.json")
        wrapper = f(lambda ctx: ctx)
        embed_manager = wrapper(self.ctx)
        self.assertIsInstance(embed_manager, EmbedManager)
