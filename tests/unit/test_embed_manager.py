import datetime
import unittest
from typing import cast

import discord.ext.commands
import jinja2

import qalib.qalib_context
from qalib import EmbedManager, jinja_manager, embed_manager as embed_decorator, JinjaManager
from tests.unit.mocked_classes import ContextMocked, MessageMocked


async def send(self, embed: discord.Embed, view: discord.ui.View, **_) -> MessageMocked:
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

    async def test_xml_rendered_send_message(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")

        e = await embed_manager.rendered_send("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(e.embed.title, "Test")

        e2 = await embed_manager.rendered_send("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(e2.embed.title, "Test2")

    async def test_xml_display_message_with_buttons(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/full_embeds.xml")

        await embed_manager.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(embed_manager._displayed.view.children), 5)

    async def test_xml_menu_display(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/menus.xml", "Menu1")

        await embed_manager.menu()
        self.assertEqual(embed_manager._displayed.embed.title, "Hello World")

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

    async def test_json_menu_display(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/menus.json", "Menu1")

        await embed_manager.menu()
        self.assertEqual(embed_manager._displayed.embed.title, "Hello World")

    async def test_jinja_menu_display(self):
        embed_manager = JinjaManager(self.ctx, jinja2.Environment(loader=jinja2.FileSystemLoader("tests/routes")),
                                     "menus.xml", "Menu1")

        await embed_manager.menu()
        self.assertEqual(embed_manager._displayed.embed.title, "Hello World")

    async def test_menu_arrows(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/menus.xml", "Menu1")

        await embed_manager.menu()
        arrow = embed_manager._displayed.view.children[0]
        self.assertIsInstance(arrow, discord.ui.Button)

        mocked_interaction = type("MockedInteraction", (object,), {})
        mocked_interaction.response = type("MockedResponse", (object,), {})()

        async def edit(embed, view, **kwargs):
            self.assertEqual(embed.title, "Hello Planet")

        mocked_interaction.response.edit_message = edit
        await arrow.callback(cast(discord.Interaction, mocked_interaction))

    async def test_decorator(self):
        @embed_decorator("tests/routes/simple_embeds.json")
        async def test(ctx):
            self.assertIsInstance(ctx, qalib.QalibContext)

        await test(ContextMocked())

    async def test_jinja_manager(self):
        @jinja_manager(jinja2.Environment("tests/routes"), "jinja-test.xml")
        async def test(ctx):
            self.assertIsInstance(ctx, qalib.QalibContext)

        await test(self.ctx)

    def test_jinja_manager_class(self):
        env = jinja2.Environment(loader=jinja2.FileSystemLoader("tests/routes"))
        self.assertTrue(qalib.JinjaManager(self.ctx, env, "jinja-test.xml"))

    def test_root_key_set(self):
        embed_manager = EmbedManager(self.ctx, "tests/routes/menus.xml")
        embed_manager.set_root("Menu1")
