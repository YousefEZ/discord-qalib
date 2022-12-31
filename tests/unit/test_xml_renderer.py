import datetime
import unittest

import discord.ui
from jinja2 import FileSystemLoader, Environment

import qalib.renderers.embed_proxy
import qalib.renderers.jinja_proxy
from .mocked_classes import MockedView

discord.ui.View = MockedView


class TestXMLRenderer(unittest.TestCase):
    """Tests the XML Renderer"""

    def test_render(self):
        path = "tests/routes/simple_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        embed = renderer.render_embed("Launch")
        self.assertEqual(embed.title, "Hello World")

    def test_full_render(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        embed = renderer.render_embed("test_key", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(embed.title, "Test")

    def test_key_not_exist(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        self.assertRaises(KeyError, renderer.render, "not_a_key")

    def test_button_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("test_key2", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 5)

    def test_select_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 2)
        child = view.children[0]
        assert isinstance(child, discord.ui.Select)
        self.assertEqual(child.placeholder, "Select a date")

    def test_channel_select_rendering(self):
        path = "tests/routes/full_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("test_key3", keywords={"todays_date": datetime.datetime.now()})
        self.assertEqual(len(view.children), 2)
        child = view.children[1]
        assert isinstance(child, discord.ui.ChannelSelect)
        self.assertEqual(child.placeholder, "Select a channel")

    def test_role_select_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[0]
        assert isinstance(child, discord.ui.RoleSelect)
        self.assertEqual(child.placeholder, "Select a Role")

    def test_user_select_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[1]
        assert isinstance(child, discord.ui.UserSelect)
        self.assertEqual(child.placeholder, "Select a User")

    def test_mentionable_select_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[2]
        assert isinstance(child, discord.ui.MentionableSelect)
        self.assertEqual(child.placeholder, "Select a Mention")

    def test_text_input_rendering(self):
        path = "tests/routes/select_embeds.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        view = renderer.render_view("Launch")
        self.assertEqual(len(view.children), 4)
        child = view.children[3]
        assert isinstance(child, discord.ui.TextInput)
        self.assertEqual(child.placeholder, "Test Placeholder")

    def test_emoji_error(self):
        path = "tests/routes/error.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        self.assertRaises(ValueError, renderer.render_view, "test1")

    def test_element_error(self):
        path = "tests/routes/error.xml"
        renderer = qalib.renderers.embed_proxy.EmbedProxy(path)
        self.assertRaises(KeyError, renderer.render_view, "test2")

    def test_jinja_renderer(self):
        template = "jinja-test.xml"
        file_loader = FileSystemLoader("tests/routes/")
        env = Environment(loader=file_loader)
        renderer = qalib.renderers.jinja_proxy.JinjaProxy(env, template)
        embed = renderer.render_embed("test1")
        self.assertEqual(len(embed.fields), 3)

    def test_jinja_view_rendering(self):
        template = "jinja-test.xml"
        file_loader = FileSystemLoader("tests/routes/")
        env = Environment(loader=file_loader)
        renderer = qalib.renderers.jinja_proxy.JinjaProxy(env, template)
        view = renderer.render_view("test1")
        self.assertEqual(len(view.children), 1)

    def test_combined_rendering(self):
        template = "jinja-test.xml"
        file_loader = FileSystemLoader("tests/routes/")
        env = Environment(loader=file_loader)
        renderer = qalib.renderers.jinja_proxy.JinjaProxy(env, template)
        embed, view = renderer.render("test1")
        self.assertEqual(len(embed.fields), 3)
        self.assertEqual(len(view.children), 1)

    def test_jinja_size(self):
        template = "jinja-test.xml"
        file_loader = FileSystemLoader("tests/routes/")
        env = Environment(loader=file_loader)
        renderer = qalib.renderers.jinja_proxy.JinjaProxy(env, template)
        self.assertEqual(renderer.template().size, 2)

    def test_jinja_keys(self):
        template = "jinja-test.xml"
        file_loader = FileSystemLoader("tests/routes/")
        env = Environment(loader=file_loader)
        renderer = qalib.renderers.jinja_proxy.JinjaProxy(env, template)
        self.assertEqual(renderer.template().keys, ["test1", "test2"])

    def test_jinja_empty_view(self):
        template = "jinja-test.xml"
        file_loader = FileSystemLoader("tests/routes/")
        env = Environment(loader=file_loader)
        renderer = qalib.renderers.jinja_proxy.JinjaProxy(env, template)
        view = renderer.render_view("test2")
        self.assertIs(view, None)
