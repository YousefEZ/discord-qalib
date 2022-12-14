from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Optional, List, Dict, Any, cast, Type
from xml.etree import ElementTree as ElementTree

import discord
import discord.types.embed
import discord.ui as ui

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, Display
from qalib.translators.deserializer import Deserializer
from qalib.translators.parser import Parser
from qalib.translators.utils import *


class XMLParser(Parser):

    def __init__(self, source: str):
        """Initialisation of the XML Parser

        Args:
            source (str): the text of the XML file
        """
        self.root = ElementTree.fromstring(source)

    def get_embed(self, identifier: str) -> str:
        """This method is used to get an embed by its key.

        Args:
            identifier (str): key of the embed

        Returns (str): a raw string containing the embed.
        """
        for embed in self.root.findall("embed"):
            if embed.get("key") == identifier:
                return ElementTree.tostring(embed, encoding='unicode', method='xml')
        raise KeyError(f"Embed with key {identifier} not found")

    def get_menu(self, identifier: str) -> str:
        """This method is used to get a menu by its key.

        Args:
            identifier (str): key of the menu

        Returns (str): a raw string containing the menu.
        """
        for menu in self.root.findall("menu"):
            if menu.get("key") == identifier:
                return ElementTree.tostring(menu, encoding='unicode', method='xml')
        raise KeyError(f"Menu with key {identifier} not found")

    def get_modal(self, identifier: str) -> str:
        """This method is used to get a modal by its key.

        Args:
            identifier (str): key of the modal

        Returns (str): a raw string containing the modal.
        """
        for modal in self.root.findall("modal"):
            if modal.get("key") == identifier:
                return ElementTree.tostring(modal, encoding='unicode', method='xml')
        raise KeyError(f"Modal with key {identifier} not found")

    def template_embed(self, key: str, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template an embed, by identifying it by its key and using the template engine to
        template it.

        Args:
            key (str): key of the embed
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed
        """
        return template_engine.template(self.get_embed(key), keywords)

    def template_menu(self, key: str, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template a menu, by identifying it by its key and using the template engine to
        template it.

        Args:
            key (str): key of the menu
            template_engine (TemplateEngine): template engine that is used to template the menu
            keywords (Dict[str, Any]): keywords that are used to template the menu

        Returns (str): templated menu
        """
        return template_engine.template(self.get_menu(key), keywords)

    def template_modal(self, key: str, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template a modal, by identifying it by its key and using the template engine to
        template it.

        Args:
            key (str): key of the modal
            template_engine (TemplateEngine): template engine that is used to template the modal
            keywords (Dict[str, Any]): keywords that are used to template the modal

        Returns (str): templated modal
        """
        return template_engine.template(self.get_modal(key), keywords)


class XMLDeserializer(Deserializer):
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    def deserialize(self, source: str, callables: Dict[str, Callback], **kw) -> Display:
        """Deserializes an embed from an XML file, and returns it as a Display object.

        Args:
            source (str): templated document contents to deserialize.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            **kw (Dict[str, Any]): A dictionary containing the keyword arguments to use for the view.

        Returns (Display): A display object containing the embed and its view.
        """
        return self.deserialize_to_embed(ElementTree.fromstring(source), callables, kw)

    def deserialize_to_embed(
            self,
            embed_tree: ElementTree.Element,
            callables: Dict[str, Callback],
            kw: Dict[str, Any]
    ) -> Display:
        """Deserializes an embed from an ElementTree.Element, and returns it as a Display object.

        Args:
            embed_tree (ElementTree.Element): The element to deserialize the embed from.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            kw (Dict[str, Any]): A dictionary containing the keyword arguments to use for the view.

        Returns (Display): A display object containing the embed and its view.
        """
        view_tree: ElementTree.Element = embed_tree.find("view")
        embed = self.render(embed_tree)
        view = ui.View(**kw) if view_tree is None else self._render_view(view_tree, callables, kw)
        return Display(embed, view)

    def deserialize_into_menu(self, source: str, callables: Dict[str, Callback], **kw) -> List[Display]:
        """Deserializes a menu from an XML file, by generating a list of displays that are connected by buttons in their
        views to navigate between them.

        Args:
            source (str): The XML file to deserialize.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            **kw (Dict[str, Any]): A dictionary containing the keyword arguments to use for the views.

        Returns (List[Display]): List of displays that are connected by buttons in their views to navigate between them.
        """
        menu_tree: ElementTree = ElementTree.fromstring(source)
        return [self.deserialize_to_embed(embed, callables, kw) for embed in menu_tree.findall("embed")]

    def deserialize_into_modal(self, source: str, methods: Dict[str, Callback], **kw: Any) -> discord.ui.Modal:
        """Method to deserialize a modal into a discord.ui.Modal object

        Args:
            source (str): The source text to deserialize into a modal
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            **kw (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        modal_tree = ElementTree.fromstring(source)
        return self._render_modal(modal_tree, methods, kw)

    def _render_modal(
            self,
            tree: ElementTree.Element,
            methods: Dict[str, Callback],
            kw: Any
    ) -> discord.ui.Modal:
        """Method to render a modal from a modal tree

        Args:
            tree (Dict[str, Any]): The modal tree to render
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kw (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        title = self._render_attribute(tree, "title")
        modal = type(f"{title} Modal", (discord.ui.Modal,), dict(**methods, **kw))(title=title)

        for component in self.render_components(tree):
            modal.add_item(component)

        return modal

    def _render_view(
            self,
            raw_view: ElementTree.Element,
            callables: Dict[str, Callback],
            kw: Dict[str, Any]
    ) -> ui.View:
        """Renders a view from an ElementTree.Element.

        Args:
            raw_view (ElementTree.Element): The element to render the view from.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            kw (Dict[str, Any]): A dictionary containing the keyword arguments to use for the view.

        Returns (ui.View): A view object containing the components.
        """
        view = ui.View(**kw)
        for component in self.render_components(raw_view, callables):
            view.add_item(component)
        return view

    @staticmethod
    def _render_element(element: ElementTree.Element) -> str:
        """Renders the given ElementTree.Element by returning its text.

        Args:
            element (ElementTree.Element): The element to render.

        Returns (str): The rendered element.
        """
        return "" if element is None else element.text

    @staticmethod
    def _render_attribute(element: ElementTree.Element, attribute: str) -> str:
        """Renders an attribute from an ElementTree.Element.

        Args:
            element (ElementTree.Element): The element to render the attribute from.
            attribute (str): The name of the attribute to render.

        Returns (str): The value of the attribute.
        """
        return "" if (value := element.get(attribute)) is None else value

    def _render_timestamp(self, timestamp_element: ElementTree.Element) -> Optional[datetime]:
        """Renders the timestamp from an ElementTree.Element. Element may contain an attribute "format" which will be
        used to parse the timestamp.

        Args:
            timestamp_element (ElementTree.Element): The element to render the timestamp from.

        Returns (Optional[datetime]): A datetime object containing the timestamp.
        """
        if timestamp_element is not None:
            timestamp = self._render_element(timestamp_element)
            date_format = self._render_attribute(timestamp_element, "format")
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(timestamp, date_format) if timestamp != "" else None

    def _render_author(self, author_element: ElementTree.Element) -> Optional[dict]:
        """Renders the author from an ElementTree.Element.

        Args:
            author_element (ElementTree.Element): The element to render the author information from.

        Returns (Optional[dict]): A dictionary containing the raw author.
        """
        return {
            "name": self._render_element(author_element.find("name")),
            "url": self._render_element(author_element.find("url")),
            "icon_url": self._render_element(author_element.find("icon"))
        }

    def _render_footer(self, footer_element: ElementTree.Element) -> Optional[dict]:
        """Renders the footer from an ElementTree.Element.

        Args:
            footer_element (ElementTree.Element): The element to render the footer from.

        Returns (Optional[dict]): A dictionary containing the raw footer.
        """
        return {
            "text": self._render_element(footer_element.find("text")),
            "icon_url": self._render_element(footer_element.find("icon"))
        }

    def _render_fields(self, fields_element: ElementTree.Element) -> List[dict]:
        """Renders the fields from an ElementTree.Element.

        Args:
            fields_element (ElementTree.Element): The element to render the fields from.

        Returns (List[dict]): A list of dictionaries containing the raw fields.
        """
        return [{"name": self._render_element(field.find("name")),
                 "value": self._render_element(field.find("value")),
                 "inline": self._render_attribute(field, "inline").lower() == "true"}
                for field in fields_element.findall("field")]

    def _pop_component(self, component: ElementTree.Element, key: str) -> Optional[ElementTree.Element]:
        """Pops a component from the given element, and returns it.

        Args:
            component (ElementTree.Element): The element to pop the component from.
            key (str): The key of the component to pop.

        Returns (Optional[ElementTree.Element]): The popped component, or None if it doesn't exist.
        """
        if (child_component := component.find(key)) is not None:
            component.remove(child_component)
        return child_component

    def _render_emoji(self, emoji_element: Optional[ElementTree.Element]) -> Optional[Dict[str, str]]:
        """Renders an ElementTree.Element into a dictionary.

        Args:
            emoji_element (Optional[ElementTree.Element]): The element to render into a Dictionary of emoji data

        Returns (Optional[Dict[str, str]]): The rendered emoji, or None if the element is None.
        """
        if emoji_element is None:
            return

        emoji = {}
        if (name := emoji_element.find("name")) is not None:
            emoji["name"] = self._render_element(name)
        if (identifier := emoji_element.find("id")) is not None:
            emoji["id"] = self._render_element(identifier)
        if (animated := emoji_element.find("animated")) is not None:
            emoji["animated"] = self._render_element(animated) == "True"
        return (None, emoji)[len(emoji) > 0]

    def _extract_elements(self, tree: ElementTree.Element) -> Dict[str, Any]:
        """Extracts the elements from the given ElementTree.Element, and returns them as a dictionary.

        Args:
            tree (ElementTree.Element): The element to extract the elements from.

        Returns (Dict[str, Any]): A dictionary containing the extracted elements.
        """
        return {element.tag: self._render_element(element) for element in tree}

    def _render_button(self, component: ElementTree.Element, callback: Optional[Callback]) -> ui.Button:
        """Renders a button based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The button to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this button.

        Returns (ui.Button): The rendered button.
        """
        emoji_component = self._pop_component(component, "emoji")
        attributes = self._extract_elements(component)
        attributes["emoji"] = make_emoji(self._render_emoji(emoji_component))

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def _render_options(self, raw_options: Optional[ElementTree.Element]) -> List[discord.SelectOption]:
        """Renders a list of options based on the template in the element, and formatted values given by the keywords.

        Args:
            raw_options (ElementTree.Element): The options to render, contains the template.

        Returns (List[discord.SelectOption]): The rendered options.
        """
        options = []
        for option in (raw_options or []):
            emoji_component = self._pop_component(option, "emoji")
            option_attributes = self._extract_elements(option)
            option_attributes["emoji"] = make_emoji(self._render_emoji(emoji_component))
            options.append(discord.SelectOption(**option_attributes))
        return options

    def _render_select(
            self,
            component: ElementTree.Element,
            callback: Optional[Callback],
    ) -> ui.Select:
        """Renders a select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The select to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this select.

        Returns (ui.Select): The rendered select.
        """
        options = self._render_options(self._pop_component(component, "options"))

        attributes = self._extract_elements(component)
        attributes["options"] = options

        select: ui.Select = create_select(**attributes)
        select.callback = callback
        return select

    def _render_channel_select(self, component: ElementTree.Element, callback: Optional[Callback]) -> ui.ChannelSelect:
        """Renders a channel select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The channel select to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this channel select.

        Returns (ui.ChannelSelect): The rendered channel select.
        """
        channel_types: ElementTree.Element = self._pop_component(component, "channel_types")

        attributes = self._extract_elements(component)
        if channel_types is not None:
            attributes["channel_types"] = make_channel_types(list(map(
                lambda element: self._render_element(element),
                channel_types.findall("channel_type")
            )))

        select: ui.ChannelSelect = create_channel_select(**attributes)
        select.callback = callback
        return select

    def _render_type_select(
            self,
            select_type: Type[T],
            component: ElementTree.Element,
            callback: Optional[Callback],
    ) -> T:
        """Renders a type select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The type select to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this role select.

        Returns (ui.RoleSelect): The rendered role select.
        """
        attributes = self._extract_elements(component)

        select: ui.RoleSelect = create_type_select(select_type, **attributes)
        select.callback = callback
        return select

    def _render_text_input(self, component: ElementTree.Element, callback: (Optional[Callback])) -> ui.TextInput:
        """Renders a text input based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The text input to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this text input.

        Returns (ui.TextInput): The rendered text input.
        """
        attributes = self._extract_elements(component)

        text_input: ui.TextInput = create_text_input(**attributes)
        text_input.callback = callback
        return text_input

    def render_component(self, component: ElementTree.Element, callback: Optional[Callback]) -> ui.Item:
        """Renders a component based on the tag in the element.

        Args:
            component (ElementTree.Element): The component to render, contains all template.
            callback (Optional[Callback]): The callback to use if the user interacts with this component.

        Returns (discord.ui.Item): The rendered component.
        """

        return {
            "button": self._render_button,
            "select": self._render_select,
            "channel_select": self._render_channel_select,
            "text_input": self._render_text_input,
            "role_select": partial(self._render_type_select, ui.RoleSelect),
            "mentionable_select": partial(self._render_type_select, ui.MentionableSelect),
            "user_select": partial(self._render_type_select, ui.UserSelect),
        }[component.tag](component, callback)

    def render_components(
            self,
            view: ElementTree.Element,
            callables: Optional[Dict[str, Callback]] = None
    ) -> List[ui.Item]:
        """Renders a list of components based on the identifier given.

        Args:
            view (ui.View): The raw view.
            callables (Dict[str, Callback]): The callbacks to use if the user interacts with the components.

        Returns (Optional[List[discord.ui.Item]]): The rendered components.
        """
        if callables is None:
            callables = {}

        return [
            self.render_component(
                component,
                callables.get(self._render_attribute(component, "key"), ui.Item.callback),
            )
            for component in view
        ]

    def render(self, raw_embed: ElementTree.Element) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance.

        Args:
           raw_embed(ElementTree.Element): The element to render the embed from.

        Returns:
            Embed: Embed Object, discord compatible.
        """

        def render(name: str):
            return self._render_element(raw_embed.find(name))

        embed_type: discord.types.embed.EmbedType = "rich"
        if cast(discord.types.embed.EmbedType, given_type := render("type")) != "":
            embed_type = cast(discord.types.embed.EmbedType, given_type)

        embed = discord.Embed(
            title=render("title"),
            colour=make_colour(render("colour")),
            type=embed_type,
            url=render("url"),
            description=render("description"),
            timestamp=self._render_timestamp(raw_embed.find("timestamp"))
        )

        for field in self._render_fields(raw_embed.find("fields")):
            embed.add_field(**field)

        if (footer := raw_embed.find("footer")) is not None:
            embed.set_footer(**self._render_footer(footer))

        embed.set_thumbnail(url=self._render_element(raw_embed.find("thumbnail")))
        embed.set_image(url=self._render_element(raw_embed.find("image")))

        if (author := raw_embed.find("author")) is not None:
            embed.set_author(**self._render_author(author))

        return embed
