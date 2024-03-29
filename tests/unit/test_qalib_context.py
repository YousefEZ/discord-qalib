import datetime
import unittest
from typing import cast

import discord
import discord.ext.commands
import discord.interactions
import mock
from discord.ext.commands.view import StringView

import qalib
from qalib import Renderer, RenderingOptions, qalib_context, qalib_interaction
from qalib.context import QalibContext
from qalib.interaction import QalibInteraction
from qalib.template_engines.formatter import Formatter
from qalib.template_engines.jinja2 import Jinja2
from qalib.translators.modal import ModalEvents, QalibModal
from qalib.translators.view import ViewEvents
from tests.unit.mocked_classes import MessageMocked, MockedInteraction, BotMocked
from tests.unit.types import SimpleEmbeds, FullEmbeds, Menus, Modals, ErrorEmbeds


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

    async def test_menu_in_context(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(
            self.ctx, Renderer(Formatter(), "tests/routes/menus.xml")
        )
        await context.display("Menu4")
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

    async def test_xml_render_message_bound_with_timeout(self, *args: mock.mock.MagicMock):
        called = False

        async def test_call(view: discord.ui.View) -> None:
            nonlocal called
            called = True

        renderer = Renderer(Formatter(), "tests/routes/full_embeds.xml")
        message = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()},
                                  events={ViewEvents.ON_TIMEOUT: test_call})
        await message.view.on_timeout()
        self.assertTrue(called)

    async def test_xml_render_message_bound_on_error(self, *args: mock.mock.MagicMock):
        called = False

        async def on_error(
                view: discord.ui.View,
                interaction: discord.Interaction,
                exception: Exception,
                item: discord.ui.Item
        ) -> None:
            nonlocal called
            called = True

        renderer = Renderer(Formatter(), "tests/routes/full_embeds.xml")
        message = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()},
                                  events={ViewEvents.ON_ERROR: on_error})
        await message.view.on_error(MockedInteraction(), Exception(), discord.ui.Button())
        self.assertTrue(called)

    async def test_xml_render_message_bound_on_check(self, *args: mock.mock.MagicMock):
        called = False

        async def on_check(view: discord.ui.View, interaction: discord.Interaction) -> None:
            nonlocal called
            called = True

        renderer = Renderer(Formatter(), "tests/routes/full_embeds.xml")
        message = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()},
                                  events={ViewEvents.ON_CHECK: on_check})
        await message.view.interaction_check(MockedInteraction())
        self.assertTrue(called)

    async def test_xml_render_message_bound_on_default_check(self, *args: mock.mock.MagicMock):
        renderer = Renderer(Formatter(), "tests/routes/full_embeds.xml")
        message = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertTrue(await message.view.interaction_check(MockedInteraction()))

    async def test_xml_menu_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        args[0].assert_called_once()

    async def test_xml_menu_no_timeout_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu2")
        args[0].assert_called_once()

    async def test_interaction_menu(self, *args: mock.mock.MagicMock):
        interaction: QalibInteraction[Menus] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/menus.xml")
        )

        await interaction.menu("Menu1")
        args[-1].assert_called_once()

    async def test_interaction_menu_front_page_change(self, *args: mock.mock.MagicMock):
        interaction: QalibInteraction[Menus] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/menus.xml")
        )

        await interaction.display("Menu1", page=1)
        args[-1].assert_called_once()

    async def test_xml_modal_rendering(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.xml"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        modal = renderer.render("modal1", events={})
        assert isinstance(modal, discord.ui.Modal)
        self.assertEqual(len(modal.children), 2)

    async def test_xml_modal_rendering_with_endless_timeout(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.xml"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        modal = renderer.render("modal2")
        assert isinstance(modal, discord.ui.Modal)
        self.assertEqual(len(modal.children), 1)
        self.assertIsNone(modal.timeout)

    async def test_json_modal_rendering(self, *_: mock.mock.MagicMock):
        path = "tests/routes/modal.json"
        renderer: Renderer[Modals] = Renderer(Formatter(), path)
        modal = renderer.render("modal1", events={})
        assert isinstance(modal, discord.ui.Modal)
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

        await interaction.rendered_send("modal1")
        modal = args[-2].call_args.args[0]
        self.assertEqual(modal.title, "Questionnaire")

    async def test_xml_modal_deprecated_display(self, *args: mock.mock.MagicMock):
        interaction: QalibInteraction[Modals] = QalibInteraction(
            MockedInteraction(), Renderer(Formatter(), "tests/routes/modal.xml")
        )

        await interaction.respond_with_modal("modal1")
        modal = args[-2].call_args.args[0]
        self.assertEqual(modal.title, "Questionnaire")

    async def test_xml_modal_decorator(self, *_: mock.mock.MagicMock):
        @qalib_interaction(Formatter(), "tests/routes/modal.xml")
        async def test_modal(interaction: QalibInteraction[Modals]) -> None:
            return await interaction.rendered_send("modal1")

        await test_modal(MockedInteraction())

    async def test_cog_xml_modal_decorator(self, *_: mock.mock.MagicMock):
        class T:
            @qalib_interaction(Formatter(), "tests/routes/modal.xml")
            async def test_modal(self, interaction: QalibInteraction[Modals]):
                return await interaction.rendered_send("modal1")

        await T().test_modal(MockedInteraction())

    async def test_xml_modal_decorator_method(self, *_: mock.mock.MagicMock):
        class T:
            @qalib_interaction(Formatter(), "tests/routes/modal.xml")
            async def test_modal(self, interaction: QalibInteraction[Modals]) -> None:
                return await interaction.rendered_send("modal1")

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

    async def test_json_menu_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu1")

        args[0].assert_called()

    async def test_json_menu_timeout_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu2")

        args[0].assert_called()

    async def test_xml_menu_expansive(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu3")

        args[0].assert_called()

    async def test_xml_menu_page(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu4")

        args[0].assert_called()

    async def test_json_menu_expansive(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.json"))

        await context.menu("Menu3")

        args[0].assert_called()

    async def test_json_error_page(self, *args: mock.mock.MagicMock):
        context: QalibContext[ErrorEmbeds] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/error.json"))

        with self.assertRaises(TypeError):
            await context.menu("menu_type")

    async def test_jinja_menu_display(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Jinja2(), "tests/routes/menus.xml"))

        await context.menu("Menu1")
        args[0].assert_called()

    async def test_menu_arrows(self, *args: mock.mock.MagicMock):
        context: QalibContext[Menus] = QalibContext(self.ctx, Renderer(Formatter(), "tests/routes/menus.xml"))

        await context.menu("Menu1")

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

    async def test_modal_on_submit(self, *_: mock.mock.MagicMock):
        submitted = False

        async def submit(modal: discord.ui.Modal, interaction: discord.Interaction) -> None:
            nonlocal submitted
            submitted = True

        qalib_modal = QalibModal(title="Test", events={
            ModalEvents.ON_SUBMIT: submit
        })
        await qalib_modal.on_submit(MockedInteraction())
        self.assertTrue(submitted)

    async def test_modal_on_check(self, *_: mock.mock.MagicMock):
        checked = False

        async def check(modal: discord.ui.Modal, interaction: discord.Interaction) -> bool:
            nonlocal checked
            checked = True
            return True

        qalib_modal = QalibModal(title="Test", events={
            ModalEvents.ON_CHECK: check,
        })
        self.assertTrue(await qalib_modal.interaction_check(MockedInteraction()))
        self.assertTrue(checked)

    async def test_modal_on_timeout(self, *_: mock.mock.MagicMock):
        timed_out = False

        async def timeout(modal: discord.ui.Modal) -> None:
            nonlocal timed_out
            timed_out = True
            return

        qalib_modal = QalibModal(title="Test", events={
            ModalEvents.ON_TIMEOUT: timeout,
        })
        await qalib_modal.on_timeout()
        self.assertTrue(timed_out)

    async def test_modal_default_on_check(self, *_: mock.mock.MagicMock):
        qalib_modal = QalibModal(title="Test")
        self.assertTrue(await qalib_modal.interaction_check(MockedInteraction()))

    async def test_modal_on_error(self, *_: mock.mock.MagicMock):
        errored = False

        async def error(modal: discord.ui.Modal, interaction: discord.Interaction, exception: Exception) -> None:
            nonlocal errored
            errored = True
            return

        qalib_modal = QalibModal(title="Test", events={
            ModalEvents.ON_ERROR: error,
        })
        await qalib_modal.on_error(MockedInteraction(), Exception())
        self.assertTrue(errored)

    async def test_button_callback(self, *_: mock.mock.MagicMock):
        invoked = False

        @qalib.qalib_item_interaction(Formatter(), "tests/routes/full_embeds.xml")
        async def callback(item: discord.ui.Item, interaction: QalibInteraction[str]):
            nonlocal invoked
            invoked = True

        renderer: Renderer[str] = Renderer(Formatter(), "tests/routes/full_embeds.xml")
        message = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()},
                                  callbacks={"button1": callback})
        await message.view.children[0].callback(MockedInteraction())
        self.assertTrue(invoked)
