import qalib.xml_renderer as xml_renderer

import unittest

class TestRenderer(unittest.TestCase):

    def test_render(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = xml_renderer.Renderer(path)
        embed = renderer.render("Launch")
        self.assertEqual(embed.title, "Hello World")