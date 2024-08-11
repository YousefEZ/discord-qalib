from __future__ import annotations

from functools import partial
from typing import Optional, Dict, Any, List, Callable, Sequence, cast, Type
from xml.etree import ElementTree

import discord
from discord import ui
from discord.abc import Snowflake

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback, Message, DiscordIdentifier
from qalib.translators.deserializer import Deserializer, K_contra, ReturnType, ElementTypes
from qalib.translators.element.embed import render
from qalib.translators.element.expansive import expand
from qalib.translators.element.types.embed import Emoji
from qalib.translators.events import EventCallbacks
from qalib.translators.menu import Menu, MenuActions
from qalib.translators.message_parsing import (
    ButtonComponent,
    apply,
    create_button,
    make_emoji,
    create_select,
    make_channel_types,
    ChannelType,
    create_channel_select,
    create_type_select,
    create_text_input,
    TextInputComponent,
)
from qalib.translators.modal import ModalEvents, ModalEventsCallbacks, QalibModal
from qalib.translators.templater import Templater
from qalib.translators.view import QalibView
from qalib.translators.xml.embed import filter_tabs, XMLEmbedAdapter, XMLExpansiveEmbedAdapter


def get_text(element_tree: ElementTree.Element, child: str) -> Optional[str]:
    element = element_tree.find(child)
    if element is None:
        return None
    return None if element.text is None else element.text


def get_element(element_tree: ElementTree.Element, child: str) -> Optional[ElementTree.Element]:
    return None if (element := element_tree.find(child)) is None else element


class XMLTemplater(Templater):
    def __init__(self, source: str):
        """Initialisation of the XML Parser

        Args:
            source (str): the text of the XML file
        """
        self.source = source

    def template(self, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template an element, by identifying it by its key and using the template engine to
        template it.

        Args:
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed
        """
        return template_engine.template(self.source, keywords)


class XMLDeserializer(Deserializer[K_contra]):
    """Read and process the data given by the XML file, and use given user objects to render the text"""

    def _get_element(self, document: ElementTree.Element, key: str) -> ElementTree.Element:
        for element in document:
            if key == self.get_attribute(element, "key"):
                return element
        raise KeyError("Key not found")

    def deserialize(
        self, source: str, key: K_contra, callables: Dict[str, Callback], events: EventCallbacks
    ) -> ReturnType:
        """This method is used to deserialize the embed from the XML file.

        Args:
            source (str): raw string containing the element
            key (K): key of the element
            callables (Dict[str, Callback]): dictionary containing the callables to use for the components
            events (EventCallbacks): dictionary containing the events to use for the components

        Returns (Message): message containing the embed and its view
        """
        document = ElementTree.fromstring(source)
        element = self._get_element(document, key)
        return self.deserialize_element(document, element, callables, events)

    def deserialize_element(
        self,
        document: ElementTree.Element,
        element: ElementTree.Element,
        callables: Dict[str, Callback],
        events: EventCallbacks,
    ) -> ReturnType:
        """This method is used to deserialize the embed from the XML file.

        Args:
            document (ElementTree.Element): document containing all the elements
            element (ElementTree.Element): element containing the embed
            callables (Dict[str, Callback]): dictionary containing the callables to use for the components
            events (EventCallbacks): dictionary containing the events to use for the components

        Returns (ReturnType): all possible deserialized objects.
        """
        element_type = ElementTypes.from_str(element.tag)

        if element_type == ElementTypes.MESSAGE:
            return self.deserialize_message(element, callables, events)
        if element_type == ElementTypes.EXPANSIVE:
            return self.deserialize_expansive_into_menu(element, callables, events)
        if element_type == ElementTypes.MENU:
            return self.deserialize_menu(element, callables, events, document=document)
        if element_type == ElementTypes.MODAL:
            return self.deserialize_modal(element, callables, cast(Dict[ModalEvents, ModalEventsCallbacks], events))
        raise TypeError(f"Unrecognized ElementType {element_type}")

    def deserialize_expansive_into_menu(
        self, element: ElementTree.Element, callbacks: Dict[str, Callback], events: EventCallbacks
    ) -> Menu:
        pages = self.deserialize_expansive(element, callbacks, events)
        timeout_element = element.find("timeout")
        timeout: Optional[float] = 180.0
        if timeout_element is not None:
            timeout = None if timeout_element.text is None else float(timeout_element.text)

        arrows: Dict[MenuActions, ButtonComponent] = self.deserialize_menu_arrows(element)
        return Menu(pages, timeout, arrows, events)

    def deserialize_expansive(
        self, element: ElementTree.Element, callbacks: Dict[str, Callback], events: EventCallbacks
    ) -> List[Message]:
        """Deserializes an embed from an XML file, and returns it as a Display object.

        Args:
            element (ElementTree.Element): templated document contents to deserialize.
            callbacks (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            events (EventCallbacks): A dictionary containing the events to use for the components.

        Returns (List[Message]): A list of messages containing the embed and its view.
        """
        raw_embed = element.find("embed")
        assert raw_embed is not None, "Embed not found"

        return [
            self.deserialize_message(element, callbacks, events, embed=e)
            for e in expand(XMLExpansiveEmbedAdapter(raw_embed, element.get("page_number_key")))
        ]

    def deserialize_menu_arrows(self, arrows_view: ElementTree.Element) -> Dict[MenuActions, ButtonComponent]:
        """Deserializes the arrows of a menu from an XML file, and returns it as a dictionary.

        Args:
            arrows_view (ElementTree.Element): templated document contents to deserialize.

        Returns (Dict[MenuActions, ButtonComponent]): A dictionary containing the arrows.
        """
        arrows: Dict[MenuActions, ButtonComponent] = {}
        previous_element = arrows_view.find("previous")
        next_element = arrows_view.find("next")
        if previous_element is not None:
            arrows[MenuActions.PREVIOUS] = self._create_button_component(previous_element)
        if next_element is not None:
            arrows[MenuActions.NEXT] = self._create_button_component(next_element)

        return arrows

    def deserialize_message(
        self,
        message_tree: ElementTree.Element,
        callables: Dict[str, Callback],
        events: EventCallbacks,
        **overrides: Any,
    ) -> Message:
        """Deserializes an embed from an ElementTree.Element, and returns it as a Display object.

        Args:
            message_tree (ElementTree.Element): The element to deserialize the embed from.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            events (EventCallbacks): A dictionary containing the events to use for the components.
            **overrides (Any): any overrides to apply to the Message

        Returns (Message): A display object containing the embed and its view.
        """
        message = Message(
            embed=apply(get_element(message_tree, "embed"), lambda raw_embed: render(XMLEmbedAdapter(raw_embed))),
            embeds=apply(
                get_element(message_tree, "embeds"),
                lambda raw_tree: [render(XMLEmbedAdapter(raw_embed)) for raw_embed in raw_tree],
            ),
            view=apply(get_element(message_tree, "view"), self._render_view, callables, events),
            content=" ".join(filter_tabs(get_text(message_tree, "content")).split("\n"))
            if apply(get_element(message_tree, "content"), lambda element: self.get_attribute(element, "strip"))
            == "true"
            else filter_tabs(get_text(message_tree, "content")),
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
            ),
        )
        for key, value in overrides.items():
            setattr(message, key, value)
        return message

    def deserialize_page(
        self,
        document: ElementTree.Element,
        element: ElementTree.Element,
        callables: Dict[str, Callback],
        events: EventCallbacks,
    ) -> List[Message]:
        if element.tag == "page":
            element = self._get_element(document, self.get_attribute(element, "key"))
        element_type = ElementTypes.from_str(element.tag)

        page_deserializers: Dict[
            ElementTypes, Callable[[ElementTree.Element, Dict[str, Callback], EventCallbacks], List[Message]]
        ] = {
            ElementTypes.MESSAGE: lambda page, callback, m_events: [self.deserialize_message(page, callback, m_events)],
            ElementTypes.EXPANSIVE: self.deserialize_expansive,
        }
        assert element_type is not None, f"Element type {element.tag} not found"
        return page_deserializers[element_type](element, callables, events)

    def deserialize_menu(
        self,
        element: ElementTree.Element,
        callables: Dict[str, Callback],
        events: EventCallbacks,
        *,
        document: ElementTree.Element,
    ) -> Menu:
        """Deserializes a menu from an XML file, by generating a list of displays that are connected by buttons in their
        views to navigate between them.

        Args:
            element (ElementTree.Element): The XML Menu Element to deserialize.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.
            events (EventCallbacks): A dictionary containing the events to callback on.
            document (ElementTree.Element): The entire document

        Returns (List[Display]): List of displays that are connected by buttons in their views to navigate between them.
        """
        raw_pages = element.find("pages")
        assert raw_pages is not None, "pages is not present"

        pages: List[Message] = sum([self.deserialize_page(document, page, callables, events) for page in raw_pages], [])

        timeout_ele = element.find("timeout")
        timeout = float(timeout_ele.text) if timeout_ele is not None and timeout_ele.text is not None else None

        view = element.find("arrows")
        if view is None:
            return Menu(pages, timeout, events=events)

        arrows: Dict[MenuActions, ButtonComponent] = self.deserialize_menu_arrows(view)
        return Menu(pages, timeout, arrows, events)

    def deserialize_modal(
        self,
        element: ElementTree.Element,
        callables: Dict[str, Callback],
        events: Dict[ModalEvents, ModalEventsCallbacks],
    ) -> discord.ui.Modal:
        """Method to deserialize a modal into a discord.ui.Modal object

        Args:
            element (ElementTree.Element): The element to deserialize into a modal
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components
            events (Dict[ModalEvents, ModalEventsCallbacks]): A dictionary containing the events to callback on

        Returns (discord.ui.Modal): A discord.ui.Modal object
        """
        title = self.get_attribute(element, "title")
        timeout_element = element.find("timeout")
        if timeout_element is not None:
            timeout = float(timeout_element.text) if timeout_element.text is not None else None
            modal = QalibModal(title=title, events=events, timeout=timeout, custom_id=element.get("custom_id"))
        else:
            modal = QalibModal(title=title, events=events, custom_id=element.get("custom_id"))

        for component in self.render_components(element, callables):
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
        events: EventCallbacks,
    ) -> ui.View:
        """Renders a view from an ElementTree.Element.

        Args:
            raw_view (ElementTree.Element): The element to render the view from.
            callables (Dict[str, Callback]): A dictionary containing the callables to use for the components.

        Returns (ui.View): A view object containing the components.
        """
        view = QalibView(events)
        timeout = raw_view.find("timeout")
        if timeout is not None:
            view.timeout = None if timeout.text is None else float(timeout.text)
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

    def _create_button_component(self, component: ElementTree.Element) -> ButtonComponent:
        """Creates a button component from the given element.

        Args:
            component (ElementTree.Element): The element to create the button component from.

        Returns (ButtonComponent): The created button component.
        """
        emoji_component = self.pop_component(component, "emoji")
        attributes = self._extract_elements(component)
        attributes["emoji"] = self._render_emoji(emoji_component)
        attributes["disabled"] = attributes["disabled"].lower() == "true" if "disabled" in attributes else False

        return cast(ButtonComponent, attributes)

    def _render_button(self, component: ElementTree.Element, callback: Optional[Callback] = None) -> ui.Button:
        """Renders a button based on the template in the element, and formatted values given by the keywords.

        Args:
            component (ElementTree.Element): The button to render, contains the template.
            callback (Optional[Callback]): The callback to use if the user interacts with this button.

        Returns (ui.Button): The rendered button.
        """
        button: ButtonComponent = self._create_button_component(component)
        if callback:
            button["callback"] = callback

        return create_button(button)

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
        attributes["callback"] = callback

        return create_type_select(select_base, **attributes)

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

    def render_components(self, view: ElementTree.Element, callables: Dict[str, Callback]) -> List[ui.Item]:
        """Renders a list of components based on the identifier given.

        Args:
            view (ui.View): The raw view.
            callables (Dict[str, Callback]): The callbacks to use if the user interacts with the components.

        Returns (Optional[List[discord.ui.Item]]): The rendered components.
        """
        components = view.find("components")
        if components is None:
            return []
        return [
            self.render_component(
                component,
                callables.get(self.get_attribute(component, "key")),
            )
            for component in components
        ]
