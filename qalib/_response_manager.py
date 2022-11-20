from typing import Any, Optional, Dict, Callable

import discord.message
import discord.ui as ui
import discord.ext.commands

from qalib.renderers.renderer_proxy import RendererProxy


class ResponseManager:
    """ResponseManager object is responsible for handling messages that are to be sent to the client.
       Data is stored in .xml files, where they are called and parsed. """

    def __init__(self, ctx: discord.ext.commands.context, renderer: RendererProxy):
        """Constructor for the ResponseManager object

        Args:
            ctx (commands.context): context object that is passed to the command
            renderer (RendererProxy): renderer object that is used to render the embeds and views
        """
        self._ctx: discord.ext.commands.context = ctx
        self._renderer: RendererProxy = renderer
        self.message: Optional[discord.message.Message] = None

    def verify(self, message: discord.message.Message) -> bool:
        """Method verifies if the content of the message is in the contents

        Args:
            message (discord.message.Message): message that is getting verified

        Returns:
            bool: true of false that indicates whether the data is valid.
        """
        return message.author == self._ctx.message.author and message.channel == self._ctx.message.channel

    async def get_message(self) -> Optional[str]:
        """This method waits for a message to be sent by the user"""
        confirm: Optional[discord.message.Message] = await self._ctx.bot.wait_for('message',
                                                                                  timeout=59.0,
                                                                                  check=self.verify)
        return confirm.content if confirm is not None else None

    def _render(
            self,
            identifier: str,
            callables: Optional[Dict[str, Callable]] = None,
            keywords: Dict[str, Any] = None,
            timeout: Optional[int] = 180
    ) -> (discord.Embed, Optional[ui.View]):
        """This method renders the embed and the view based on the identifier string given.

        Args:
            identifier (str): identifies the embed in the route file
            callables (Optional[Dict[str, Callable]]) : functions that are hooked to components
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view

        Returns (discord.Embed, Optional[ui.View]): tuple of the embed and the view
        """

        if callables is None:
            callables = {}

        if keywords is None:
            keywords = {}

        view: Optional[ui.View] = self._renderer.render_view(identifier, callables, timeout, keywords)
        embed: discord.Embed = self._renderer.render(identifier, keywords)
        return embed, view

    async def send(
            self,
            identifier: str,
            callables: Optional[Dict[str, Callable]] = None,
            keywords: Dict[str, Any] = None,
            timeout: Optional[int] = 180,
            **kwargs
    ) -> discord.message.Message:
        """Methods that is fires a message to the client and returns the message object.
        Doesn't save/keep track of the message.

        Args:
            identifier (str): identifies the embed in the route file
            callables (Optional[Dict[str, Callable]]) : functions that are hooked to components
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view
            **kwargs: kwargs that are passed to the context's send method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        if keywords is None:
            keywords = {}
        embed, view = self._render(identifier, callables, keywords, timeout)
        return await self._ctx.send(embed=embed, view=view, **kwargs)

    async def display(
            self,
            key: str,
            callables: Optional[Dict[str, Callable]] = None,
            keywords: Dict[str, Any] = None,
            **kwargs
    ) -> None:
        """this is the main function that we use to send one message, and one message only.
           However, edits to that message can take place.

        Args:
            key (str): identifies the embed in the route file
            callables: callable functions that are called when the user interacts with the message
            keywords: keywords that are passed to the embed renderer to format the text
            **kwargs: kwargs that are passed to the context send method or the message edit method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        if keywords is None:
            keywords = {}

        if self.message is None:
            self.message = await self.send(key, callables, keywords, **kwargs)
        else:
            embed, view = self._render(key, callables, keywords)
            await self.message.edit(embed=embed, view=view, **kwargs)
