import datetime
import unittest

import discord.ui

import qalib.renderers.embed_renderer
from .mocked_classes import MockedView

discord.ui.View = MockedView


class TestXMLRenderer(unittest.TestCase):
    """Tests the XML Renderer"""

    def test_render(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        embed = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        embed = renderer.render("test_key", todays_date=datetime.datetime.now())
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        view = renderer.render_view("test_key2", todays_date=datetime.datetime.now())
        self.assertEqual(len(view.children), 5)

    def test_emoji_error(self):
        path = "tests/routes/error.xml"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        self.assertRaises(ValueError, renderer.render_view, "test1")

    def test_element_error(self):
        path = "tests/routes/error.xml"
        renderer = qalib.renderers.embed_renderer.EmbedRenderer(path)
        self.assertRaises(ValueError, renderer.render_view, "test2")
