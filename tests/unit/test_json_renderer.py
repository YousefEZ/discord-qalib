import asyncio
import datetime
import unittest

import discord.ui
import mock

from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter
from qalib.translators import BaseMessage, Message
from qalib.translators.message_parsing import make_menu
from tests.unit.mocked_classes import MockedInteraction
from tests.unit.types import FullEmbeds, SelectEmbeds, ErrorEmbeds, CompleteJSONMessages
from tests.unit.utils import render_message


async def callback_mocked(_: discord.Interaction) -> None:
    return None


class TestJSONRenderer(unittest.TestCase):
    """Tests the JSON Renderer"""

    def test_render(self):
        message = render_message("tests/routes/simple_embeds.json", "Launch")
        assert message.embed is not None
        self.assertEqual(message.embed.title, "Hello World")

    def test_full_render(self):
        message = render_message("tests/routes/full_embeds.json", "test_key", todays_date=datetime.datetime.now())
        assert message.embed is not None
        self.assertEqual(message.embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    @mock.patch("discord.ui.View")
    def test_button_rendering(self, mock_view: mock.mock.MagicMock):
        render_message("tests/routes/full_embeds.json", "test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(mock_view.return_value.add_item.call_count, 5)

    @mock.patch("discord.ui.View")
    def test_button_rendering_with_callback(self, mock_view: mock.mock.MagicMock):
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), "tests/routes/full_embeds.json")
        renderer.render(
            "test_key2", callbacks={"button1": callback_mocked}, keywords={"todays_date": datetime.datetime.now()}
        )

        self.assertGreater(mock_view.return_value.add_item.call_count, 0)
        asyncio.run(mock_view.return_value.add_item.call_args_list[0].args[0].callback(MockedInteraction()))

    @mock.patch("discord.ui.View")
    def test_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)

        renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_select_rendering_with_callback(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)

        renderer.render(
            "test_key3",
            callbacks={"select1": callback_mocked, "channel1": callback_mocked},
            keywords={"todays_date": datetime.datetime.now()},
        )
        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_components_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)

        renderer.render(
            "Launch",
            callbacks={
                "test1": callback_mocked,
                "test2": callback_mocked,
                "test3": callback_mocked,
                "test4": callback_mocked,
            },
            keywords={"todays_date": datetime.datetime.now()},
        )
        self.assertGreater(mock_view.return_value.add_item.call_count, 0)
        for i in range(mock_view.return_value.add_item.call_count):
            asyncio.run(mock_view.return_value.add_item.call_args_list[i].args[0].callback(MockedInteraction()))

    @mock.patch("discord.ui.View")
    def test_component_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)
        renderer.render("Launch")

        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_emoji_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.json"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(ValueError, renderer.render, "test1")

    @mock.patch("discord.ui.View")
    def test_element_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.json"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "test2")

    def test_content_rendering(self):
        path = "tests/routes/complete_messages.json"
        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), path)
        message = renderer.render("content_test")
        self.assertEqual(message.content, "This is a test message")

    def test_tts_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("tts_test")
        self.assertTrue(message.tts)

    def test_json_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("file_test")
        assert message.file is not None
        self.assertIsInstance(message.file, discord.File)
        self.assertEqual(message.file.filename, "complete_messages.xml")

    def test_basic_message(self):
        message = BaseMessage(content=None, embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                              ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                              delete_after=None)
        self.assertRaises(NotImplementedError, message.as_edit)

    @mock.patch("discord.ui.View")
    def test_menu(self, mock_view: mock.mock.MagicMock):
        messages = [Message(content=None, embed=None, embeds=None, file=None, files=None, view=None, tts=None,
                            ephemeral=None, allowed_mentions=None, suppress_embeds=None, silent=None,
                            delete_after=None, mention_author=None, nonce=None, reference=None, stickers=None)
                    for _ in range(3)]
        message = make_menu(messages)
        self.assertIsInstance(message, Message)
        self.assertEqual(mock_view.return_value.add_item.call_count, 4)

    def test_allowed_mentions_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteJSONMessages] = Renderer(Formatter(), template)
        message = renderer.render("allowed_mentions_test")
        assert message.allowed_mentions is not None
        self.assertIsInstance(message.allowed_mentions, discord.AllowedMentions)
        self.assertFalse(message.allowed_mentions.everyone)
