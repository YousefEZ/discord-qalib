import datetime
import unittest

import discord.ui

import qalib.renderers.embed_renderer


class TestJSONRenderer(unittest.TestCase):
    """Tests the JSON Renderer"""

    def test_render(self):
        path = "tests/routes/simple_embeds.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        embed = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        embed = renderer.render("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self):
        path = "tests/routes/full_embeds.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        view = renderer.render_view("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 5)

    def test_select_rendering(self):
        path = "tests/routes/full_embeds.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        view = renderer.render_view("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(len(view.children), 0)
        child = view.children[0]
        assert isinstance(child, discord.ui.Select)
        self.assertEqual(child.placeholder, "Select a date")

    def test_channel_select_rendering(self):
        path = "tests/routes/full_embeds.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        view = renderer.render_view("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertGreater(len(view.children), 0)
        child = view.children[1]
        assert isinstance(child, discord.ui.ChannelSelect)
        self.assertEqual(child.placeholder, "Select a channel")

    def test_emoji_error(self):
        path = "tests/routes/error.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        self.assertRaises(ValueError, renderer.render_view, "test1")

    def test_element_error(self):
        path = "tests/routes/error.json"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        self.assertRaises(KeyError, renderer.render_view, "test2")
