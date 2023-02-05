from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from functools import partial
from typing import Dict, List, Optional, Any, Union, cast, Type

import discord
import discord.types.embed
import discord.ui as ui

from qalib.translators import Callback, Message, MISSING
from qalib.translators.deserializer import Deserializer
from qalib.translators.parser import Parser
from qalib.translators.utils import *
from qalib.template_engines.template_engine import TemplateEngine


class JSONParser(Parser):
    """This method is used to parse the document into a menu and a list of callables for .json files"""

    __slots__ = ("_data",)

    def __init__(self, source: str):
        """This method is used to initialize the parser by parsing the source text.

        Args:
            source (str): source text that is parsed
        """
        self._data = json.loads(source)

    def recursive_template(self, obj: Any, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> Dict[str, Any]:
        """Method that is used to recursively template the object using the templater and the keywords.

        Args:
            obj (Any): object that is templated
            template_engine (TemplateEngine): template engine that is used to template the object
            keywords (Dict[str, Any]): keywords that are used to template the object

        Returns (Dict[str, Any]): templated object
        """
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = self.recursive_template(obj[key], template_engine, keywords)
        elif isinstance(obj, list):
            for i in range(len(obj)):
                obj[i] = self.recursive_template(obj[i], template_engine, keywords)
        elif isinstance(obj, str):
            obj = template_engine.template(obj, keywords)

        return obj

    def template_message(self, key: str, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template the embed by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (str): key of the embed
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed in the form of string.
        """
        return json.dumps(self.recursive_template(deepcopy(self._data[key]), template_engine, keywords))

    def template_menu(self, key: str, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """Method that is used to template the menu by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (str): key of the menu
            template_engine (TemplateEngine): template engine that is used to template the menu
            keywords (Dict[str, Any]): keywords that are used to template the menu

        Returns (str): templated menu in the form of string.
        """
        return json.dumps(self.recursive_template(deepcopy(self._data[key]), template_engine, keywords))

    def template_modal(self, key: str, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """Method that is used to template the modal by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (str): key of the modal
            template_engine (TemplateEngine): template engine that is used to template the modal
            keywords (Dict[str, Any]): keywords that are used to template the modal

        Returns (str): templated modal in the form of string.
        """
        return json.dumps(self.recursive_template(deepcopy(self._data[key]), template_engine, keywords))


class JSONDeserializer(Deserializer):

    def deserialize_into_message(self, source: str, callables: Dict[str, Callback], **kw) -> Message:
        """Method to deserialize a source into a Display object

        Args:
            source (str): The source text to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            **kw: Additional keyword arguments

        Returns (Display): A Display object
        """
        return self.deserialize_message(json.loads(source), callables, kw)

    def deserialize_message(
            self,
            message_tree: Dict[str, Any],
            callables: Dict[str, Callback],
            kw: Dict[str, Any]
    ) -> Message:
        """Method to deserialize an embed into a Display NamedTuple containing the embed and the view

        Args:
            message_tree (Dict[str, Any]): The embed to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kw (Dict[str, Any]): A dictionary containing the attributes to use for the view

        Returns (Display): A Display NamedTuple containing the embed and the view
        """
        view_tree = message_tree.get("view")
        embed = self.render(embed_tree) if (embed_tree := message_tree.get("embed")) is not None else MISSING
        view = MISSING if view_tree is None else self._render_view(view_tree, callables, kw)
        return Message(
            embed=embed,
            content=message_tree.get("content", MISSING),
            tts=MISSING if (tts_element := message_tree.get("tts")) is None else (
                        type(tts_element) == bool or tts_element.lower() == "true"),
            view=view
        )

    def deserialize_into_menu(self, source: str, callables: Dict[str, Callback], **kw) -> List[Message]:
        """Method to deserialize a menu into a list of Display objects

        Args:
            source (str): The source text to deserialize int a Menu
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            **kw (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (List[Display]): A list of Display objects
        """
        return [self.deserialize_message(embed, callables, kw) for embed in json.loads(source).values()]

    def deserialize_into_modal(self, source: str, methods: Dict[str, Callback], **kw: Any) -> discord.ui.Modal:
        """Method to deserialize a modal into a discord.ui.Modal object

        Args:
            source (str): The source text to deserialize into a modal
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            **kw (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        modal_tree = json.loads(source)
        return self._render_modal(modal_tree, methods, kw)

    def _render_modal(self, tree: Dict[str, Any], methods: Dict[str, Callback], kw: Dict[str, Any]) -> discord.ui.Modal:
        """Method to render a modal from a modal tree

        Args:
            tree (Dict[str, Any]): The modal tree to render
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kw (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        title = self._render_attribute(tree, "title")
        modal = type(f"{title} Modal", (discord.ui.Modal,), dict(**methods))(title=title, **kw)

        for component in self.render_components(tree.get("components"), {}):
            modal.add_item(component)

        return modal

    def _render_view(
            self,
            raw_view: Dict[str, ...],
            callables: Dict[str, Callback],
            kw: Dict[str, Any]
    ) -> ui.View:
        """Method to render a view element into a discord.ui.View object

        Args:
            raw_view (Dict[str, ...]): The view element to render
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kw (Dict[str, Any]): A dictionary containing the attributes to use for the view

        Returns (ui.View): A discord.ui.View object
        """
        view = ui.View(**kw)
        for component in self.render_components(raw_view, callables):
            view.add_item(component)
        return view

    def _render_attribute(self, element: Dict[str, str], attribute) -> str:
        """Render an attribute of an element

        Args:
            element (Dict[str, str]): The element to render the attribute from
            attribute (str): The attribute to render

        Returns (str): The attribute that is extracted from the element.
        """
        return "" if (value := element.get(attribute)) is None else value

    def _render_timestamp(self, timestamp: Optional[Dict[str, str]]) -> Optional[datetime]:
        """Method to render a timestamp element into a datetime object

        Args:
            timestamp (Optional[Dict[str, str]]): The timestamp element to render

        Returns (Optional[datetime]): A datetime object
        """
        if timestamp is None:
            return None

        date = self._render_attribute(timestamp, "timestamp")
        date_format = self._render_attribute(timestamp, "format")
        if date_format == "":
            date_format = "%Y-%m-%d %H:%M:%S.%f"
        return datetime.strptime(date, date_format) if date != "" else None

    def _render_author(self, author: Dict[str, str]) -> Optional[dict]:
        """Method to render an author element into a dictionary containing the author attributes

        Args:
            author (Dict[str, str]): The author element to render

        Returns (Optional[dict]): A dictionary containing the author attributes
        """
        return {
            "name": self._render_attribute(author, "name"),
            "url": self._render_attribute(author, "url"),
            "icon_url": self._render_attribute(author, "icon")
        }

    def _render_footer(self, footer: Dict[str, str]) -> Optional[dict]:
        """Method to render a footer element into a dictionary containing the footer attributes

        Args:
            footer (Dict[str, str]): The footer element to render

        Returns (Optional[dict]): A dictionary containing the footer attributes
        """
        return {
            "text": self._render_attribute(footer, "text"),
            "icon_url": self._render_attribute(footer, "icon")
        }

    def _render_fields(self, fields: List[Dict[str, str]]) -> List[dict]:
        """Method that renders a list of fields into a list of dictionaries containing the field attributes

        Args:
            fields (List[Dict[str, str]]): The list of fields to render

        Returns (List[dict]): A list of dictionaries containing the field attributes
        """
        return [{
            "name": self._render_attribute(field, "name"),
            "value": self._render_attribute(field, "text"),
            "inline": (attr := self._render_attribute(field, "inline")) or attr.lower() == "true"}
            for field in fields
        ]

    def _render_emoji(self, emoji_element: Dict[str, str]) -> Optional[Dict[str, str]]:
        """Method to render an emoji element into a dictionary containing the emoji attributes

        Args:
            emoji_element (Dict[str, str]): The emoji element to render

        Returns (Optional[Dict[str, str]]): A dictionary containing the emoji attributes
        """
        emoji = {}
        if "name" in emoji_element:
            emoji["name"] = self._render_attribute(emoji_element, "name")
        if "id" in emoji_element:
            emoji["id"] = self._render_attribute(emoji_element, "id")
        if "animated" in emoji_element:
            animated = self._render_attribute(emoji_element, "animated")
            emoji["animated"] = animated if type(animated) == bool else animated.lower() == "true"
        return (None, emoji)[len(emoji) > 0]

    def _extract_attributes(self, element: Dict[str, Any]) -> Dict[str, Union[str, Dict[str, str]]]:
        """Method to extract attributes from a component element and return them as a dictionary

        Args:
            element (Dict[str, Any]): The element to extract attributes from

        Returns (Dict[str, Union[str, Dict[str, str]]]): A dictionary containing the attributes
        """
        return {attribute: self._render_attribute(element, attribute) for attribute in element.keys()}

    def _render_button(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Callback],
    ) -> ui.Button:
        """Renders a button from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called when the button is pressed

        Returns (ui.Item): the rendered button
        """

        emoji = self._render_emoji(component.pop("emoji")) if "emoji" in component else None

        attributes = self._extract_attributes(component)
        if emoji is not None:
            attributes["emoji"] = make_emoji(emoji)

        button: ui.Button = create_button(**attributes)
        button.callback = callback
        return button

    def _render_options(self, raw_options: List[Dict[str, Dict[str, str]]]) -> List[discord.SelectOption]:
        """Renders the options for a select menu

        Args:
            raw_options (List[Dict[str, Union[str, str]]]): the raw options to be rendered

        Returns (List[discord.SelectOption]): the rendered options
        """
        options = []
        for option in raw_options:
            emoji = self._render_emoji(option.pop("emoji")) if "emoji" in option else None
            attributes = self._extract_attributes(option)

            if emoji is not None:
                attributes["emoji"] = make_emoji(emoji)

            options.append(discord.SelectOption(**attributes))
        return options

    def _render_channel_select(
            self,
            component: Dict[str, Union[str, List[str], Dict[str, Any]]],
            callback: Optional[Callback],
    ) -> ui.ChannelSelect:
        """Renders a select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called when the select menu is pressed

        Returns (ui.Item): the rendered channel select menu
        """

        channel_types: List[str] = component.pop("channel_types")

        attributes: Dict[str, Any] = self._extract_attributes(component)
        if channel_types is not None:
            attributes["channel_types"] = make_channel_types(channel_types)

        select: ui.ChannelSelect = create_channel_select(**attributes)
        select.callback = callback
        return select

    def _render_select(
            self,
            component: Dict[str, Union[str, List[Dict[str, ...]], Dict[str, Any]]],
            callback: Optional[Callback],
    ) -> ui.Select:
        """Renders a select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called when the select menu is pressed

        Returns (ui.Item): the rendered select menu
        """

        options = self._render_options(component.pop("options"))
        attributes: Dict[str, Any] = self._extract_attributes(component)
        attributes["options"] = options

        select: ui.Select = create_select(**attributes)
        select.callback = callback
        return select

    def _render_type_select(
            self,
            select_type: Type[T],
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Callback],
    ) -> T:
        """Renders a type select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called it is selected from the select menu

        Returns (ui.Item): the rendered role select menu
        """

        attributes: Dict[str, Any] = self._extract_attributes(component)

        select: T = create_type_select(select_type, **attributes)
        select.callback = callback
        return select

    def _render_text_input(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Callback],
    ) -> ui.TextInput:
        """Renders a text input form the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called when the text is submitted

        Returns (ui.TextInput): the rendered text input block.
        """

        attributes: Dict[str, Any] = self._extract_attributes(component)

        text_input: ui.TextInput = create_text_input(**attributes)
        text_input.callback = callback
        return text_input

    def render_component(
            self,
            component: Dict[str, Union[str, Dict[str, Any]]],
            callback: Optional[Callback],
    ) -> ui.Item:
        """ Renders a component from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called when the user interacts with the component

        Returns (ui.Item): the rendered component
        """
        return {
            "button": self._render_button,
            "select": self._render_select,
            "channel_select": self._render_channel_select,
            "role_select": partial(self._render_type_select, ui.RoleSelect),
            "user_select": partial(self._render_type_select, ui.UserSelect),
            "mentionable_select": partial(self._render_type_select, ui.MentionableSelect),
            "text_input": self._render_text_input
        }[component.pop("type")](component, callback)

    def render_components(
            self,
            view: Dict[str, ...],
            callables: Dict[str, Callback]
    ) -> Optional[List[ui.Item]]:
        """Renders the components specified by the identifier

        Args:
            view (Dict[str, ...]): the dictionary containing the view component.
            callables (Dict[str, Callback]): the callbacks to be called when the user interacts with the components

        Returns (Optional[List[ui.Item]]): the rendered components
        """
        return [self.render_component(component, callables.get(key, ui.Item.callback)) for key, component in
                view.items()]

    def render(self, raw_embed: Dict[str, ...]) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           raw_embed (Dict[str, ...]): the dictionary containing the required key, values needed to render the
                                        embed.

        Returns:
            Embed: Embed Object, discord compatible.
        """

        def render(attribute: str) -> str:
            return self._render_attribute(raw_embed, attribute)

        embed_type: discord.types.embed.EmbedType = "rich"
        if cast(discord.types.embed.EmbedType, given_type := render("type")) != "":
            embed_type = cast(discord.types.embed.EmbedType, given_type)

        embed = discord.Embed(
            title=render("title"),
            colour=make_colour(
                colour if (colour := render("colour")) != "" else render("color")),
            type=embed_type,
            url=render("url"),
            description=render("description"),
            timestamp=self._render_timestamp(raw_embed.get("timestamp"))
        )

        for field in self._render_fields(raw_embed["fields"]):
            embed.add_field(**field)

        if (footer := raw_embed.get("footer")) is not None:
            embed.set_footer(**self._render_footer(footer))

        embed.set_thumbnail(url=self._render_attribute(raw_embed, "thumbnail"))
        embed.set_image(url=self._render_attribute(raw_embed, "image"))

        if (author := raw_embed.get("author")) is not None:
            embed.set_author(**self._render_author(author))

        return embed
