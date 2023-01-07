from typing import Any, Optional, Dict

import discord.ext.commands
import discord.message

from qalib.renderer import Renderer
from qalib.translators import Display, Callback


class QalibContext(discord.ext.commands.Context):
    """QalibContext object is responsible for handling messages that are to be sent to the client."""

    def __init__(self, ctx: discord.ext.commands.context, renderer: Renderer):
        """Constructor for the QalibContext object

        Parameters:
            ctx (commands.context): context object that is passed to the command
            renderer (RendererProxy): renderer object that is used to render the embeds and views
        """
        super().__init__(
            message=ctx.message,
            bot=ctx.bot,
            view=ctx.view,
            args=ctx.args,
            kwargs=ctx.kwargs,
            prefix=ctx.prefix,
            command=ctx.command,
            invoked_with=ctx.invoked_with,
            invoked_parents=ctx.invoked_parents,
            invoked_subcommand=ctx.invoked_subcommand,
            subcommand_passed=ctx.subcommand_passed,
            command_failed=ctx.command_failed,
            current_parameter=ctx.current_parameter,
            current_argument=ctx.current_argument,
            interaction=ctx.interaction
        )
        self._renderer = renderer
        self._displayed: Optional[discord.message.Message] = None

    def verify(self, message: discord.message.Message) -> bool:
        """Method verifies if the content of the message is in the contents

        Parameters:
            message (discord.message.Message): message that is getting verified

        Returns:
            bool: true of false that indicates whether the data is valid.
        """
        return message.author == self.message.author and message.channel == self.message.channel

    async def get_message(self) -> Optional[str]:
        """This method waits for a message to be sent by the user"""
        confirm: Optional[discord.message.Message] = await self.bot.wait_for('message',
                                                                             timeout=59.0,
                                                                             check=self.verify)
        return confirm.content if confirm is not None else None

    def _render(
            self,
            identifier: str,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180
    ) -> Display:
        """This method renders the embed and the view based on the identifier string given.

        Parameters:
            identifier (str): identifies the embed in the route file
            callables (Optional[Dict[str, Callback]]): item callbacks
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view

        Returns (Display): tuple of the embed and the view
        """
        return self._renderer.render(identifier, callables, keywords, timeout=timeout)

    async def rendered_send(
            self,
            identifier: str,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180,
            **kwargs
    ) -> discord.message.Message:
        """Methods that is fires a message to the client and returns the message object. Doesn't save/keep track of the
        message.

        Parameters:
            identifier (str): identifies the embed in the route file
            callables (Optional[Dict[str, Callback]]) : functions that are hooked to components
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view
            **kwargs: kwargs that are passed to the context's send method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        embed, view = self._render(identifier, callables, keywords, timeout)
        return await self.send(embed=embed, view=view, **kwargs)

    async def display(
            self,
            key: str,
            callables: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            timeout: Optional[int] = 180,
            **kwargs
    ) -> None:
        """this is the main function that we use to send one message, and one message only. However, edits to that
        message can take place.

        Parameters:
            key (str): identifies the embed in the route file
            callables: callable coroutines that are called when the user interacts with the message
            keywords: keywords that are passed to the embed renderer to format the text
            timeout (Optional[int]): timeout for the view
            **kwargs: kwargs that are passed to the context send method or the message edit method

        Returns (discord.message.Message): Message object that got sent to the client.
        """
        embed, view = self._render(key, callables, keywords, timeout)
        await self._display(embed=embed, view=view, **kwargs)

    async def _display(self, **kwargs: Any) -> None:
        """This method is responsible for sending the message to the client and keeping track of the message object.

        Parameters:
            **kwargs (Dict[str, Any]): kwargs that are passed to the context's send method
        """
        if self._displayed is None:
            self._displayed = await self.send(**kwargs)
        else:
            await self._displayed.edit(**kwargs)

    async def menu(
            self,
            key: str,
            callbacks: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
            **kwargs
    ) -> None:
        """This method is used to create a menu for the user to select from.

        Parameters:
            key (str): identifies the menu in the template file
            callbacks (Dict[str, Callback]): callbacks that are called when the user interacts with the menu
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text
            **kwargs: kwargs that are passed to the context's send method
        """
        display = self._renderer.render_menu(key, callbacks=callbacks, keywords=keywords, **kwargs)
        await self._display(embed=display.embed, view=display.view, **kwargs)
