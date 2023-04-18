import datetime
import unittest
from typing import Literal

import discord.ui
import mock

from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter

SimpleEmbeds = Literal["Launch", "Launch2"]
FullEmbeds = Literal["Launch", "test_key", "test_key2", "test_key3"]
SelectEmbeds = Literal["Launch"]
CompleteEmbeds = Literal["content_test", "tts_test", "file_test", "allowed_mentions_test"]
ErrorEmbeds = Literal["test1", "test2"]


class TestJSONRenderer(unittest.TestCase):
    """Tests the JSON Renderer"""

    def test_render(self):
        path = "tests/routes/simple_embeds.json"
        renderer: Renderer[SimpleEmbeds] = Renderer(Formatter(), path)
        (embed,) = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        (embed,) = renderer.render("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    @mock.patch("discord.ui.View")
    def test_button_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(mock_view.return_value.add_item.call_count, 5)

    @mock.patch("discord.ui.View")
    def test_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_channel_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.json"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_role_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")

        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_user_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")

        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_mentionable_select_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")

        self.assertGreater(mock_view.return_value.add_item.call_count, 0)

    @mock.patch("discord.ui.View")
    def test_text_input_rendering(self, mock_view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.json"
        renderer: Renderer[SelectEmbeds] = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")

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
        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), path)
        content, _ = renderer.render("content_test")
        self.assertEqual(content, "This is a test message")

    def test_tts_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        _, tts = renderer.render("tts_test")
        self.assertTrue(tts)

    def test_json_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("file_test")
        assert message.file is not None
        self.assertIsInstance(message.file, discord.File)
        self.assertEqual(message.file.filename, "complete_messages.xml")

    def test_allowed_mentions_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("allowed_mentions_test")
        assert message.allowed_mentions is not None
        self.assertIsInstance(message.allowed_mentions, discord.AllowedMentions)
        self.assertFalse(message.allowed_mentions.everyone)
