from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, List, Literal, Optional, Type, TypedDict, TypeVar, Union, cast, Tuple, Sequence

import discord
import discord.types.embed
from discord import ui
from discord.abc import Snowflake
from typing_extensions import NotRequired

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, DiscordIdentifier, Message
from qalib.translators.deserializer import Deserializer, ElementTypes, Types, ReturnType, K_contra
from qalib.translators.message_parsing import (
    ButtonComponent,
    ButtonStyle,
    ChannelType,
    CustomSelects,
    Emoji,
    create_button,
    create_channel_select,
    create_select,
    create_text_input,
    create_type_select,
    make_channel_types,
    make_colour,
    make_emoji,
    Field,
    Footer,
    Author,
    TextInputRaw,
    TextInputComponent,
    make_expansive_embeds, apply, bind_menu, attach_views
)
from qalib.translators.templater import Templater

OBJ = TypeVar("OBJ")

ComponentTypes = Literal[
    "button",
    "select",
    "channel_select",
    "role_select",
    "user_select",
    "mentionable_select",
    "text_input",
]


class Option(TypedDict):
    """This class is used to represent the blueprint of a select menu option."""

    label: str
    value: str
    description: str
    emoji: NotRequired[Emoji]
    default: bool


class Component(TypedDict):
    type: ComponentTypes


class Button(Component):
    """This class is used to represent the blueprint of a button."""

    custom_id: NotRequired[str]
    label: NotRequired[str]
    style: NotRequired[ButtonStyle]
    emoji: NotRequired[Emoji]
    url: NotRequired[str]
    disabled: NotRequired[bool]
    row: NotRequired[int]


class Select(Component):
    """This class is used to represent the blueprint of a select menu."""

    custom_id: NotRequired[str]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    options: NotRequired[List[Option]]
    row: NotRequired[int]


class CustomSelect(Component):
    """This class is used to represent the blueprint of a mentionable select menu."""

    custom_id: NotRequired[str]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    options: NotRequired[List[Option]]
    row: NotRequired[int]


class ChannelSelect(Component):
    """This class is used to represent the blueprint of a channel select menu."""

    custom_id: NotRequired[str]
    channel_types: NotRequired[List[ChannelType]]
    placeholder: NotRequired[str]
    min_values: NotRequired[int]
    max_values: NotRequired[int]
    options: NotRequired[List[Option]]
    row: NotRequired[int]


class TextInput(TextInputRaw):
    type: ComponentTypes


ComponentType = Union[Button, Select, CustomSelect, ChannelSelect, TextInput]
Components = Dict[str, ComponentType]


class Timestamp(TypedDict):
    """This class is used to represent object's timestamp."""

    date: str
    format: NotRequired[str]


class Embed(TypedDict):
    title: str
    colour: NotRequired[str]
    color: NotRequired[str]
    fields: List[Field]
    description: NotRequired[str]
    type: NotRequired[discord.types.embed.EmbedType]
    url: NotRequired[str]
    timestamp: NotRequired[Timestamp]
    footer: NotRequired[Footer]
    image: NotRequired[str]
    thumbnail: NotRequired[str]
    author: NotRequired[Author]


class ExpansiveEmbed(Embed):
    expansive_field: Field


class File(TypedDict):
    """This class is used to represent the blueprint of a file."""

    filename: str
    spoiler: NotRequired[bool]
    description: NotRequired[str]


class AllowedMentions(TypedDict):
    """This class is used to represent the blueprint of allowed mentions."""

    everyone: NotRequired[bool]
    users: NotRequired[Union[bool, List[int]]]
    roles: NotRequired[Union[bool, List[int]]]
    replied_user: NotRequired[bool]


class MessageReference(TypedDict):
    """This class is used to represent the blueprint of a message reference."""

    message_id: int
    channel_id: int
    guild_id: NotRequired[int]


class View(TypedDict):
    timeout: NotRequired[Optional[float]]
    components: Components


class Element(TypedDict):
    type: Types


class BaseMessage(Element):
    view: NotRequired[View]
    timeout: NotRequired[float]
    content: NotRequired[str]
    embeds: NotRequired[List[Embed]]
    tts: NotRequired[bool]
    nonce: NotRequired[int]
    delete_after: NotRequired[float]
    suppress_embeds: NotRequired[bool]
    file: NotRequired[File]
    files: NotRequired[List[File]]
    allowed_mentions: NotRequired[AllowedMentions]
    message_reference: NotRequired[MessageReference]
    mention_author: NotRequired[bool]
    ephemeral: NotRequired[bool]
    silent: NotRequired[bool]


class RegularMessage(BaseMessage):
    """This class is used to represent the blueprint of a message."""
    embed: NotRequired[Embed]


class ExpansiveMessage(BaseMessage):
    page_number_key: NotRequired[str]
    embed: ExpansiveEmbed


Page = Union[RegularMessage, ExpansiveMessage]


class Menu(Element):
    timeout: NotRequired[Optional[float]]
    pages: List[Union[str, Page]]


class Modal(Element):
    title: str
    components: Components


Elements = Union[RegularMessage, ExpansiveMessage, Menu, Modal]
Document = Dict[str, Elements]


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

    def deserialize(self, source: str, key: K_contra, callables: Dict[str, Callback]) -> ReturnType:
        """Method to deserialize a source into a Display object

        Args:
            source (str): The source text to deserialize
            key (K): The key of the element to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (ReturnType): All possible deserialized objects.
        """
        document: Document = json.loads(source)
        element: Elements = document[key]
        return self.deserialize_element(document, element, callables)

    def deserialize_element(self, document: Document, element: Elements, callables: Dict[str, Callback]) -> ReturnType:
        """Method to deserialize an element into a Display object

        Args:
            document (Document): The document to deserialize
            element (Elements): The element to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (ReturnType): All possible deserialized objects.
        """
        element_type: Optional[ElementTypes] = ElementTypes.from_str(element["type"])

        deserializers: Dict[ElementTypes, Callable[..., ReturnType]] = {
            ElementTypes.MESSAGE: self.deserialize_message,
            ElementTypes.EXPANSIVE: bind_menu(self.deserialize_expansive),
            ElementTypes.MENU: bind_menu(partial(self.deserialize_menu, document=document)),
            ElementTypes.MODAL: self.deserialize_modal,
        }
        assert element_type is not None, f"Invalid element type: {element['type']}"
        return deserializers[element_type](element, callables)

    # pylint: disable= too-many-locals
    def deserialize_message(
            self,
            message_tree: Union[RegularMessage, ExpansiveMessage],
            callables: Dict[str, Callback],
            **overrides: Any
    ) -> Message:
        """Method to deserialize an embed into a Display NamedTuple containing the embed and the view

        Args:
            message_tree (Dict[str, Any]): The embed to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            **overrides (Any): keyword arguments that override the messages

        Returns (Display): A Display NamedTuple containing the embed and the view
        """

        def render(embeds: List[Embed]) -> Sequence[discord.Embed]:
            return [self._render_embed(embed) for embed in embeds]

        message = Message(
            embed=apply(message_tree.get("embed"), self._render_embed),
            embeds=apply(message_tree.get("embeds"), render),
            content=message_tree.get("content"),
            tts=message_tree.get("tts"),
            nonce=apply(message_tree.get("nonce"), int),
            delete_after=apply(message_tree.get("delete_after"), float),
            suppress_embeds=message_tree.get("suppress_embeds"),
            file=apply(message_tree.get("file"), self._render_file),
            files=apply(message_tree.get("files"), lambda files: list(map(self._render_file, files))),
            allowed_mentions=apply(message_tree.get("allowed_mentions"), self._render_allowed_mentions),
            reference=apply(message_tree.get("message_reference"), lambda reference: discord.MessageReference(
                message_id=reference["message_id"],
                channel_id=reference["channel_id"],
                guild_id=reference.get("guild_id"),
            )),
            mention_author=message_tree.get("mention_author"),
            view=apply(message_tree.get("view"), self._render_view, callables),
            stickers=None,
            ephemeral=message_tree.get("ephemeral"),
            silent=message_tree.get("silent"),
        )

        for key, value in overrides.items():
            setattr(message, key, value)

        return message

    def deserialize_expansive(self, message_tree: ExpansiveMessage, callbacks: Dict[str, Callback]) -> List[Message]:
        """Method to deserialize a source into a list of Display objects

        Args:
            message_tree (ExpansiveMessage): The ExpansiveMessage of the message_tree
            callbacks (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (List[Display]): A list of Display objects
        """
        timeout = 180.0
        if "timeout" in message_tree:
            timeout = message_tree["timeout"]
        messages = [self.deserialize_message(message_tree, callbacks, embed=embed)
                    for embed in self._separate_embed(message_tree["embed"], message_tree.get("page_number_key"))]

        attach_views(messages, timeout)
        return messages

    def deserialize_page(
            self,
            document: Document,
            raw_page: Union[str, Page],
            callables: Dict[str, Callback]
    ) -> List[Message]:
        """Method to deserialize a page into a Display object

        Args:
            document (Document): the original document containing all the keys.
            raw_page (Page): The page to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (Display): A Display object
        """
        page = document[raw_page] if isinstance(raw_page, str) else raw_page
        element_type = ElementTypes.from_str(page["type"])
        if element_type == ElementTypes.MESSAGE:
            return [self.deserialize_message(cast(RegularMessage, page), callables)]
        if element_type == ElementTypes.EXPANSIVE:
            return self.deserialize_expansive(cast(ExpansiveMessage, page), callables)
        raise TypeError(f"Invalid type {element_type} for page")

    def deserialize_menu(self, menu: Menu, callables: Dict[str, Callback], *, document: Document) -> List[Message]:
        """Method to deserialize a menu into a list of Display objects

        Args:
            menu (Menu): The Menu Dictionary to deserialize into a List of Messages
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            document (Document): the original document containing all the keys.

        Returns (List[Message]): A list of Display objects
        """
        pages: List[Message] = sum((self.deserialize_page(document, page, callables) for page in menu["pages"]), [])

        timeout: Optional[float] = menu.get("timeout", 180.0)

        for page in pages:
            if page.view is None:
                page.view = ui.View(timeout=timeout)
            else:
                page.view.timeout = timeout
        return pages

    def deserialize_modal(self, tree: Modal, methods: Dict[str, Callback]) -> discord.ui.Modal:
        """Method to deserialize a modal into a discord.ui.Modal object

        Args:
            tree (Modal): The Modal Dictionary to deserialize into a discord.ui.Modal object
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        modal = type(f"{tree['title']} Modal", (discord.ui.Modal,), methods)(title=tree["title"])

        components = self.render_components(tree["components"]) if "components" in tree else []

        for component in components:
            modal.add_item(component)

        return modal

    def _separate_embed(self, raw_embed: ExpansiveEmbed, replacement_key: Optional[str]) -> List[discord.Embed]:
        """Separates the embeds from the raw embed element.

        Args:
            raw_embed (ElementTree.Element): The raw embed element.
            replacement_key (str): the key to replace with the page number.

        Returns (List[discord.Embed]): A list of embeds.
        """
        return make_expansive_embeds(raw_embed["expansive_field"]["name"],
                                     raw_embed["expansive_field"]["value"],
                                     replacement_key,
                                     raw_embed,
                                     self._render_embed)

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

    def _render_view(self, raw_view: View, callables: Dict[str, Callback]) -> ui.View:
        """Method to render a view element into a discord.ui.View object

        Args:
            raw_view (View) The view element to render
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons

        Returns (ui.View): A discord.ui.View object
        """
        view = ui.View()
        if "timeout" in raw_view:
            view.timeout = raw_view["timeout"]
        for component in self.render_components(raw_view["components"], callables):
            view.add_item(component)
        return view

    @staticmethod
    def _render_timestamp(timestamp: Optional[Timestamp]) -> Optional[datetime]:
        """Method to render a timestamp element into a datetime object

        Args:
            timestamp (Optional[Dict[str, str]]): The timestamp element to render

        Returns (Optional[datetime]): A datetime object
        """
        if timestamp is None:
            return None

        date = timestamp["date"]
        date_format = timestamp.get("format", "%Y-%m-%d %H:%M:%S.%f")
        return datetime.strptime(date, date_format)

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

    def render_components(
            self,
            components: Components,
            callables: Optional[Dict[str, Callback]] = None
    ) -> List[ui.Item]:
        """Renders the components specified by the identifier

        Args:
            components (Components): the dictionary containing the view component.
            callables (Dict[str, Callback]): the callbacks to be called when the user interacts with the components

        Returns (List[ui.Item]): the rendered components
        """
        if callables is None:
            callables = {}
        return [self.render_component(component, callables.get(key)) for key, component in components.items()]

    def _render_embed(self, raw_embed: Embed, *replacements: Tuple[str, str]) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           raw_embed (Embed): the dictionary containing the required key, values needed to render the embed.
           *replacements (Tuple[str, str]): Replace the first string with the second string in the embed.

        Returns:
            discord.Embed: Embed Object, discord compatible.
        """
        assert "colour" in raw_embed or "color" in raw_embed, "Embed must have either a colour or color key"

        def replace(value: Optional[str]) -> Optional[str]:
            if value is None:
                return value
            for replacement in replacements:
                value = value.replace(*replacement)
            return value

        embed = discord.Embed(
            title=replace(raw_embed["title"]),
            colour=make_colour(raw_embed["colour"] if "colour" in raw_embed else raw_embed["color"]),
            type="rich" if "type" not in raw_embed else raw_embed["type"],
            url=replace(raw_embed["url"]) if "url" in raw_embed else None,
            description=replace(raw_embed["description"]) if "description" in raw_embed else None,
            timestamp=self._render_timestamp(raw_embed.get("timestamp")),
        )

        for field in raw_embed.get("fields", []):
            embed.add_field(**field)

        if "footer" in raw_embed:
            embed.set_footer(text=replace(raw_embed["footer"].get("text")),
                             icon_url=replace(raw_embed["footer"].get("icon_url")))

        embed.set_thumbnail(url=replace(raw_embed.get("thumbnail")))
        embed.set_image(url=replace(raw_embed.get("image")))

        if "author" in raw_embed:
            embed.set_author(name=replace(raw_embed["author"]["name"]),
                             url=replace(raw_embed["author"]["url"]),
                             icon_url=replace(raw_embed["author"]["icon_url"]))

        return embed
