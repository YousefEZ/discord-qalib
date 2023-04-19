from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, List, Literal, Optional, Type, TypedDict, TypeVar, Union, cast

import discord
import discord.types.embed
from discord import ui
from discord.abc import Snowflake
from typing_extensions import NotRequired

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, DiscordIdentifier, Message
from qalib.translators.deserializer import Deserializer
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
)
from qalib.translators.parser import K, Parser

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


Components = Union[Button, Select, CustomSelect, ChannelSelect, TextInput]


class Timestamp(TypedDict):
    """This class is used to represent object's timestamp."""

    date: str
    format: NotRequired[str]


class Embed(TypedDict):
    """This class is used to represent the blueprint of an embed."""

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


View = Dict[str, Components]


class JSONMessage(TypedDict):
    """This class is used to represent the blueprint of a message."""

    embed: NotRequired[Embed]
    embeds: NotRequired[List[Embed]]
    view: NotRequired[View]
    content: NotRequired[str]
    tts: NotRequired[bool]
    nonce: NotRequired[int]
    delete_after: NotRequired[float]
    suppress_embeds: NotRequired[bool]
    file: NotRequired[File]
    files: NotRequired[List[File]]
    allowed_mentions: NotRequired[AllowedMentions]
    message_reference: NotRequired[MessageReference]
    mention_author: NotRequired[bool]
    silent: NotRequired[bool]


JSONMenu = Dict[str, JSONMessage]


class JSONModal(TypedDict):
    title: str
    components: Dict[str, Components]


Template = Dict[str, Union[JSONMessage, JSONMenu, JSONModal]]


class JSONParser(Parser[K]):
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

    def template_message(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template the embed by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (K): key of the embed
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed in the form of string.
        """
        return json.dumps(self.recursive_template(deepcopy(self._data[key]), template_engine, keywords))

    def template_menu(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """Method that is used to template the menu by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (K): key of the menu
            template_engine (TemplateEngine): template engine that is used to template the menu
            keywords (Dict[str, Any]): keywords that are used to template the menu

        Returns (str): templated menu in the form of string.
        """
        return json.dumps(self.recursive_template(deepcopy(self._data[key]), template_engine, keywords))

    def template_modal(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """Method that is used to template the modal by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (K): key of the modal
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

    # pylint: disable= too-many-locals
    def deserialize_message(
        self,
        message_tree: JSONMessage,
        callables: Dict[str, Callback],
        kwargs: Dict[str, Any],
    ) -> Message:
        """Method to deserialize an embed into a Display NamedTuple containing the embed and the view

        Args:
            message_tree (Dict[str, Any]): The embed to deserialize
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kwargs (Dict[str, Any]): A dictionary containing the attributes to use for the view

        Returns (Display): A Display NamedTuple containing the embed and the view
        """
        view_tree = message_tree.get("view")
        embed = self.render(embed_tree) if (embed_tree := message_tree.get("embed")) is not None else None
        view = None if view_tree is None else self._render_view(view_tree, callables, kwargs)
        return Message(
            embed=embed,
            embeds=None if (embeds := message_tree.get("embeds")) is None else list(map(self.render, embeds)),
            content=message_tree.get("content", None),
            tts=None
            if (tts_element := message_tree.get("tts")) is None
            else ((isinstance(tts_element, bool) and tts_element) or str(tts_element).lower() == "true"),
            nonce=None if (nonce_element := message_tree.get("nonce")) is None else int(nonce_element),
            delete_after=None if (delete_after := message_tree.get("delete_after")) is None else float(delete_after),
            suppress_embeds=None if (suppress := message_tree.get("suppress_embeds")) is None else suppress,
            file=None if (file := message_tree.get("file")) is None else self._render_file(file),
            files=None if (files := message_tree.get("files")) is None else list(map(self._render_file, files)),
            allowed_mentions=None
            if (allowed_mentions := message_tree.get("allowed_mentions")) is None
            else self._render_allowed_mentions(allowed_mentions),
            reference=None
            if (reference := message_tree.get("message_reference")) is None
            else discord.MessageReference(
                message_id=reference["message_id"],
                channel_id=reference["channel_id"],
                guild_id=reference.get("guild_id"),
            ),
            mention_author=message_tree.get("mention_author"),
            view=view,
            stickers=None,
            ephemeral=None,
            silent=message_tree.get("silent")
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

    def _render_modal(self, tree: JSONModal, methods: Dict[str, Callback], kwargs: Dict[str, Any]) -> discord.ui.Modal:
        """Method to render a modal from a modal tree

        Args:
            tree (Dict[str, Any]): The modal tree to render
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kwargs (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        modal = type(f"{tree['title']} Modal", (discord.ui.Modal,), methods)(title=(tree["title"]), **kwargs)

        components = self.render_components(tree["components"]) if "components" in tree else []

        for component in components:
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

    def _render_view(self, raw_view: View, callables: Dict[str, Callback], kwargs: Dict[str, Any]) -> ui.View:
        """Method to render a view element into a discord.ui.View object

        Args:
            raw_view (View) The view element to render
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kwargs (Dict[str, Any]): A dictionary containing the attributes to use for the view

        Returns (ui.View): A discord.ui.View object
        """
        view = ui.View(**kwargs)
        for component in self.render_components(raw_view, callables):
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
        component: Components,
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

    def render_components(self, view: View, callables: Optional[Dict[str, Callback]] = None) -> List[ui.Item]:
        """Renders the components specified by the identifier

        Args:
            view (Dict[str, ...]): the dictionary containing the view component.
            callables (Dict[str, Callback]): the callbacks to be called when the user interacts with the components

        Returns (Optional[List[ui.Item]]): the rendered components
        """
        if callables is None:
            callables = {}
        return [self.render_component(component, callables.get(key)) for key, component in view.items()]

    def render(self, raw_embed: Embed) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance

        Args:
           raw_embed (Embed): the dictionary containing the required key, values needed to render the
                                        embed.

        Returns:
            discord.Embed: Embed Object, discord compatible.
        """
        assert "colour" in raw_embed or "color" in raw_embed, "Embed must have either a colour or color key"

        embed = discord.Embed(
            title=raw_embed["title"],
            colour=make_colour(raw_embed["colour"] if "colour" in raw_embed else raw_embed["color"]),
            type="rich" if "type" not in raw_embed else raw_embed["type"],
            url=raw_embed["url"] if "url" in raw_embed else None,
            description=raw_embed["description"] if "description" in raw_embed else None,
            timestamp=self._render_timestamp(raw_embed.get("timestamp")),
        )

        for field in raw_embed["fields"]:
            embed.add_field(**field)

        if "footer" in raw_embed:
            embed.set_footer(**raw_embed["footer"])

        embed.set_thumbnail(url=raw_embed.get("thumbnail"))
        embed.set_image(url=raw_embed.get("image"))

        if "author" in raw_embed:
            embed.set_author(**raw_embed["author"])

        return embed
