from __future__ import annotations

from datetime import datetime
from functools import partial
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, TypeVar, cast
from xml.etree import ElementTree

import discord
import discord.types.embed as embed_types
from discord import ui
from discord.abc import Snowflake
from typing_extensions import Concatenate, ParamSpec

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, DiscordIdentifier, Message
from qalib.translators.deserializer import Deserializer
from qalib.translators.message_parsing import (
    ButtonComponent,
    ChannelType,
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
    TextInputComponent,
)
from qalib.translators.parser import K, Parser

M = TypeVar("M")
N = TypeVar("N")
P = ParamSpec("P")


class XMLParser(Parser[K]):
    def __init__(self, source: str):
        """Initialisation of the XML Parser

        Args:
            source (str): the text of the XML file
        """
        self.root = ElementTree.fromstring(source)

    def get_message(self, identifier: K) -> str:
        """This method is used to get an embed by its key.

        Args:
            identifier (K): key of the embed

        Returns (str): a raw string containing the embed.
        """
        for message in self.root.findall("message"):
            if message.get("key") == identifier:
                return ElementTree.tostring(message, encoding="unicode", method="xml")
        raise KeyError(f"Message with key {identifier} not found")

    def get_menu(self, identifier: K) -> str:
        """This method is used to get a menu by its key.

        Args:
            identifier (K): key of the menu

        Returns (str): a raw string containing the menu.
        """
        for menu in self.root.findall("menu"):
            if menu.get("key") == identifier:
                return ElementTree.tostring(menu, encoding="unicode", method="xml")
        raise KeyError(f"Menu with key {identifier} not found")

    def get_modal(self, identifier: K) -> str:
        """This method is used to get a modal by its key.

        Args:
            identifier (K): key of the modal

        Returns (str): a raw string containing the modal.
        """
        for modal in self.root.findall("modal"):
            if modal.get("key") == identifier:
                return ElementTree.tostring(modal, encoding="unicode", method="xml")
        raise KeyError(f"Modal with key {identifier} not found")

    def template_message(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template an embed, by identifying it by its key and using the template engine to
        template it.

        Args:
            key (K): key of the embed
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed
        """
        return template_engine.template(self.get_message(key), keywords)

    def template_menu(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template a menu, by identifying it by its key and using the template engine to
        template it.

        Args:
            key (K): key of the menu
            template_engine (TemplateEngine): template engine that is used to template the menu
            keywords (Dict[str, Any]): keywords that are used to template the menu

        Returns (str): templated menu
        """
        return template_engine.template(self.get_menu(key), keywords)

    def template_modal(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template a modal, by identifying it by its key and using the template engine to
        template it.

        Args:
            key (K): key of the modal
            template_engine (TemplateEngine): template engine that is used to template the modal
            keywords (Dict[str, Any]): keywords that are used to template the modal

        Returns (str): templated modal
        """
        return template_engine.template(self.get_modal(key), keywords)


class XMLDeserializer(Deserializer):
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    def deserialize_into_message(self, source: str, callables: Dict[str, Callback], **kw) -> Message:
        """Deserializes an embed from an XML file, and returns it as a Display object.

        Args:
            source (str): templated document contents to deserialize.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            **kw (Dict[str, Any]): A dictionary containing the keyword arguments to use for the view.

        Returns (Display): A display object containing the embed and its view.
        """
        return self.deserialize_message(ElementTree.fromstring(source), callables, kw)

    def deserialize_message(
            self,
            message_tree: ElementTree.Element,
            callables: Dict[str, Callback],
            kwargs: Dict[str, Any],
    ) -> Message:
        """Deserializes an embed from an ElementTree.Element, and returns it as a Display object.

        Args:
            message_tree (ElementTree.Element): The element to deserialize the embed from.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            kwargs (Dict[str, Any]): A dictionary containing the keyword arguments to use for the view.

        Returns (Message): A display object containing the embed and its view.
        """

        def get_text(element_tree: ElementTree.Element, child: str) -> Optional[str]:
            element = element_tree.find(child)
            if element is None:
                return None
            return None if element.text is None else element.text

        def get_element(element_tree: ElementTree.Element, child: str) -> Optional[ElementTree.Element]:
            return None if (element := element_tree.find(child)) is None else element

        def apply(
                element: Optional[M],
                func: Callable[Concatenate[M, P], N],
                *args: P.args,
                **keyword_args: P.kwargs,
        ) -> Optional[N]:
            if element is None:
                return None
            return func(element, *args, **keyword_args)

        return Message(
            embed=apply(get_element(message_tree, "embed"), self._render_embed),
            embeds=apply(
                get_element(message_tree, "embeds"),
                lambda raw_tree: list(map(self._render_embed, raw_tree)),
            ),
            view=apply(get_element(message_tree, "view"), self._render_view, callables, kwargs),
            content=get_text(message_tree, "content"),
            tts=apply(get_text(message_tree, "tts"), lambda string: string.lower() == "true"),
            nonce=apply(get_text(message_tree, "nonce"), int),
            delete_after=apply(get_text(message_tree, "delete_after"), float),
            suppress_embeds=apply(
                get_element(message_tree, "suppress_embeds"),
                lambda tree: self.get_attribute(tree, "value") in ("", "true"),
            ),
            file=apply(get_element(message_tree, "file"), self._render_file),
            files=apply(
                get_element(message_tree, "files"),
                lambda raw_tree: list(map(self._render_file, raw_tree)),
            ),
            allowed_mentions=apply(
                get_element(message_tree, "allowed_mentions"),
                self._render_allowed_mentions,
            ),
            reference=apply(get_element(message_tree, "reference"), self._render_reference),
            mention_author=apply(
                get_element(message_tree, "mention_author"),
                lambda tree: self.get_attribute(tree, "value") in ("", "true"),
            ),
            stickers=None,
            ephemeral=None,
            silent=apply(
                get_element(message_tree, "silent"),
                lambda tree: self.get_attribute(tree, "value") in ("", "true"),
            )
        )

    def deserialize_into_menu(self, source: str, callables: Dict[str, Callback], **kw) -> List[Message]:
        """Deserializes a menu from an XML file, by generating a list of displays that are connected by buttons in their
        views to navigate between them.

        Args:
            source (str): The XML file to deserialize.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            **kw (Dict[str, Any]): A dictionary containing the keyword arguments to use for the views.

        Returns (List[Display]): List of displays that are connected by buttons in their views to navigate between them.
        """

        menu_tree: ElementTree.Element = ElementTree.fromstring(source)
        return [self.deserialize_message(embed, callables, kw) for embed in menu_tree.findall("message")]

    def deserialize_into_modal(self, source: str, methods: Dict[str, Callback], **kwargs: Any) -> discord.ui.Modal:
        """Method to deserialize a modal into a discord.ui.Modal object

        Args:
            source (str): The source text to deserialize into a modal
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            **kwargs (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        modal_tree = ElementTree.fromstring(source)
        return self._render_modal(modal_tree, methods, **kwargs)

    def _render_modal(self, tree: ElementTree.Element, methods: Dict[str, Callback], **kwargs: Any) -> discord.ui.Modal:
        """Method to render a modal from a modal tree

        Args:
            tree (Dict[str, Any]): The modal tree to render
            methods (Dict[str, Callback]): A dictionary containing the callables to use for the buttons
            kwargs (Dict[str, Any]): A dictionary containing the keywords to use for the view

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        title = self.get_attribute(tree, "title")
        modal = type(f"{title} Modal", (discord.ui.Modal,), {**methods, **kwargs})(title=title)

        for component in self.render_components(tree):
            modal.add_item(component)

        return modal

    @staticmethod
    def _render_reference(
            reference_tree: ElementTree.Element,
    ) -> discord.MessageReference:
        """Renders a message reference object from an ElementTree.Element.

        Args:
            reference_tree (ElementTree.Element): The element to render the message reference object from.

        Returns (discord.MessageReference): The message reference object.
        """
        message_id = reference_tree.find("message_id")
        channel_id = reference_tree.find("channel_id")
        guild_id = reference_tree.find("guild_id")

        if message_id is None or message_id.text is None:
            raise ValueError("Message reference must have a message id")

        if channel_id is None or channel_id.text is None:
            raise ValueError("Message reference must have a channel id")

        return discord.MessageReference(
            message_id=int(message_id.text),
            channel_id=int(channel_id.text),
            guild_id=None if guild_id is None or guild_id.text is None else int(guild_id.text),
        )

    def _render_allowed_mentions(self, raw_mentions: ElementTree.Element) -> discord.AllowedMentions:
        """Renders an allowed mentions object from an ElementTree.Element.

        Args:
            raw_mentions (ElementTree.Element): The element to render the allowed mentions object from.

        Returns (discord.AllowedMentions): The allowed mentions object.
        """

        def get_value(element: Optional[ElementTree.Element] = None) -> bool:
            if element is None:
                return True
            return self.get_attribute(element, "mention").lower() != "false"

        def extract_tags(
                element: Optional[ElementTree.Element], child_tag: Optional[str] = None
        ) -> bool | Sequence[Snowflake]:
            if element is None:
                return True
            if child_tag is not None and len(element) > 0:
                return [DiscordIdentifier(int(self.get_element_text(child))) for child in element.findall(child_tag)]

            return get_value(element)

        return discord.AllowedMentions(
            everyone=get_value(raw_mentions.find("everyone")),
            users=extract_tags(raw_mentions.find("users"), "user"),
            roles=extract_tags(raw_mentions.find("roles"), "role"),
            replied_user=get_value(raw_mentions.find("replied_user")),
        )

    def _render_file(self, raw_file: ElementTree.Element) -> discord.File:
        return discord.File(
            fp=self.get_element_text(raw_file.find("filename")),
            spoiler=self.get_element_text(raw_file.find("spoilers")).lower() == "true",
            description=self.get_element_text(raw_file.find("description")),
        )

    def _render_view(
            self,
            raw_view: ElementTree.Element,
            callables: Dict[str, Callback],
            kwargs: Dict[str, Any],
    ) -> ui.View:
        """Renders a view from an ElementTree.Element.

        Args:
            raw_view (ElementTree.Element): The element to render the view from.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            kwargs (Dict[str, Any]): A dictionary containing the keyword arguments to use for the view.

        Returns (ui.View): A view object containing the components.
        """
        view = ui.View(**kwargs)
        for component in self.render_components(raw_view, callables):
            view.add_item(component)
        return view

    @staticmethod
    def get_element_text(element: Optional[ElementTree.Element]) -> str:
        """Renders the given ElementTree.Element by returning its text.

        Args:
            element (ElementTree.Element): The element to render.

        Returns (str): The rendered element.
        """
        return "" if element is None or element.text is None else element.text

    @staticmethod
    def get_attribute(element: ElementTree.Element, attribute: str) -> str:
        """Renders an attribute from an ElementTree.Element.

        Args:
            element (ElementTree.Element): The element to render the attribute from.
            attribute (str): The name of the attribute to render.

        Returns (str): The value of the attribute.
        """
        return "" if (value := element.get(attribute)) is None else value

    def _render_timestamp(self, timestamp_element: Optional[ElementTree.Element]) -> Optional[datetime]:
        """Renders the timestamp from an ElementTree.Element. Element may contain an attribute "format" which will be
        used to parse the timestamp.

        Args:
            timestamp_element (Optional[ElementTree.Element]): The element to render the timestamp from.

        Returns (Optional[datetime]): A datetime object containing the timestamp.
        """
        if timestamp_element is not None:
            timestamp = self.get_element_text(timestamp_element)
            date_format = self.get_attribute(timestamp_element, "format")
            if date_format == "":
                date_format = "%Y-%m-%d %H:%M:%S.%f"
            return datetime.strptime(timestamp, date_format) if timestamp != "" else None
        return None

    def _render_author(self, author_element: ElementTree.Element) -> Author:
        """Renders the author from an ElementTree.Element.

        Args:
            author_element (ElementTree.Element): The element to render the author information from.

        Returns (Optional[dict]): A dictionary containing the raw author.
        """
        return {
            "name": self.get_element_text(author_element.find("name")),
            "url": self.get_element_text(author_element.find("url")),
            "icon_url": self.get_element_text(author_element.find("icon")),
        }

    def _render_footer(self, footer_element: ElementTree.Element) -> Footer:
        """Renders the footer from an ElementTree.Element.

        Args:
            footer_element (ElementTree.Element): The element to render the footer from.

        Returns (Optional[dict]): A dictionary containing the raw footer.
        """
        return {
            "text": self.get_element_text(footer_element.find("text")),
            "icon_url": self.get_element_text(footer_element.find("icon")),
        }

    def _render_fields(self, fields_element: Optional[ElementTree.Element]) -> List[Field]:
        """Renders the fields from an ElementTree.Element.

        Args:
            fields_element (ElementTree.Element): The element to render the fields from.

        Returns (List[dict]): A list of dictionaries containing the raw fields.
        """
        assert fields_element is not None, "Expected Fields For Embed"

        return [
            {
                "name": self.get_element_text(field.find("name")),
                "value": self.get_element_text(field.find("value")),
                "inline": self.get_attribute(field, "inline").lower() == "true",
            }
            for field in fields_element.findall("field")
        ]

    @staticmethod
    def pop_component(component: ElementTree.Element, key: str) -> Optional[ElementTree.Element]:
        """Pops a component from the given element, and returns it.

        Args:
            component (ElementTree.Element): The element to pop the component from.
            key (str): The key of the component to pop.

        Returns (Optional[ElementTree.Element]): The popped component, or None if it doesn't exist.
        """
        if (child_component := component.find(key)) is not None:
            component.remove(child_component)
        return child_component

    def _render_emoji(self, emoji_element: Optional[ElementTree.Element]) -> Optional[Emoji]:
        """Renders an ElementTree.Element into a dictionary.

        Args:
            emoji_element (Optional[ElementTree.Element]): The element to render into a Dictionary of emoji data

        Returns (Optional[Dict[str, str]]): The rendered emoji, or None if the element is None.
        """
        if emoji_element is None:
            return None

        if emoji_element.find("name") is None:
            raise ValueError("Expected Name For Emoji")

        emoji = Emoji(name=self.get_element_text(emoji_element.find("name")))

        if (id_element := emoji_element.find("id")) is not None:
            assert id_element.text is not None
            emoji["id"] = int(id_element.text)
        if (animated_element := emoji_element.find("animated")) is not None:
            assert animated_element.text is not None
            emoji["animated"] = animated_element.text.lower() == "true"

        return emoji

    def _extract_elements(self, tree: ElementTree.Element) -> Dict[str, Any]:
        """Extracts the elements from the given ElementTree.Element, and returns them as a dictionary.

        Args:
            tree (ElementTree.Element): The element to extract the elements from.

        Returns (Dict[str, Any]): A dictionary containing the extracted elements.
        """
        return {element.tag: self.get_element_text(element) for element in tree}

    def _render_button(self, component: ElementTree.Element, callback: Optional[Callback]) -> ui.Button:
        """Renders a button based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The button to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this button.

        Returns (ui.Button): The rendered button.
        """
        emoji_component = self.pop_component(component, "emoji")
        attributes = self._extract_elements(component)
        attributes["emoji"] = self._render_emoji(emoji_component)
        attributes["callback"] = callback
        attributes["disabled"] = attributes["disabled"].lower() == "true" if "disabled" in attributes else False

        button: ui.Button = create_button(cast(ButtonComponent, attributes))
        return button

    def _render_options(self, raw_options: Optional[ElementTree.Element]) -> List[discord.SelectOption]:
        """Renders a list of options based on the template in the element, and formatted values given by the keywords.

        Args:
            raw_options (ElementTree.Element): The options to render, contains the template.

        Returns (List[discord.SelectOption]): The rendered options.
        """
        options = []
        for option in raw_options or []:
            emoji_component = self.pop_component(option, "emoji")
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
        options = self._render_options(self.pop_component(component, "options"))

        attributes = self._extract_elements(component)
        attributes["options"] = options
        attributes["callback"] = callback

        select: ui.Select = create_select(**attributes)

        return select

    def _render_channel_select(self, component: ElementTree.Element, callback: Optional[Callback]) -> ui.ChannelSelect:
        """Renders a channel select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The channel select to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this channel select.

        Returns (ui.ChannelSelect): The rendered channel select.
        """
        channel_types: Optional[ElementTree.Element] = self.pop_component(component, "channel_types")

        attributes = self._extract_elements(component)
        if channel_types is not None:
            attributes["channel_types"] = make_channel_types(
                [cast(ChannelType, self.get_element_text(channel)) for channel in channel_types.findall("channel_type")]
            )
        attributes["callback"] = callback
        select: ui.ChannelSelect = create_channel_select(**attributes)
        return select

    def _render_type_select(
            self,
            component: ElementTree.Element,
            callback: Optional[Callback],
            select_base: Type[ui.UserSelect | ui.RoleSelect | ui.MentionableSelect],
    ) -> ui.UserSelect | ui.RoleSelect | ui.MentionableSelect:
        """Renders a type select based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The type select to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this role select.
            select_base (Type[ui.UserSelect | ui.RoleSelect | ui.MentionableSelect]): The type of select to render.

        Returns (ui.RoleSelect): The rendered role select.
        """
        attributes = self._extract_elements(component)
        select_type = type(select_base.__name__, (select_base,), {"callback": callback})

        assert issubclass(select_type, (ui.UserSelect, ui.RoleSelect, ui.MentionableSelect))

        select = create_type_select(select_type, **attributes)
        return select

    def _render_text_input(self, component: ElementTree.Element, callback: (Optional[Callback])) -> ui.TextInput:
        """Renders a text input based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The text input to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this text input.

        Returns (ui.TextInput): The rendered text input.
        """
        attributes = self._extract_elements(component)
        attributes["callback"] = callback
        text_input: ui.TextInput = create_text_input(cast(TextInputComponent, attributes))

        return text_input

    def render_component(self, component: ElementTree.Element, callback: Optional[Callback]) -> ui.Item:
        """Renders a component based on the tag in the element.

        Args:
            component (ElementTree.Element): The component to render, contains all template.
            callback (Optional[Callback]): The callback to use if the user interacts with this component.

        Returns (discord.ui.Item): The rendered component.
        """

        components: Dict[str, Callable[[ElementTree.Element, Optional[Callback]], ui.Item]] = {
            "button": self._render_button,
            "select": self._render_select,
            "channel_select": self._render_channel_select,
            "text_input": self._render_text_input,
            "role_select": partial(self._render_type_select, select_base=ui.RoleSelect),
            "mentionable_select": partial(self._render_type_select, select_base=ui.MentionableSelect),
            "user_select": partial(self._render_type_select, select_base=ui.UserSelect),
        }
        renderer: Callable[[ElementTree.Element, Optional[Callback]], ui.Item] = components[component.tag]
        return renderer(component, callback)

    def render_components(
            self, view: ElementTree.Element, callables: Optional[Dict[str, Callback]] = None
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
                callables.get(self.get_attribute(component, "key")),
            )
            for component in view
        ]

    def _render_embed(self, raw_embed: ElementTree.Element) -> discord.Embed:
        """Render the desired templated embed in discord.Embed instance.

        Args:
           raw_embed(ElementTree.Element): The element to render the embed from.

        Returns:
            Embed: Embed Object, discord compatible.
        """

        def render(name: str):
            return self.get_element_text(raw_embed.find(name))

        embed_type: embed_types.EmbedType = "rich"
        if cast(embed_types.EmbedType, given_type := render("type")) != "":
            embed_type = cast(embed_types.EmbedType, given_type)

        embed = discord.Embed(
            title=render("title"),
            colour=make_colour(render("colour")),
            type=embed_type,
            url=render("url"),
            description=render("description"),
            timestamp=self._render_timestamp(raw_embed.find("timestamp")),
        )

        for field in self._render_fields(raw_embed.find("fields")):
            embed.add_field(**field)

        if (footer := raw_embed.find("footer")) is not None:
            embed.set_footer(**self._render_footer(footer))

        embed.set_thumbnail(url=self.get_element_text(raw_embed.find("thumbnail")))
        embed.set_image(url=self.get_element_text(raw_embed.find("image")))

        if (author := raw_embed.find("author")) is not None:
            embed.set_author(**self._render_author(author))

        return embed
