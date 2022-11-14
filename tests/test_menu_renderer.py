import unittest

from qalib import MenuRenderer


class MenuRendererTest(unittest.TestCase):

    def test_render(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        embed = renderer.render("test_key1")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        embed = renderer.render("test_key2")
        self.assertEqual(embed.title, "Hello Planet")

    def test_menu_key_not_exist(self):
        path = "tests/routes/menus.xml"
        self.assertRaises(KeyError, MenuRenderer, path, "not_a_key")

    def test_pages(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        self.assertEqual(renderer.number_of_pages, 2)

    def test_keys(self):
        path = "tests/routes/menus.xml"
        renderer = MenuRenderer(path, "Menu1")
        self.assertEqual(renderer.keys, ["test_key1", "test_key2"])
