import datetime
import unittest
from typing import Literal

import discord.ext.commands
import discord
import discord.interactions
import mock

import qalib.context
from qalib import Formatter, Jinja2, QalibInteraction, Renderer, RenderingOptions, qalib_context, qalib_interaction
from qalib.renderer import create_arrows
from tests.unit.mocked_classes import ContextMocked, MessageMocked, MockedInteraction


@mock.patch("discord.interactions.InteractionResponse.send_message")
@mock.patch("discord.interactions.InteractionResponse.send_modal")
@mock.patch("discord.Interaction.edit_original_response")
@mock.patch("discord.ui.View")
@mock.patch("qalib.QalibContext.send")
class TestEmbedManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self, *args: mock.mock.MagicMock):
        self.ctx = ContextMocked()

    async def test_xml_context(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.xml"))
        await context.display("Launch")
        args[0].assert_called_once()

    async def test_xml_get_message(self, *args: mock.mock.MagicMock):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.xml"))
        self.assertEqual(await context.get_message(), waiting_message.content)

    async def test_xml_display_message(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        args[0].assert_called_once()

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        args[0].return_value.edit.assert_called_once()

    async def test_xml_rendered_send_message(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await context.rendered_send("test_key", keywords={"todays_date": datetime.datetime.now()})
        args[0].assert_called_once()

        await context.rendered_send("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(args[0].call_count, 2)

    async def test_xml_pre_rendering(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(
            self.ctx,
            Renderer(
                Formatter(),
                "tests/routes/full_embeds.xml",
                RenderingOptions.PRE_TEMPLATE,
            ),
        )

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})

    async def test_xml_display_message_with_buttons(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})

        self.assertEqual(args[1].return_value.add_item.call_count, 5)

    async def test_xml_menu_display(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        args[0].assert_called_once()

    async def test_interaction_menu(self, *args: mock.mock.MagicMock):
        interaction = qalib.QalibInteraction(MockedInteraction(), Renderer(Formatter(), "tests/routes/menus.xml"))

        await interaction.menu("Menu1")
        args[-1].assert_called_once()

    async def test_xml_modal_rendering(self, *args: mock.mock.MagicMock):
        path = "tests/routes/modal.xml"
        renderer = Renderer(Formatter(), path)
        modal = renderer.render_modal("modal1")
        self.assertEqual(len(modal.children), 2)

    async def test_json_modal_rendering(self, *args: mock.mock.MagicMock):
        path = "tests/routes/modal.json"
        renderer = Renderer(Formatter(), path)
        modal = renderer.render_modal("modal1")
        self.assertEqual(len(modal.children), 2)

    async def test_json_missing_modal_key(self, *args: mock.mock.MagicMock):
        path = "tests/routes/modal.json"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render_modal, "MISSING_KEY")

    async def test_xml_missing_modal_key(self, *args: mock.mock.MagicMock):
        path = "tests/routes/modal.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render_modal, "MISSING_KEY")

    async def test_xml_modal_display(self, *args: mock.mock.MagicMock):
        interaction = qalib.QalibInteraction(MockedInteraction(), Renderer(Formatter(), "tests/routes/modal.xml"))

        await interaction.respond_with_modal("modal1")
        modal = args[-2].call_args.args[0]
        self.assertEqual(modal.title, "Questionnaire")

    async def test_xml_modal_decorator(self, *args: mock.mock.MagicMock):
        @qalib_interaction(Formatter(), "tests/routes/modal.xml")
        async def test_modal(interaction):
            return await interaction.respond_with_modal("modal1")

        await test_modal(MockedInteraction())

    async def test_cog_xml_modal_decorator(self, *args: mock.mock.MagicMock):
        class T:
            @qalib_interaction(Formatter(), "tests/routes/modal.xml")
            async def test_modal(self, interaction):
                return await interaction.respond_with_modal("modal1")

        await T().test_modal(MockedInteraction())

    async def test_xml_modal_decorator_method(self, *args: mock.mock.MagicMock):
        class T:
            @qalib_interaction(Formatter(), "tests/routes/modal.xml")
            async def test_modal(self, interaction):
                return await interaction.respond_with_modal("modal1")

        t = T()
        await t.test_modal(MockedInteraction())

    async def test_interaction_rendered_send(self, *args: mock.mock.MagicMock):
        @qalib_interaction(Formatter(), "tests/routes/simple_embeds.xml")
        async def test_modal(interaction: QalibInteraction[Literal["Launch"]]):
            return await interaction.rendered_send("Launch")

        await test_modal(MockedInteraction())
        args[-1].assert_called_once()

    async def test_xml_interaction(self, *args: mock.mock.MagicMock):
        interaction = qalib.QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/simple_embeds.xml")
        )
        await interaction.display("Launch")

    async def test_rendered_send_interaction(self, *args: mock.mock.MagicMock):
        interaction = qalib.QalibInteraction(MockedInteraction(), Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await interaction.rendered_send("test_key", keywords={"todays_date": datetime.datetime.now()})
        args[-1].assert_called_once()

        await interaction.rendered_send("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(args[-1].call_count, 2)

    async def test_xml_display_message_interaction(self, *args: mock.mock.MagicMock):
        interaction = qalib.QalibInteraction(MockedInteraction(), Renderer(Formatter(), "tests/routes/full_embeds.xml"))

        await interaction.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        await interaction.display("test_key2", keywords={"todays_date": datetime.datetime.now()})

    async def test_json_context(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.json"))
        await context.display("Launch")

        args[0].assert_called_once()

    async def test_json_get_message(self, *args: mock.mock.MagicMock):
        author, channel = "Yousef", 346712637812
        self.ctx.message = MessageMocked(author=author, channel=channel, content="Original Message")

        # simulate a message being received
        waiting_message = MessageMocked(author=author, channel=channel, content="Burning")
        self.ctx.bot.inject_message(waiting_message)

        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.json"))
        self.assertEqual(await context.get_message(), waiting_message.content)

    async def test_json_display_message(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.json"))

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        args[0].assert_called_once()

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        args[0].return_value.edit.assert_called_once()

    async def test_json_display_message_with_buttons(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.json"))

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(args[1].return_value.add_item.call_count, 5)

    async def test_json_menu_display(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu1")

        args[0].assert_called()

    async def test_json_menu_display_callback(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu1")
        args[0].assert_called()

    async def test_menu_arrows_callback(self, *args: mock.mock.MagicMock):
        renderer = Renderer(Formatter(), "tests/routes/simple_embeds.xml")
        launch1 = renderer.render("Launch")
        arrow = create_arrows(left=launch1)[0]
        with mock.patch('discord.interactions.InteractionResponse.edit_message',
                        new_callable=mock.mock.AsyncMock) as inter:
            await arrow.callback(MockedInteraction())
            inter.assert_called_once()

    async def test_jinja_menu_display(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Jinja2(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        args[0].assert_called()

    async def test_menu_arrows(self, *args: mock.mock.MagicMock):
        context = qalib.QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        self.assertEqual(args[1].return_value.add_item.call_count, 2)

    async def test_decorator(self, *args: mock.mock.MagicMock):
        @qalib_context(Formatter(), "tests/routes/simple_embeds.json")
        async def test(ctx):
            self.assertIsInstance(ctx, qalib.QalibContext)

        await test(ContextMocked())

    async def test_cog_decorator(self, *args: mock.mock.MagicMock):
        test_obj = self

        class T:
            @qalib_context(Formatter(), "tests/routes/simple_embeds.json")
            async def test(self, ctx):
                test_obj.assertIsInstance(ctx, qalib.QalibContext)

        await T().test(ContextMocked())
