import asyncio
import datetime
import unittest

import discord.ui
import mock
from mock.mock import AsyncMock

from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter
from qalib.translators import BaseMessage, Message
from qalib.translators.menu import Menu, MenuEvents
from tests.unit.mocked_classes import MockedInteraction
from tests.unit.types import FullEmbeds, SelectEmbeds, ErrorEmbeds, CompleteJSONMessages
from tests.unit.utils import render_message


async def callback_mocked(_: discord.Interaction) -> None:
    return None


class TestJSONRenderer(unittest.TestCase):
    """Tests the JSON Renderer"""

    def test_render(self):
        message = render_message("tests/routes/simple_embeds.json", "Launch")
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(message.embed.title, "Hello World")

    def test_full_render(self):
        message = render_message("tests/routes/full_embeds.json", "test_key", todays_date=datetime.datetime.now())
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(message.embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    @mock.patch("asyncio.get_running_loop")
    def test_button_rendering(self, mock_view: mock.mock.MagicMock):
        message = render_message("tests/routes/full_embeds.json", "test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(len(message.view.children), 5)

    @mock.patch("asyncio.get_running_loop")
    def test_button_rendering_with_callback(self, mock_view: mock.mock.MagicMock):
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), "tests/routes/full_embeds.json")
        message = renderer.render("test_key2", callbacks={"button1": callback_mocked},
                                  keywords={"todays_date": datetime.datetime.now()}, events={})

        self.assertGreater(len(message.view.children), 0)
        asyncio.run(message.view.children[0].callback(MockedInteraction()))

    @mock.patch("asyncio.get_running_loop")
    def test_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)

        message = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()}, events={})
        self.assertGreater(len(message.view.children), 0)

    @mock.patch("asyncio.get_running_loop")
    def test_select_rendering_with_callback(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)

        message = renderer.render("test_key3", callbacks={"select1": callback_mocked, "channel1": callback_mocked},
                                  keywords={"todays_date": datetime.datetime.now()}, events={})
        self.assertGreater(len(message.view.children), 0)

    @mock.patch("asyncio.get_running_loop")
    def test_components_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)

        message = renderer.render("Launch", callbacks={
            "test1": callback_mocked,
            "test2": callback_mocked,
            "test3": callback_mocked,
            "test4": callback_mocked,
        }, keywords={"todays_date": datetime.datetime.now()}, events={})
        self.assertGreater(len(message.view.children), 0)
        for child in message.view.children:
            asyncio.run(child.callback(MockedInteraction()))

    @mock.patch("asyncio.get_running_loop")
    def test_component_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)
        message = renderer.render("Launch", events={})

        self.assertGreater(len(message.view.children), 0)

    @mock.patch("asyncio.get_running_loop")
    def test_emoji_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.json"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(ValueError, renderer.render, "test1")

    @mock.patch("asyncio.get_running_loop")
    def test_element_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.json"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "test2")

    def test_content_rendering(self):
        path = "tests/routes/complete_messages.json"
        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), path)
        message = renderer.render("content_test", events={})

        assert isinstance(message, Message)
        self.assertEqual(message.content, "This is a test message")

    @mock.patch("asyncio.get_running_loop")
    def test_expansive_message(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/menus.json"
        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), path)
        message = renderer.render("menu4", events={})

        assert isinstance(message, Menu)

    @mock.patch("asyncio.get_running_loop")
    def test_expansive_message_with_arrows(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/menus.json"
        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), path)
        message = renderer.render("menu5", events={})

        assert isinstance(message, Menu)

    def test_tts_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("tts_test", events={})

        assert isinstance(message, Message)
        self.assertTrue(message.tts)

    def test_json_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("file_test", events={})

        assert isinstance(message, Message)
        assert message.file is not None
        self.assertIsInstance(message.file, discord.File)
        self.assertEqual(message.file.filename, "complete_messages.xml")

    def test_basic_message(self):
        message = BaseMessage(content=None, embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                              ephemeral=None, allowed_mentions=None, suppress_embeds=None, delete_after=None)
        self.assertRaises(NotImplementedError, message.as_edit)

    def test_message_error(self):
        message = Message(content=None, embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                          ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                          delete_after=None, stickers=None, nonce=None, reference=None, mention_author=None,
                          )
        self.assertRaises(NotImplementedError, message.as_edit)

    def test_message_type_error(self):
        template = "tests/routes/error.json"

        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), template)
        self.assertRaises(TypeError, renderer.render, "unknown_type")

    def test_missing_colour(self):
        template = "tests/routes/error.json"

        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), template)
        self.assertRaises(ValueError, renderer.render, "missing_colour")

    @mock.patch("asyncio.get_running_loop")
    def test_menu(self, mock_view: mock.mock.MagicMock):
        messages = [Message(content=None, embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(3)]
        message = Menu(messages)
        assert isinstance(message.front, Message)
        self.assertEqual(sum(len(m.view.children) for m in messages), 4)

    @mock.patch("asyncio.get_running_loop")
    @mock.patch("discord.interactions.InteractionResponse.edit_message", new_callable=AsyncMock)
    def test_menu_with_events(self, mock_response: mock.mock.MagicMock, mock_view: mock.mock.MagicMock):
        messages = [Message(content=None, embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(3)]

        called = False

        async def callback(m: Menu) -> None:
            nonlocal called
            called = True

            self.assertEqual(m.index, 1)

        menu = Menu(messages, events={MenuEvents.ON_CHANGE: callback})
        self.assertEqual(menu.index, 0)
        self.assertEqual(len(menu), 3)
        assert isinstance(menu.front, Message)
        self.assertEqual(sum(len(m.view.children) for m in messages), 4)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(messages[0].view.children[0].callback(MockedInteraction()))
        loop.run_until_complete(task)
        self.assertTrue(called)

    @mock.patch("asyncio.get_running_loop")
    @mock.patch("discord.interactions.InteractionResponse.edit_message", new_callable=AsyncMock)
    def test_setting_front_menu(self, mock_response: mock.mock.MagicMock, mock_view: mock.mock.MagicMock):
        messages = [Message(content=str(_), embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(4)]

        menu = Menu(messages)
        with self.assertRaises(IndexError):
            menu.front = 4

    @mock.patch("asyncio.get_running_loop")
    @mock.patch("discord.interactions.InteractionResponse.edit_message", new_callable=AsyncMock)
    def test_menu_page_retrieval(self, mock_response: mock.mock.MagicMock, mock_view: mock.mock.MagicMock):
        messages = [Message(content=str(_), embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(4)]

        menu = Menu(messages)
        self.assertEqual(menu[3].content, "3")

    @mock.patch("asyncio.get_running_loop")
    @mock.patch("discord.interactions.InteractionResponse.edit_message", new_callable=AsyncMock)
    def test_menu_current_page_retrieval(self, mock_response: mock.mock.MagicMock, mock_view: mock.mock.MagicMock):
        messages = [Message(content=str(_), embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(4)]

        menu = Menu(messages)
        self.assertEqual(menu.current_page().content, "0")

    @mock.patch("asyncio.get_running_loop")
    @mock.patch("discord.interactions.InteractionResponse.edit_message", new_callable=AsyncMock)
    def test_menu_with_added_events(self, mock_response: mock.mock.MagicMock, mock_view: mock.mock.MagicMock):
        messages = [Message(content=str(_), embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(4)]

        called = False

        async def callback(m: Menu) -> None:
            nonlocal called
            called = True

            self.assertEqual(m.index, 1)

        menu = Menu(messages)
        menu.add_event(MenuEvents.ON_CHANGE, callback)
        self.assertEqual(menu.index, 0)
        self.assertEqual(len(menu), 4)
        assert isinstance(menu.front, Message)
        self.assertEqual(sum(len(m.view.children) for m in messages), 6)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        task = loop.create_task(messages[0].view.children[0].callback(MockedInteraction()))
        loop.run_until_complete(task)
        self.assertTrue(called)

    def test_allowed_mentions_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("allowed_mentions_test", events={})

        assert isinstance(message, Message)
        assert message.allowed_mentions is not None
        self.assertIsInstance(message.allowed_mentions, discord.AllowedMentions)
        self.assertFalse(message.allowed_mentions.everyone)

    def test_multi_embed_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("multi_embeds", events={})

        assert isinstance(message, Message)
        self.assertEqual(len(message.embeds), 2)
