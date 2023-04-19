from typing import TYPE_CHECKING, Any, Dict, Generic, Optional, cast

import discord
from discord.interactions import InteractionResponse

from qalib.renderer import Renderer
from qalib.translators import Callback, Message
from qalib.translators.parser import K

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


class QalibInteraction(discord.Interaction, Generic[K]):
    """The QalibInteraction class is a subclass of discord.Interaction, and is used to add additional functionality to
    the interaction. It is meant to be used in the on_interaction event, and is responsible for deserializing the
    requested modal and sending it to the user."""

    def __init__(self, interaction: discord.Interaction, renderer: Renderer[K]):
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

    async def respond_with_modal(
            self,
            key: K,
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
        if methods is None:
            methods = {}

        if keywords is None:
            keywords = {}

        assert isinstance(self.response, InteractionResponse)  # pyright: ignore [reportGeneralTypeIssues]
        # pylint: disable= no-member
        modal = self._renderer.render_modal(key, methods, keywords)
        return await self.response.send_modal(modal)  # pyright: ignore [reportGeneralTypeIssues]

    def _render(
            self,
            identifier: K,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: int = 180,
    ) -> Message:
        """This method renders the embed and the view based on the identifier string given.

        Args:
            identifier (K): identifies the embed in the route file
            callables (Optional[Dict[str, Callback]]): item callbacks
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view

        Returns (Display): tuple of the embed and the view
        """
        return self._renderer.render(identifier, callables, keywords, timeout=timeout)

    async def rendered_send(
            self,
            identifier: K,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: int = 180,
            **kwargs,
    ) -> None:
        """Methods that is fires a message to the client and returns the message object. Doesn't save/keep track of the
        message.

        Args:
            identifier (str): identifies the embed in the route file
            callables (Optional[Dict[str, Callback]]) : functions that are hooked to components
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view
            **kwargs: kwargs that are passed to the context's send method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        message = self._render(identifier, callables, keywords, timeout)

        assert isinstance(self.response, InteractionResponse)  # pyright: ignore [reportGeneralTypeIssues]
        # pylint: disable= no-member
        message_info = {**message.convert_to_interaction_message().dict(), **kwargs}
        return await self.response.send_message(**message_info)  # pyright: ignore [reportGeneralTypeIssues]

    async def display(
            self,
            key: K,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: int = 180,
            **kwargs,
    ) -> None:
        """this is the main function that we use to send one message, and one message only. However, edits to that
        message can take place.

        Args:
            key (K): identifies the message in the template file
            callables: callable coroutines that are called when the user interacts with the message
            keywords: keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view
            **kwargs: kwargs that are passed to the context send method or the message edit method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        message = self._render(key, callables, keywords, timeout)
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

    async def menu(
            self,
            key: K,
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
        message = self._renderer.render_menu(key, callbacks=callbacks, keywords=keywords, **kwargs)
        await self._display(**{**message.convert_to_interaction_message().dict(), **kwargs})
