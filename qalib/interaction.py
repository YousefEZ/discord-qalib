import warnings
from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, cast

import discord
from deprecated import deprecated
from discord.interactions import InteractionResponse
from discord.ui import Modal

from qalib.renderer import Renderer
from qalib.translators import Callback, Message
from qalib.translators.deserializer import K_contra

if TYPE_CHECKING:
    from discord.types.interactions import Interaction as InteractionPayload


def create_interaction_payload(interaction: discord.Interaction) -> Dict[str, Any]:
    # pylint: disable=protected-access
    # noinspection PyProtectedMember
    return {
        "id": interaction.id,
        "type": int(interaction.type.value),
        "data": interaction.data,
        "token": interaction.token,
        "version": interaction.version,
        "channel_id": interaction.channel_id,
        "guild_id": interaction.guild_id,
        "application_id": interaction.application_id,
        "locale": interaction.locale,
        "guild_locale": interaction.guild_locale,
        "app_permissions": interaction._app_permissions,
    }


class QalibInteraction(discord.Interaction, Generic[K_contra]):
    """The QalibInteraction class is a subclass of discord.Interaction, and is used to add additional functionality to
    the interaction. It is meant to be used in the on_interaction event, and is responsible for deserializing the
    requested modal and sending it to the user."""

    def __init__(self, interaction: discord.Interaction, renderer: Renderer[K_contra]):
        """Constructor method for the QalibInteraction class."""
        data = create_interaction_payload(interaction)
        if TYPE_CHECKING:
            super().__init__(
                data=(cast(InteractionPayload, data)),
                state=interaction._state,
            )
        else:
            super().__init__(
                data=data,
                state=interaction._state,
            )
        self.message = interaction.message
        self.user = interaction.user
        self._renderer = renderer
        self._displayed = False

    async def rendered_send(
            self,
            identifier: K_contra,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            **kwargs,
    ) -> None:
        """Methods that is fires a message to the client and returns the message object. Doesn't save/keep track of the
        message.

        Args:
            identifier (str): identifies the embed in the route file
            callables (Optional[Dict[str, Callback]]) : functions that are hooked to components
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            **kwargs: kwargs that are passed to the context's send method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        message = self._renderer.render(identifier, callables, keywords)
        if isinstance(message, Message):
            assert isinstance(self.response, InteractionResponse)  # pyright: ignore [reportGeneralTypeIssues]
            # pylint: disable= no-member
            message_info = {**message.convert_to_interaction_message().dict(), **kwargs}
            return await self.response.send_message(**message_info)  # pyright: ignore [reportGeneralTypeIssues]
        if isinstance(message, Modal):
            assert isinstance(self.response, InteractionResponse)  # pyright: ignore [reportGeneralTypeIssues]
            # pylint: disable= no-member
            return await self.response.send_modal(message)  # pyright: ignore [reportGeneralTypeIssues]

    async def display(
            self,
            key: K_contra,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            **kwargs,
    ) -> None:
        """this is the main function that we use to send one message, and one message only. However, edits to that
        message can take place.

        Args:
            key (K): identifies the message in the template file
            callables: callable coroutines that are called when the user interacts with the message
            keywords: keywords that are passed to the embed renderer to format the text
            **kwargs: kwargs that are passed to the context send method or the message edit method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        message = self._renderer.render(key, callables, keywords)
        assert isinstance(message, Message)
        if self._displayed:
            await self._display(**{**message.convert_to_interaction_message().as_edit().dict(), **kwargs})
            return
        await self._display(**{**message.convert_to_interaction_message().dict(), **kwargs})

    async def _display(self, **kwargs: Any) -> None:
        """This method is responsible for sending the message to the client, and editing the message if there is one
        that has already been sent.

        Args:
            **kwargs (Dict[str, Any]): kwargs that are passed to the context's send method
        """
        if self._displayed:
            await self.edit_original_response(**kwargs)
        else:
            assert isinstance(self.response, InteractionResponse)  # pyright: ignore [reportGeneralTypeIssues]
            # pylint: disable= no-member
            await self.response.send_message(**kwargs)  # pyright: ignore [reportGeneralTypeIssues]
            self._displayed = True

    @deprecated(version="2.1.2", reason="Use rendered_send method instead")
    async def menu(
            self,
            key: K_contra,
            callbacks: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            **kwargs,
    ) -> None:
        """This method is used to create a menu for the user to select from.

        Args:
            key (K): identifies the menu in the template file
            callbacks (Dict[str, Callback]): callbacks that are called when the user interacts with the menu
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            **kwargs: kwargs that are passed to the context's send method
        """
        warnings.warn("Use rendered_send method instead", DeprecationWarning)
        await self.rendered_send(key, callbacks, keywords, **kwargs)

    @deprecated(version="2.1.2", reason="Use rendered_send method instead")
    async def respond_with_modal(
            self,
            key: K_contra,
            methods: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Method that is responsible for templating the document, and then deserializing the requested modal based on
        its key and sending it to the user.

        Args:
            methods (Dict[str, Callback]): methods that are used to override the default methods of the modal
            key (str): key that identifies the modal in the route file
            keywords (Any): keywords that are passed to the modal renderer to format the text
        """
        warnings.warn("Use rendered_send method instead", DeprecationWarning)
        await self.rendered_send(key, methods, keywords)
