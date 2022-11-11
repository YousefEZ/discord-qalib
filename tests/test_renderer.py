import unittest

import qalib._xml_renderer as xml_renderer

import datetime

class TestRenderer(unittest.TestCase):
    """Tests the XML Renderer"""
    def test_render(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = xml_renderer.Renderer(path)
        embed = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.xml"
        renderer = xml_renderer.Renderer(path)
        embed = renderer.render("test_key", todays_date=datetime.datetime.now())
        self.assertEqual(embed.title, "Test")