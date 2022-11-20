import unittest

from qalib.renderers.file_renderers._json_renderer import JSONRenderer
from qalib.renderers.file_renderers._xml_renderer import XMLRenderer
from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class TestRendererFactory(unittest.TestCase):

    def test_json_render(self):
        path = "tests/routes/menus.json"
        renderer = RendererFactory.get_renderer(path)
        self.assertTrue(type(renderer) is JSONRenderer)

    def test_xml_render(self):
        path = "tests/routes/menus.xml"
        renderer = RendererFactory.get_renderer(path)
        self.assertTrue(type(renderer) is XMLRenderer)

    def test_no_render(self):
        path = ""
        self.assertRaises(ValueError, RendererFactory.get_renderer, path)
