from __future__ import annotations

import json
from copy import deepcopy
from functools import partial
from typing import List, Union, Dict, Optional, Any, cast, Callable, Type

import discord
from discord import ui
from discord.abc import Snowflake

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, Message, DiscordIdentifier
from qalib.translators.deserializer import Deserializer, K_contra, ReturnType, ElementTypes
from qalib.translators.element.embed import render
from qalib.translators.element.expansive import expand
from qalib.translators.events import EventCallbacks
from qalib.translators.json.components import (
    ComponentTypes,
    Option,
    Button,
    Select,
    CustomSelect,
    ChannelSelect,
    ComponentType,
    Components,
    Timestamp,
    ExpansiveEmbed,
    File,
    AllowedMentions,
    MessageReference,
    View,
    BaseMessage,
    RegularMessage,
    Arrows,
    ExpansiveMessage,
    Page,
    MenuMessage,
    Modal,
    OBJ,
    Elements,
    Document,
)
from qalib.translators.json.embed import JSONEmbedAdapter, JSONExpansiveEmbedAdapter
from qalib.translators.menu import Menu, MenuActions
from qalib.translators.message_parsing import (
    ButtonComponent,
    apply,
    create_button,
    make_emoji,
    make_channel_types,
    create_channel_select,
    create_select,
    CustomSelects,
    create_type_select,
    TextInputComponent,
    create_text_input,
    pipe,
)
from qalib.translators.modal import QalibModal, ModalEvents, ModalEventsCallbacks
from qalib.translators.templater import Templater
from qalib.translators.view import QalibView


class JSONTemplater(Templater):
    """This method is used to parse the document into a menu and a list of callables for .json files"""

    __slots__ = ("_data",)

    def __init__(self, source: str):
        """This method is used to initialize the parser by parsing the source text.

        Args:
            source (str): source text that is parsed
        """
        self._data = json.loads(source)

    def recursive_template(self, obj: OBJ, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> OBJ:
        """Method that is used to recursively template the object using the templater and the keywords.

        Args:
            obj (Dict | List | str | Any): object that is templated
            template_engine (TemplateEngine): template engine that is used to template the object
            keywords (Dict[str, Any]): keywords that are used to template the object

        Returns (Dict[str, Any]): templated object
        """
        if isinstance(obj, dict):
            for key in obj:
                obj[key] = self.recursive_template(obj[key], template_engine, keywords)
        elif isinstance(obj, list):
            for i, value in enumerate(obj):
                obj[i] = self.recursive_template(value, template_engine, keywords)
        elif isinstance(obj, str):
            return cast(OBJ, template_engine.template(obj, keywords))

        return obj

    def template(self, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template the element by first retrieving it using its key, and then templating it
        using the template_engine

        Args:
            template_engine (TemplateEngine): template engine that is used to template the element
            keywords (Dict[str, Any]): keywords that are used to template the element

        Returns (str): templated element in the form of string.
        """
        return json.dumps(self.recursive_template(deepcopy(self._data), template_engine, keywords))


class JSONDeserializer(Deserializer[K_contra]):
    def deserialize(
        self, source: str, key: K_contra, callables: Dict[str, Callback], events: EventCallbacks
    ) -> ReturnType:
        """Method to deserialize a source into a Display object

        Args:
            source (str): The source text to deserialize
            key (K): The key of the element to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.

        Returns (ReturnType): All possible deserialized objects.
        """
        document: Document = json.loads(source)
        element: Elements = document[key]
        return self.deserialize_element(document, element, callables, events)

    def deserialize_element(
        self, document: Document, element: Elements, callables: Dict[str, Callback], events: EventCallbacks
    ) -> ReturnType:
        """Method to deserialize an element into a Display object

        Args:
            document (Document): The document to deserialize
            element (Elements): The element to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.

        Returns (ReturnType): All possible deserialized objects.
        """
        element_type: Optional[ElementTypes] = ElementTypes.from_str(element["type"])

        if element_type == ElementTypes.MESSAGE:
            return self.deserialize_message(cast(Union[RegularMessage, ExpansiveMessage], element), callables, events)
        if element_type == ElementTypes.EXPANSIVE:
            return self.deserialize_expansive_into_menu(cast(ExpansiveMessage, element), callables, events)
        if element_type == ElementTypes.MENU:
            return self.deserialize_menu(cast(MenuMessage, element), callables, events, document=document)
        if element_type == ElementTypes.MODAL:
            return self.deserialize_modal(
                cast(Modal, element), callables, cast(Dict[ModalEvents, ModalEventsCallbacks], events)
            )

        raise TypeError(f"Unrecognized Element Type: {element_type}")

    # pylint: disable= too-many-locals
    def deserialize_message(
        self,
        message_tree: Union[RegularMessage, ExpansiveMessage],
        callables: Dict[str, Callback],
        events: EventCallbacks,
        **overrides: Any,
    ) -> Message:
        """Method to deserialize an embed into a Display NamedTuple containing the embed and the view

        Args:
            message_tree (Dict[str, Any]): The embed to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.
            **overrides (Any): keyword arguments that override the messages

        Returns (Display): A Display NamedTuple containing the embed and the view
        """

        message = Message(
            embed=apply(message_tree.get("embed"), lambda e: render(JSONEmbedAdapter(e))),
            embeds=apply(message_tree.get("embeds"), lambda embeds: [render(JSONEmbedAdapter(e)) for e in embeds]),
            content=message_tree.get("content"),
            tts=message_tree.get("tts"),
            nonce=apply(message_tree.get("nonce"), int),
            delete_after=apply(message_tree.get("delete_after"), float),
            suppress_embeds=message_tree.get("suppress_embeds"),
            file=pipe(cast(Optional[File], message_tree.get("file")), self._render_file),
            files=apply(message_tree.get("files"), lambda files: list(map(self._render_file, files))),
            allowed_mentions=pipe(
                cast(Optional[AllowedMentions], message_tree.get("allowed_mentions")), self._render_allowed_mentions
            ),
            reference=apply(
                message_tree.get("message_reference"),
                lambda reference: discord.MessageReference(
                    message_id=reference["message_id"],
                    channel_id=reference["channel_id"],
                    guild_id=reference.get("guild_id"),
                ),
            ),
            mention_author=message_tree.get("mention_author"),
            view=apply(message_tree.get("view"), self._render_view, callables, events),
            stickers=None,
            ephemeral=message_tree.get("ephemeral"),
            silent=message_tree.get("silent"),
        )

        for key, value in overrides.items():
            setattr(message, key, value)

        return message

    def deserialize_expansive_into_menu(
        self, message_tree: ExpansiveMessage, callbacks: Dict[str, Callback], events: EventCallbacks
    ) -> Menu:
        """Method to deserialize an expansive message into a Menu

        Args:
            message_tree (ExpansiveMessage): The ExpansiveMessage of the message_tree
            callbacks (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.

        Returns (Menu): A Menu object
        """
        pages = self.deserialize_expansive(message_tree, callbacks, events)
        timeout = message_tree.get("timeout", 180.0)
        if "arrows" not in message_tree:
            return Menu(pages, timeout, events=events)

        arrows: Dict[MenuActions, ButtonComponent] = self._deserialize_menu_arrows(message_tree["arrows"])
        return Menu(pages, timeout, arrows, events)

    @staticmethod
    def _deserialize_menu_arrows(arrows: Arrows) -> Dict[MenuActions, ButtonComponent]:
        """Method to deserialize the arrows of a menu

        Args:
            arrows (Arrows): The view of the menu

        Returns (Dict[MenuActions, ButtonComponent]): A dictionary containing the arrows of the menu
        """
        return {
            MenuActions.PREVIOUS: cast(ButtonComponent, arrows["previous"]),
            MenuActions.NEXT: cast(ButtonComponent, arrows["next"]),
        }

    def deserialize_expansive(
        self, message_tree: ExpansiveMessage, callbacks: Dict[str, Callback], events: EventCallbacks
    ) -> List[Message]:
        """Method to deserialize a source into a list of Display objects

        Args:
            message_tree (ExpansiveMessage): The ExpansiveMessage of the message_tree
            callbacks (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.

        Returns (List[Display]): A list of Display objects
        """
        return [
            self.deserialize_message(message_tree, callbacks, events=events, embed=e)
            for e in expand(JSONExpansiveEmbedAdapter(message_tree["embed"], message_tree.get("page_number_key")))
        ]

    def deserialize_page(
        self, document: Document, raw_page: Union[str, Page], callables: Dict[str, Callback], events: EventCallbacks
    ) -> List[Message]:
        """Method to deserialize a page into a Display object

        Args:
            document (Document): the original document containing all the keys.
            raw_page (Page): The page to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.

        Returns (List[Message]): List of pages
        """
        page = document[raw_page] if isinstance(raw_page, str) else raw_page
        element_type = ElementTypes.from_str(page["type"])

        if element_type == ElementTypes.MESSAGE:
            return [self.deserialize_message(cast(Union[RegularMessage, ExpansiveMessage], page), callables, events)]
        if element_type == ElementTypes.EXPANSIVE:
            return self.deserialize_expansive(cast(ExpansiveMessage, page), callables, events)
        raise TypeError(f"Unrecognized Element Type: {element_type}")

    def deserialize_menu(
        self, menu: MenuMessage, callables: Dict[str, Callback], events: EventCallbacks, *, document: Document
    ) -> Menu:
        """Method to deserialize a menu into a list of Display objects

        Args:
            menu (MenuMessage): The Menu Dictionary to deserialize into a List of Messages
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (EventCallbacks): A dictionary containing the event callbacks.
            document (Document): the original document containing all the keys.

        Returns (List[Message]): A list of Display objects
        """
        pages: List[Message] = sum(
            (self.deserialize_page(document, page, callables, events) for page in menu["pages"]), []
        )
        timeout: Optional[float] = menu.get("timeout", 180.0)

        if "arrows" not in menu:
            return Menu(pages, timeout, events=events)

        arrows: Dict[MenuActions, ButtonComponent] = self._deserialize_menu_arrows(menu["arrows"])
        return Menu(pages, timeout, arrows, events)

    def deserialize_modal(
        self, tree: Modal, callables: Dict[str, Callback], events: Dict[ModalEvents, ModalEventsCallbacks]
    ) -> discord.ui.Modal:
        """Method to deserialize a modal into a discord.ui.Modal object

        Args:
            tree (Modal): The Modal Dictionary to deserialize into a discord.ui.Modal object
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            events (Dict[ModalEvents, ModalEventsCallbacks]): A dictionary containing the event callbacks.

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        modal = QalibModal(
            title=tree["title"],
            events=events,
            timeout=tree.get("timeout", 180.0),
            custom_id=tree.get("custom_id", None),
        )

        rendered_components = self.render_components(tree["components"], callables) if "components" in tree else []

        for component in rendered_components:
            modal.add_item(component)

        return modal

    @staticmethod
    def _render_allowed_mentions(
        allowed_mentions: AllowedMentions,
    ) -> discord.AllowedMentions:
        def parse_mentions(mentions: Union[bool, List[int]]) -> Union[bool, List[Snowflake]]:
            if isinstance(mentions, bool):
                return mentions
            return [DiscordIdentifier(int(identifier)) for identifier in mentions]

        return discord.AllowedMentions(
            everyone=allowed_mentions.get("everyone", True),
            users=parse_mentions(allowed_mentions.get("users", True)),
            roles=parse_mentions(allowed_mentions.get("roles", True)),
            replied_user=allowed_mentions.get("replied_user", True),
        )

    @staticmethod
    def _render_file(raw_file: File) -> discord.File:
        """Method to render a file from a file tree

        Args:
            raw_file (Dict[str, Any]): The file tree to render

        Returns (discord.File): A discord.File object
        """
        return discord.File(
            fp=raw_file["filename"],
            description=raw_file["description"] if "description" in raw_file else None,
            spoiler=raw_file["spoiler"] if "spoiler" in raw_file else False,
        )

    def _render_view(self, raw_view: View, callables: Dict[str, Callback], events: EventCallbacks) -> ui.View:
        """Method to render a view element into a discord.ui.View object

        Args:
            raw_view (View) The view element to render
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (ui.View): A discord.ui.View object
        """

        view = QalibView(events)
        if "timeout" in raw_view:
            view.timeout = raw_view["timeout"]
        for component in self.render_components(raw_view["components"], callables):
            view.add_item(component)
        return view

    @staticmethod
    def _render_button(component: Button, callback: Optional[Callback]) -> ui.Button:
        """Renders a button from the given component's template

        Args:
            component (Button): the component's template
            callback (Optional[Callback]): the callback to be called when the button is pressed

        Returns (ui.Item): the rendered button
        """
        button_component: ButtonComponent = cast(ButtonComponent, component.copy())
        if callback is not None:
            button_component["callback"] = callback
        return create_button(button_component)

    @staticmethod
    def _render_options(raw_options: List[Option]) -> List[discord.SelectOption]:
        """Renders the options for a select menu

        Args:
            raw_options (List[Option]): the raw options to be rendered

        Returns (List[discord.SelectOption]): the rendered options
        """

        def parse_option(raw_option: Option) -> discord.SelectOption:
            option: Dict[str, Any] = cast(Dict[str, Any], raw_option.copy())
            if "emoji" in raw_option:
                option["emoji"] = make_emoji(raw_option["emoji"])
            return discord.SelectOption(**option)

        return [parse_option(raw_option) for raw_option in raw_options]

    @staticmethod
    def _render_channel_select(component: ChannelSelect, callback: Optional[Callback]) -> ui.ChannelSelect:
        """Renders a select menu from the given component's template

        Args:
            component (ChannelSelect): the component's template
            callback (Optional[Callback]): the callback to be called when the select menu is pressed

        Returns (ui.Item): the rendered channel select menu
        """

        attributes: Dict[str, Any] = cast(Dict[str, Any], component.copy())
        if "channel_types" in component:
            attributes["channel_types"] = make_channel_types(component["channel_types"])

        select: ui.ChannelSelect = create_channel_select(callback=callback, **attributes)
        return select

    def _render_select(
        self,
        component: Select,
        callback: Optional[Callback],
    ) -> ui.Select:
        """Renders a select menu from the given component's template

        Args:
            component (Dict[str, Union[str, Dict[str, Any]]]): the component's template
            callback (Optional[Callback]): the callback to be called when the select menu is pressed

        Returns (ui.Item): the rendered select menu
        """
        raw_options = component.pop("options")

        assert isinstance(raw_options, list)

        options = self._render_options(raw_options)
        attributes: Dict[str, Any] = cast(Dict[str, Any], component.copy())
        attributes["options"] = options

        select: ui.Select = create_select(callback=callback, **attributes)
        return select

    @staticmethod
    def _render_type_select(
        select_type: Type[CustomSelects], component: CustomSelect, callback: Optional[Callback]
    ) -> CustomSelects:
        """Renders a type select menu from the given component's template

        Args:
            component (component): the component's template
            callback (Optional[Callback]): the callback to be called it is selected from the select menu

        Returns (ui.Item): the rendered role select menu
        """
        return create_type_select(select_type, callback=callback, **component)

    @staticmethod
    def _render_text_input(component: TextInputComponent, callback: Optional[Callback]) -> ui.TextInput:
        """Renders a text input form the given component's template

        Args:
            component (TextInputComponent): the component's template
            callback (Optional[Callback]): the callback to be called when the text is submitted

        Returns (ui.TextInput): the rendered text input block.
        """
        if callback is not None:
            component["callback"] = callback

        text_input: ui.TextInput = create_text_input(component)
        return text_input

    def render_component(
        self,
        component: ComponentType,
        callback: Optional[Callback],
    ) -> ui.Item:
        """Renders a component from the given component's template

        Args:
            component (Components): the component's template
            callback (Optional[Callback]): the callback to be called when the user interacts with the component

        Returns (ui.Item): the rendered component
        """

        component_renderer: Dict[ComponentTypes, Callable[[Any, Optional[Callback]], ui.Item]] = {
            "button": self._render_button,
            "select": self._render_select,
            "channel_select": self._render_channel_select,
            "role_select": partial(self._render_type_select, ui.RoleSelect),
            "user_select": partial(self._render_type_select, ui.UserSelect),
            "mentionable_select": partial(self._render_type_select, ui.MentionableSelect),
            "text_input": self._render_text_input,
        }

        component_type: ComponentTypes = component["type"]
        item_renderer = component_renderer[component_type]

        return item_renderer(component, callback)

    def render_components(self, raw_components: Components, callables: Dict[str, Callback]) -> List[ui.Item]:
        """Renders the components specified by the identifier

        Args:
            raw_components (Components): the dictionary containing the view component.
            callables (Dict[str, Callback]): the callbacks to be called when the user interacts with the components

        Returns (List[ui.Item]): the rendered components
        """
        return [self.render_component(component, callables.get(key)) for key, component in raw_components.items()]
