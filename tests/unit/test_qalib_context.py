import datetime
import unittest
from typing import cast

import discord.ext.commands
import discord
import discord.interactions
import mock
from discord.ext.commands.view import StringView

from qalib.context import QalibContext
from qalib.interaction import QalibInteraction
from qalib import Formatter, Jinja2, Renderer, RenderingOptions, qalib_context, qalib_interaction
from qalib.translators.message_parsing import create_arrows

from tests.unit.mocked_classes import MessageMocked, MockedInteraction, BotMocked
from tests.unit.types import SimpleEmbeds, FullEmbeds, Menus, Modals


@mock.patch("discord.interactions.InteractionResponse.send_message")
@mock.patch("discord.interactions.InteractionResponse.send_modal")
@mock.patch("discord.Interaction.edit_original_response")
@mock.patch("discord.message.Message")
@mock.patch("discord.ui.View")
@mock.patch("qalib.QalibContext.send")
class TestEmbedManager(unittest.IsolatedAsyncioTestCase):
    def setUp(self, *args: mock.mock.MagicMock):
        self.ctx = discord.ext.commands.Context(
            message=cast(discord.message.Message, MessageMocked()), bot=BotMocked(), view=StringView("")
        )

    async def test_xml_context(self, *args: mock.mock.MagicMock):
        context: QalibContext[SimpleEmbeds] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.xml")
        )
        await context.display("Launch")
        args[0].assert_called_once()

    async def test_xml_get_message(self, *_: mock.mock.MagicMock):
        author, channel = "Yousef", 346712637812
        self.ctx.message = cast(
            discord.Message, MessageMocked(author=author, channel=channel, content="Original Message")
        )

        # simulate a message being received
        waiting_message = cast(discord.Message, MessageMocked(author=author, channel=channel, content="Burning"))
        self.ctx.bot.inject_message(waiting_message)

        context: QalibContext[SimpleEmbeds] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.xml")
        )
        self.assertEqual(await context.get_message(), waiting_message.content)

    async def message_display_test(self, path: str, message: mock.mock.MagicMock):
        context: QalibContext[FullEmbeds] = QalibContext(self.ctx, Renderer(Formatter(), path))

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        message.assert_called_once()

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        message.return_value.edit.assert_called_once()

    async def test_xml_display_message(self, *args: mock.mock.MagicMock):
        await self.message_display_test("tests/routes/full_embeds.xml", args[0])

    async def test_xml_rendered_send_message(self, *args: mock.mock.MagicMock):
        context: QalibContext[FullEmbeds] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml")
        )

        await context.rendered_send("test_key", keywords={"todays_date": datetime.datetime.now()})
        args[0].assert_called_once()

        await context.rendered_send("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(args[0].call_count, 2)

    async def test_xml_pre_rendering(self, *_: mock.mock.MagicMock):
        context: QalibContext[FullEmbeds] = QalibContext(
            self.ctx,
            Renderer(
                Formatter(),
                "tests/routes/full_embeds.xml",
                RenderingOptions.PRE_TEMPLATE,
            ),
        )

        await context.display("test_key", keywords={"todays_date": datetime.datetime.now()})

    async def test_xml_display_message_with_buttons(self, *args: mock.mock.MagicMock):
        context: QalibContext[FullEmbeds] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.xml")
        )

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})

        self.assertEqual(args[1].return_value.add_item.call_count, 5)

    async def test_xml_menu_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        args[0].assert_called_once()

    async def test_interaction_menu(self, *args: mock.mock.MagicMock):
        interaction: QalibInteraction[Menus] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/menus.xml")
        )

        await interaction.menu("Menu1")
        args[-1].assert_called_once()

    async def test_xml_modal_rendering(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.xml"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        modal = renderer.render("modal1")
        self.assertEqual(len(modal.children), 2)

    async def test_json_modal_rendering(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.json"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        modal = renderer.render("modal1")
        self.assertEqual(len(modal.children), 2)

    async def test_json_missing_modal_key(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.json"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "MISSING_KEY")

    async def test_xml_missing_modal_key(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.xml"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "MISSING_KEY")

    async def test_xml_modal_display(self, *args: mock.mock.MagicMock):
        interaction: QalibInteraction[Modals] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/modal.xml")
        )

        await interaction.respond_with_modal("modal1")
        modal = args[-2].call_args.args[0]
        self.assertEqual(modal.title, "Questionnaire")

    async def test_xml_modal_decorator(self, *_: mock.mock.MagicMock):
        @qalib_interaction(Formatter(), "tests/routes/modal.xml")
        async def test_modal(interaction: QalibInteraction[Modals]) -> None:
            return await interaction.respond_with_modal("modal1")

        await test_modal(MockedInteraction())

    async def test_cog_xml_modal_decorator(self, *_: mock.mock.MagicMock):
        class T:
            @qalib_interaction(Formatter(), "tests/routes/modal.xml")
            async def test_modal(self, interaction):
                return await interaction.respond_with_modal("modal1")

        await T().test_modal(MockedInteraction())

    async def test_xml_modal_decorator_method(self, *_: mock.mock.MagicMock):
        class T:
            @qalib_interaction(Formatter(), "tests/routes/modal.xml")
            async def test_modal(self, interaction: QalibInteraction[Modals]) -> None:
                return await interaction.respond_with_modal("modal1")

        t = T()
        await t.test_modal(MockedInteraction())

    async def test_interaction_rendered_send(self, *args: mock.mock.MagicMock):
        @qalib_interaction(Formatter(), "tests/routes/simple_embeds.xml")
        async def test_modal(interaction: QalibInteraction[SimpleEmbeds]):
            return await interaction.rendered_send("Launch")

        await test_modal(MockedInteraction())
        args[-1].assert_called_once()

    async def test_xml_interaction(self, *_: mock.mock.MagicMock):
        interaction: QalibInteraction[SimpleEmbeds] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/simple_embeds.xml")
        )
        await interaction.display("Launch")

    async def test_rendered_send_interaction(self, *args: mock.mock.MagicMock):
        interaction: QalibInteraction[FullEmbeds] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/full_embeds.xml")
        )

        await interaction.rendered_send("test_key", keywords={"todays_date": datetime.datetime.now()})
        args[-1].assert_called_once()

        await interaction.rendered_send("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(args[-1].call_count, 2)

    async def test_xml_display_message_interaction(self, *_: mock.mock.MagicMock):
        interaction: QalibInteraction[FullEmbeds] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/full_embeds.xml")
        )

        await interaction.display("test_key", keywords={"todays_date": datetime.datetime.now()})
        await interaction.display("test_key2", keywords={"todays_date": datetime.datetime.now()})

    async def test_json_context(self, *args: mock.mock.MagicMock):
        context: QalibContext[SimpleEmbeds] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/simple_embeds.json")
        )
        await context.display("Launch")

        args[0].assert_called_once()

    async def test_json_display_message(self, *args: mock.mock.MagicMock):
        await self.message_display_test("tests/routes/full_embeds.json", args[0])

    async def test_json_display_message_with_buttons(self, *args: mock.mock.MagicMock):
        context: QalibContext[FullEmbeds] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/full_embeds.json")
        )

        await context.display("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(args[1].return_value.add_item.call_count, 5)

    async def test_json_menu_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu1")

        args[0].assert_called()

    async def test_menu_arrows_callback(self, *_: mock.mock.MagicMock):
        renderer: Renderer[SimpleEmbeds] = Renderer(Formatter(), "tests/routes/simple_embeds.xml")
        launch1 = renderer.render("Launch")
        arrow = create_arrows(left=launch1)[0]
        with mock.patch(
            'discord.interactions.InteractionResponse.edit_message', new_callable=mock.mock.AsyncMock
        ) as inter:
            await arrow.callback(MockedInteraction())
            inter.assert_called_once()

    async def test_jinja_menu_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Jinja2(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        args[0].assert_called()

    async def test_menu_arrows(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        self.assertEqual(args[1].return_value.add_item.call_count, 2)

    async def test_decorator(self, *_: mock.mock.MagicMock):
        @qalib_context(Formatter(), "tests/routes/simple_embeds.json")
        async def test(ctx: QalibContext[SimpleEmbeds]):
            self.assertIsInstance(ctx, QalibContext)

        await test(
            discord.ext.commands.Context(
                message=cast(discord.message.Message, MessageMocked()), bot=BotMocked(), view=StringView("")
            )
        )

    async def test_cog_decorator(self, *_: mock.mock.MagicMock):
        test_obj = self

        class T:
            @qalib_context(Formatter(), "tests/routes/simple_embeds.json")
            async def test(self, ctx):
                test_obj.assertIsInstance(ctx, QalibContext)

        await T().test(
            discord.ext.commands.Context(
                message=cast(discord.message.Message, MessageMocked()), bot=BotMocked(), view=StringView("")
            )
        )
