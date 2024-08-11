import datetime
import unittest

import discord.ui
import mock

from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter
from qalib.template_engines.jinja2 import Jinja2
from qalib.translators import Message
from qalib.translators.menu import Menu
from tests.unit.types import FullEmbeds, ErrorEmbeds, SimpleEmbeds, JinjaEmbeds, CompleteEmbeds
from tests.unit.utils import render_message


def render_select_test_key3() -> Message:
    path = "tests/routes/full_embeds.xml"
    renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
    return renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})


@mock.patch("asyncio.get_running_loop")
class TestXMLRenderer(unittest.TestCase):
    """Tests the XML Renderer"""

    def test_render(self, _: mock.mock.MagicMock):
        message = render_message("tests/routes/simple_embeds.xml", "Launch")
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(message.embed.title, "Hello World")

    def test_full_render(self, _: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        message = renderer.render("test_key", keywords={"todays_date": datetime.datetime.now()})
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(message.embed.title, "Test")

    def test_key_not_exist(self, _: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self, view: mock.mock.MagicMock):
        message = render_message("tests/routes/full_embeds.xml", "test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(len(message.view.children), 5)

    def test_button_rendering_with_callback(self, view: mock.mock.MagicMock):
        path = "tests/routes/full_embeds.xml"
        renderer: Renderer[FullEmbeds] = Renderer(Formatter(), path)
        message = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()})

        self.assertEqual(len(message.view.children), 5)

    def test_missing_components(self, view: mock.mock.MagicMock):
        path = "tests/routes/simple_embeds.xml"
        renderer: Renderer[SimpleEmbeds] = Renderer(Formatter(), path)
        renderer.render("Launch2")

        self.assertEqual(view.add_item.call_count, 0)

    def test_select_rendering(self, view: mock.mock.MagicMock):
        message = render_select_test_key3()
        self.assertEqual(len(message.view.children), 2)

        child = message.view.children[0]
        self.assertIsInstance(child, discord.ui.Select)
        self.assertEqual(child.placeholder, "Select a date")

    def test_channel_select_rendering(self, view: mock.mock.MagicMock):
        message = render_select_test_key3()
        self.assertEqual(len(message.view.children), 2)

        child = message.view.children[1]
        assert isinstance(child, discord.ui.ChannelSelect)
        self.assertEqual(child.placeholder, "Select a channel")

    def test_role_select_rendering(self, view: mock.mock.MagicMock):
        message = render_message("tests/routes/select_embeds.xml", "Launch")
        self.assertEqual(len(message.view.children), 4)
        child = message.view.children[0]
        assert isinstance(child, discord.ui.RoleSelect)
        self.assertEqual(child.placeholder, "Select a Role")

    def test_user_select_rendering(self, view: mock.mock.MagicMock):
        message = render_message("tests/routes/select_embeds.xml", "Launch")
        self.assertEqual(len(message.view.children), 4)
        child = message.view.children[1]
        self.assertIsInstance(child, discord.ui.UserSelect)
        self.assertEqual(child.placeholder, "Select a User")

    def test_mentionable_select_rendering(self, view: mock.mock.MagicMock):
        message = render_message("tests/routes/select_embeds.xml", "Launch")
        self.assertEqual(len(message.view.children), 4)
        child = message.view.children[2]
        self.assertIsInstance(child, discord.ui.MentionableSelect)
        self.assertEqual(child.placeholder, "Select a Mention")

    def test_text_input_rendering(self, view: mock.mock.MagicMock):
        message = render_message("tests/routes/select_embeds.xml", "Launch")
        assert isinstance(message, Message)
        view = message.view
        assert view is not None
        self.assertEqual(len(view.children), 4)
        child = view.children[3]
        self.assertIsInstance(child, discord.ui.TextInput)
        self.assertEqual(child.placeholder, "Test Placeholder")

    def test_emoji_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.xml"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(ValueError, renderer.render, "test1")

    def test_unknown_type_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.xml"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(TypeError, renderer.render, "unknown_type")

    def test_element_error(self, _: mock.mock.MagicMock):
        path = "tests/routes/error.xml"
        renderer: Renderer[ErrorEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "test2")

    def test_missing_embed_key(self, _: mock.mock.MagicMock):
        path = "tests/routes/simple_embeds.xml"
        renderer: Renderer[SimpleEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "missing_key")

    def test_missing_menu_key(self, _: mock.mock.MagicMock):
        path = "tests/routes/simple_embeds.xml"
        renderer: Renderer[SimpleEmbeds] = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "missing_menu_key")

    def test_jinja_renderer(self, _: mock.mock.MagicMock):
        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), "tests/routes/jinja-test.xml")
        message = renderer.render("test1")
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(len(message.embed.fields), 3)

    def test_jinja_environment(self, _: mock.mock.MagicMock):
        jinja = Jinja2()
        self.assertTrue(jinja.environment)
        renderer: Renderer[JinjaEmbeds] = Renderer(jinja, "tests/routes/jinja-test.xml")
        message = renderer.render("test1")
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(len(message.embed.fields), 3)

    def test_expansive_message(self, _: mock.mock.MagicMock):
        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), "tests/routes/jinja-test.xml")
        message = renderer.render("test3")
        self.assertIsNotNone(message)

    def test_expansive_with_static_elements(self, _: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), template)
        messages = renderer.render("test5")
        assert isinstance(messages, Menu)
        self.assertEqual(len(messages), 2)
        for idx in range(len(messages)):
            embed = messages[idx].embed
            assert embed is not None
            self.assertEqual(embed.fields, 2)

    def test_expansive_no_footer(self, _: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), template)
        message = renderer.render("test6")
        self.assertEqual(len(message), 2)

    def test_expansive_message_with_timeout(self, _: mock.mock.MagicMock):
        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), "tests/routes/jinja-test.xml")
        message = renderer.render("test4")
        self.assertIsNotNone(message)

    def test_jinja_view_rendering(self, view: mock.mock.MagicMock):
        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), "tests/routes/jinja-test.xml")
        message = renderer.render("test1")
        assert isinstance(message, Message)
        assert message.view
        self.assertEqual(len(message.view.children), 1)

    def test_combined_rendering(self, view: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), template)
        message = renderer.render("test1")
        assert isinstance(message, Message)
        assert message.embed is not None
        assert message.view is not None
        self.assertEqual(len(message.embed.fields), 3)
        self.assertEqual(len(message.view.children), 1)

    def test_jinja_empty_view(self, _: mock.mock.MagicMock):
        template = "tests/routes/jinja-test.xml"

        renderer: Renderer[JinjaEmbeds] = Renderer(Jinja2(), template)
        message = renderer.render("test2")
        assert isinstance(message, Message)
        assert message.embed is not None
        self.assertEqual(len(message.embed.fields), 3)

    def test_content_rendering(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("content_test")
        assert isinstance(message, Message)
        self.assertEqual(message.content, "This is a test message")

    def test_tts_rendering(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("tts_test")
        assert isinstance(message, Message)
        self.assertTrue(message.tts)

    def test_file_rendering(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("file_test")
        assert isinstance(message, Message)
        self.assertIsInstance(message.file, discord.File)
        assert message.file is not None
        self.assertEqual(message.file.filename, "complete_messages.xml")

    def test_allowed_mentions_rendering(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("allowed_mentions_test")
        assert isinstance(message, Message)
        self.assertIsInstance(message.allowed_mentions, discord.AllowedMentions)
        assert message.allowed_mentions is not None
        self.assertFalse(message.allowed_mentions.everyone)

    def test_message_reference(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("message_reference_test")
        assert isinstance(message, Message)
        self.assertIsInstance(message.reference, discord.MessageReference)

    def test_message_reference_missing_message_id(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        self.assertRaises(ValueError, renderer.render, "message_reference_test2")

    def test_message_reference_missing_channel_id(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        self.assertRaises(ValueError, renderer.render, "message_reference_test3")

    def test_empty_content_message(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("empty_content_test")
        assert isinstance(message, Message), "Expected Message instance"
        content = message.content
        assert content is not None
        self.assertEqual(content.strip(), "")

    def test_multi_line_content_message(self, _: mock.mock.MagicMock):
        template = "tests/routes/complete_messages.xml"

        renderer: Renderer[CompleteEmbeds] = Renderer(Formatter(), template)
        message = renderer.render("multi_line_content_test")
        assert isinstance(message, Message), "Expected Message instance"
        content = message.content
        assert content is not None
        message_lines = content.strip().split("\n")
        self.assertEqual(len(message_lines), 3)
        self.assertEqual(message_lines[0], "- This is a test message")
        self.assertEqual(message_lines[1], "- This is a test message")
        self.assertEqual(message_lines[2], "    - This is a test message")
