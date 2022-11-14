import datetime
import unittest

import qalib.renderers.embed_renderer


class TestRenderer(unittest.TestCase):
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
