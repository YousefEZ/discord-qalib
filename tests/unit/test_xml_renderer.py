import datetime
import unittest
import mock

import discord.ui

import qalib
import qalib.translators
from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter
from qalib.template_engines.jinja2 import Jinja2


@mock.patch("discord.ui.View")
class TestXMLRenderer(unittest.TestCase):
    """Tests the XML Renderer"""

    def test_render(self, view: mock.mock.MagicMock):
        path = "tests/routes/simple_embeds.xml"
        renderer = Renderer(Formatter(), path)
        (embed,) = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self, view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        (embed,) = renderer.render("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self, view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(view.return_value.add_item.call_count, 5)

    def test_select_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})

        self.assertEqual(view.return_value.add_item.call_count, 2)
        child = view.return_value.add_item.call_args_list[0].args[0]
        self.assertIsInstance(child, discord.ui.Select)
        self.assertEqual(child.placeholder, "Select a date")

    def test_channel_select_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(view.return_value.add_item.call_count, 2)

        child = view.return_value.add_item.call_args_list[1].args[0]
        assert isinstance(child, discord.ui.ChannelSelect)
        self.assertEqual(child.placeholder, "Select a channel")

    def test_role_select_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("Launch")
        self.assertEqual(view.return_value.add_item.call_count, 4)
        child = view.return_value.add_item.call_args_list[0].args[0]
        assert isinstance(child, discord.ui.RoleSelect)
        self.assertEqual(child.placeholder, "Select a Role")

    def test_user_select_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("Launch")
        self.assertEqual(view.return_value.add_item.call_count, 4)
        child = view.return_value.add_item.call_args_list[1].args[0]
        self.assertIsInstance(child, discord.ui.UserSelect)
        self.assertEqual(child.placeholder, "Select a User")

    def test_mentionable_select_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("Launch")
        self.assertEqual(view.return_value.add_item.call_count, 4)
        child = view.return_value.add_item.call_args_list[2].args[0]
        self.assertIsInstance(child, discord.ui.MentionableSelect)
        self.assertEqual(child.placeholder, "Select a Mention")

    def test_text_input_rendering(self, view: mock.mock.MagicMock):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        renderer.render("Launch")
        self.assertEqual(view.return_value.add_item.call_count, 4)
        child = view.return_value.add_item.call_args_list[3].args[0]
        self.assertIsInstance(child, discord.ui.TextInput)
        self.assertEqual(child.placeholder, "Test Placeholder")

    def test_emoji_error(self, view: mock.mock.MagicMock):
        path = "tests/routes/error.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(ValueError, renderer.render, "test1")

    def test_element_error(self, view: mock.mock.MagicMock):
        path = "tests/routes/error.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "test2")

    def test_missing_embed_key(self, view: mock.mock.MagicMock):
        path = "tests/routes/simple_embeds.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "missing_key")

    def test_missing_menu_key(self, view: mock.mock.MagicMock):
        path = "tests/routes/simple_embeds.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render_menu, "missing_menu_key")

    def test_jinja_renderer(self, view: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        embed, _ = renderer.render("test1")
        self.assertEqual(len(embed.fields), 3)

    def test_jinja_view_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        renderer.render("test1")
        self.assertEqual(view.return_value.add_item.call_count, 1)

    def test_combined_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        embed, _ = renderer.render("test1")
        self.assertEqual(len(embed.fields), 3)
        self.assertEqual(view.return_value.add_item.call_count, 1)

    def test_jinja_empty_view(self, view: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        message = renderer.render("test2")
        self.assertIs(message.view, None)

    def test_content_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        content, _ = renderer.render("content_test")
        self.assertEqual(content, "This is a test message")

    def test_tts_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        _, tts = renderer.render("tts_test")
        self.assertTrue(tts)

    def test_file_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        message = renderer.render("file_test")
        self.assertIsInstance(message.file, discord.File)
        self.assertEqual(message.file.filename, "complete_messages.xml")

    def test_allowed_mentions_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        message = renderer.render("allowed_mentions_test")
        self.assertIsInstance(message.allowed_mentions, discord.AllowedMentions)
        self.assertFalse(message.allowed_mentions.everyone)

    def test_message_reference(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        message = renderer.render("message_reference_test")
        self.assertIsInstance(message.reference, discord.MessageReference)

    def test_message_reference_missing_message_id(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        self.assertRaises(ValueError, renderer.render, "message_reference_test2")

    def test_message_reference_missing_channel_id(self, view: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        self.assertRaises(ValueError, renderer.render, "message_reference_test3")
