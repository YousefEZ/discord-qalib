import datetime
import unittest

from typing import Optional

import discord.ext.commands

import qalib.qalib_context
from qalib import EmbedManager, jinja_manager, menu_manager, embed_manager as embed_decorator, MenuManager, JinjaManager
from tests.unit.mocked_classes import ContextMocked, MessageMocked


async def send(self, embed: discord.Embed, view: discord.ui.View, **k) -> MessageMocked:
    self.message = MessageMocked(embed=embed, view=view)
    return self.message


qalib.qalib_context.QalibContext.send = send


class TestEmbedManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.ctx = ContextMocked()

    async def test_xml_embed_manager(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.xml")
        await embed_manager.display("Launch")
        self.assertEqual(embed_manager._displayed.embed.title, "Hello World")

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
        self.assertEqual(embed_manager._displayed.embed.title, "Test")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed_manager._displayed.embed.title, "Test2")

    async def test_xml_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(embed_manager._displayed.view.children), 5)

    async def test_json_embed_manager(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/simple_embeds.json")
        await embed_manager.display("Launch")
        self.assertEqual(embed_manager._displayed.embed.title, "Hello World")

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
        self.assertEqual(embed_manager._displayed.embed.title, "Test")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed_manager._displayed.embed.title, "Test2")

    async def test_json_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.json")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(embed_manager._displayed.view.children), 5)

    async def test_decorator(self):
        @embed_decorator("tests/routes/simple_embeds.json")
        async def test(ctx):
            self.assertIsInstance(ctx, EmbedManager)

        await test(ContextMocked())

    def test_menu_manager(self):
        @menu_manager("tests/routes/menus.json", "Menu1")
        def test(ctx):
            self.assertIsInstance(ctx, MenuManager)

        test(self.ctx)

    def test_jinja_manager(self):
        @jinja_manager("jinja-test.xml", "tests/routes")
        def test(ctx):
            self.assertIsInstance(ctx, JinjaManager)

        test(self.ctx)
