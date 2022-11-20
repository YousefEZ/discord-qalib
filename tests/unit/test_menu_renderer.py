import unittest

from qalib import MenuRenderer


class MenuRendererTest(unittest.TestCase):

    def test_xml_render(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        embed = renderer.render("test_key1")
        self.assertEqual(embed.title, "Hello World")

    def test_xml_full_render(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        embed = renderer.render("test_key2")
        self.assertEqual(embed.title, "Hello Planet")

    def test_xml_menu_key_not_exist(self):
        path = "tests/routes/menus.xml"
        self.assertRaises(KeyError, MenuRenderer, path, "not_a_key")

    def test_xml_pages(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        self.assertEqual(renderer.size, 2)

    def test_xml_keys(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        self.assertEqual(renderer.keys, ["test_key1", "test_key2"])

    def test_json_render(self):
        path = "tests/routes/menus.json"
        renderer = MenuRenderer(path, "Menu1")
        embed = renderer.render("test_key1")
        self.assertEqual(embed.title, "Hello World")

    def test_json_full_render(self):
        path = "tests/routes/menus.json"
        renderer = MenuRenderer(path, "Menu1")
        embed = renderer.render("test_key2")
        self.assertEqual(embed.title, "Hello Planet")

    def test_json_menu_key_not_exist(self):
        path = "tests/routes/menus.json"
        self.assertRaises(KeyError, MenuRenderer, path, "not_a_key")

    def test_json_pages(self):
        path = "tests/routes/menus.json"
        renderer = MenuRenderer(path, "Menu1")
        self.assertEqual(renderer.size, 2)

    def test_json_keys(self):
        path = "tests/routes/menus.json"
        renderer = MenuRenderer(path, "Menu1")
        self.assertEqual(renderer.keys, ["test_key1", "test_key2"])
