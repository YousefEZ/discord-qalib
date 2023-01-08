import datetime
import unittest
from typing import cast

import discord.ext.commands

import qalib.context
from qalib import Renderer, Formatter, qalib_context, Jinja2, RenderingOptions
from tests.unit.mocked_classes import ContextMocked, MessageMocked, MockedInteraction


async def send(self, embed: discord.Embed, view: discord.ui.View, **_) -> MessageMocked:
    self.message = MessageMocked(embed=embed, view=view)
    return self.message


async def send_modal(self, modal):
    return modal


qalib.QalibContext.send = send
discord.InteractionResponse.send_modal = send_modal

class TestEmbedManager(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.ctx = ContextMocked()

    async def test_xml_context(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.xml"))
        await context.display("Launch")
        self.assertEqual(context._displayed.embed.title, "Hello World")

    async def test_xml_get_message(self):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.xml"))
        self.assertEqual(await context.get_message(), waiting_message.content)

    async def test_xml_display_message(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(context._displayed.embed.title, "Test")

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(context._displayed.embed.title, "Test2")

    async def test_xml_rendered_send_message(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        e = await context.rendered_send("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(e.embed.title, "Test")

        e2 = await context.rendered_send("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(e2.embed.title, "Test2")

    async def test_xml_pre_rendering(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml",
                                                        RenderingOptions.PRE_TEMPLATE))

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})

    async def test_xml_display_message_with_buttons(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(context._displayed.view.children), 5)

    async def test_xml_menu_display(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        self.assertEqual(context._displayed.embed.title, "Hello World")

    async def test_xml_modal_rendering(self):
        path = "tests/routes/modal.xml"
        renderer = Renderer(Formatter(), path)
        modal = renderer.render_modal("modal1")
        self.assertEqual(len(modal.children), 2)

    async def test_json_modal_rendering(self):
        path = "tests/routes/modal.json"
        renderer = Renderer(Formatter(), path)
        modal = renderer.render_modal("modal1")
        self.assertEqual(len(modal.children), 2)

    async def test_json_missing_modal_key(self):
        path = "tests/routes/modal.json"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render_modal, "MISSING_KEY")

    async def test_xml_missing_modal_key(self):
        path = "tests/routes/modal.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render_modal, "MISSING_KEY")

    async def test_xml_modal_display(self):
        interaction = qalib.QalibInteraction(MockedInteraction(),
                                             Renderer(Formatter(), "tests/routes/modal.xml"))

        modal = await interaction.respond_with_modal("modal1")
        modal = cast(discord.ui.Modal, modal)
        self.assertEqual(modal.title, "Questionnaire")

    async def test_xml_modal_decorator(self):
        @qalib.qalib_interaction(Formatter(), "tests/routes/modal.xml")
        async def test_modal(_, response: qalib.QalibInteraction):
            return await response.respond_with_modal("modal1")

        await test_modal(MockedInteraction())

    async def test_json_context(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.json"))
        await context.display("Launch")
        self.assertEqual(context._displayed.embed.title, "Hello World")

    async def test_json_get_message(self):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.json"))
        self.assertEqual(await context.get_message(), waiting_message.content)

    async def test_json_display_message(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.json"))

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(context._displayed.embed.title, "Test")

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(context._displayed.embed.title, "Test2")

    async def test_json_display_message_with_buttons(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.json"))

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(context._displayed.view.children), 5)

    async def test_json_menu_display(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu1")
        self.assertEqual(context._displayed.embed.title, "Hello World")

    async def test_jinja_menu_display(self):
        context = qalib.QalibContext(self.ctx, Renderer(Jinja2(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        self.assertEqual(context._displayed.embed.title, "Hello World")

    async def test_menu_arrows(self):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        arrow = context._displayed.view.children[0]
        self.assertIsInstance(arrow, discord.ui.Button)

        mocked_interaction = type("MockedInteraction", (object,), {})
        mocked_interaction.response = type("MockedResponse", (object,), {})()

        async def edit(embed, view, **kwargs):
            self.assertEqual(embed.title, "Hello Planet")

        mocked_interaction.response.edit_message = edit
        await arrow.callback(cast(discord.Interaction, mocked_interaction))

    async def test_decorator(self):
        @qalib_context(Formatter(), "tests/routes/simple_embeds.json")
        async def test(ctx):
            self.assertIsInstance(ctx, qalib.QalibContext)

        await test(ContextMocked())
