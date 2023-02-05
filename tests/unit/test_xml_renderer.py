import datetime
import unittest

import discord.ui

import qalib
import qalib.translators
from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter
from qalib.template_engines.jinja2 import Jinja2
from .mocked_classes import MockedView

discord.ui.View = MockedView


class TestXMLRenderer(unittest.TestCase):
    """Tests the XML Renderer"""

    def test_render(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = Renderer(Formatter(), path)
        embed, = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        embed, = renderer.render("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 5)

    def test_select_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 2)
        child = view.children[0]
        assert isinstance(child, discord.ui.Select)
        self.assertEqual(child.placeholder, "Select a date")

    def test_channel_select_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 2)
        child = view.children[1]
        assert isinstance(child, discord.ui.ChannelSelect)
        self.assertEqual(child.placeholder, "Select a channel")

    def test_role_select_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[0]
        assert isinstance(child, discord.ui.RoleSelect)
        self.assertEqual(child.placeholder, "Select a Role")

    def test_user_select_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[1]
        assert isinstance(child, discord.ui.UserSelect)
        self.assertEqual(child.placeholder, "Select a User")

    def test_mentionable_select_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[2]
        assert isinstance(child, discord.ui.MentionableSelect)
        self.assertEqual(child.placeholder, "Select a Mention")

    def test_text_input_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[3]
        assert isinstance(child, discord.ui.TextInput)
        self.assertEqual(child.placeholder, "Test Placeholder")

    def test_emoji_error(self):
        path = "tests/routes/error.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(ValueError, renderer.render, "test1")

    def test_element_error(self):
        path = "tests/routes/error.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "test2")

    def test_missing_embed_key(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "missing_key")

    def test_missing_menu_key(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render_menu, "missing_menu_key")

    def test_jinja_renderer(self):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        embed, _ = renderer.render("test1")
        self.assertEqual(len(embed.fields), 3)

    def test_jinja_view_rendering(self):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        _, view = renderer.render("test1")
        self.assertEqual(len(view.children), 1)

    def test_combined_rendering(self):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        embed, view = renderer.render("test1")
        self.assertEqual(len(embed.fields), 3)
        self.assertEqual(len(view.children), 1)

    def test_jinja_empty_view(self):
        template = "tests/routes/jinja-test.xml"

        renderer = Renderer(Jinja2(), template)
        message = renderer.render("test2")
        self.assertIs(message.view, qalib.translators.MISSING)

    def test_content_rendering(self):
        template = "tests/routes/complete_messages.xml"

        renderer = Renderer(Formatter(), template)
        content, _ = renderer.render("content_test")
        self.assertEqual(content, "This is a test message")
