import datetime
import unittest

import discord.ui

from qalib.renderer import Renderer
from qalib.template_engines.formatter import Formatter


class TestJSONRenderer(unittest.TestCase):
    """Tests the JSON Renderer"""

    def test_render(self):
        path = "tests/routes/simple_embeds.json"
        renderer = Renderer(Formatter(), path)
        embed, = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.json"
        renderer = Renderer(Formatter(), path)
        embed, = renderer.render("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.json"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self):
        path = "tests/routes/full_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 5)

    def test_select_rendering(self):
        path = "tests/routes/full_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(len(view.children), 0)
        child = view.children[0]
        assert isinstance(child, discord.ui.Select)
        self.assertEqual(child.placeholder, "Select a date")

    def test_channel_select_rendering(self):
        path = "tests/routes/full_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(len(view.children), 0)
        child = view.children[1]
        assert isinstance(child, discord.ui.ChannelSelect)
        self.assertEqual(child.placeholder, "Select a channel")

    def test_role_select_rendering(self):
        path = "tests/routes/select_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertGreater(len(view.children), 0)
        child = view.children[0]
        assert isinstance(child, discord.ui.RoleSelect)
        self.assertEqual(child.placeholder, "Select a Role")

    def test_user_select_rendering(self):
        path = "tests/routes/select_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertGreater(len(view.children), 0)
        child = view.children[1]
        assert isinstance(child, discord.ui.UserSelect)
        self.assertEqual(child.placeholder, "Select a User")

    def test_mentionable_select_rendering(self):
        path = "tests/routes/select_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertGreater(len(view.children), 0)
        child = view.children[2]
        assert isinstance(child, discord.ui.MentionableSelect)
        self.assertEqual(child.placeholder, "Select a Mention")

    def test_text_input_rendering(self):
        path = "tests/routes/select_embeds.json"
        renderer = Renderer(Formatter(), path)
        _, view = renderer.render("Launch")
        self.assertGreater(len(view.children), 0)
        child = view.children[3]
        assert isinstance(child, discord.ui.TextInput)
        self.assertEqual(child.placeholder, "Test Placeholder")

    def test_emoji_error(self):
        path = "tests/routes/error.json"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(ValueError, renderer.render, "test1")

    def test_element_error(self):
        path = "tests/routes/error.json"
        renderer = Renderer(Formatter(), path)
        self.assertRaises(KeyError, renderer.render, "test2")

    def test_content_rendering(self):
        path = "tests/routes/complete_messages.json"
        renderer = Renderer(Formatter(), path)
        content, _ = renderer.render("content_test")
        self.assertEqual(content, "This is a test message")

    def test_tts_rendering(self):
        template = "tests/routes/complete_messages.json"

        renderer = Renderer(Formatter(), template)
        _, tts = renderer.render("tts_test")
        self.assertTrue(tts)