from typing import Any, Dict

import discord

from qalib import Renderer
from qalib.translators import Callback


class QalibInteraction(discord.Interaction):
    """The QalibInteraction class is a subclass of discord.Interaction, and is used to add additional functionality to
    the interaction. It is meant to be used in the on_interaction event, and is responsible for deserializing the
    requested modal and sending it to the user."""

    def __init__(self, interaction: discord.Interaction, renderer: Renderer):
        """Constructor method for the QalibInteraction class."""
        super().__init__(data=interaction.__dict__, state=interaction._state)
        self._renderer = renderer

    async def respond_with_modal(self, key: str, methods: Dict[str, Callback], keywords: Any) -> None:
        """Method that is responsible for templating the document, and then deserializing the requested modal based on
        its key and sending it to the user.

        Args:
            methods (Dict[str, Callback]): methods that are used to override the default methods of the modal
            key (str): key that identifies the modal in the route file
            keywords (Any): keywords that are passed to the modal renderer to format the text
        """
        return await self.response.send_modal(self._renderer.render_modal(key, methods, keywords))
