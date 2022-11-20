from typing import Optional, Dict, Callable

import discord.message
import discord.ui as ui
from discord.ext import commands

from qalib.renderers.renderer_proxy import RendererProxy


class ResponseManager:
    """ResponseManager object is responsible for handling messages that are to be sent to the client.
       Data is stored in .xml files, where they are called and parsed. """

    def __init__(self, ctx: commands.context, renderer: RendererProxy):

        self._ctx: commands.context = ctx
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

    async def send(self, key: str, callables: Dict[str, Callable] = None, **kwargs) -> discord.message.Message:
        if callables is None:
            callables = {}
        view: Optional[ui.View] = self._renderer.render_view(key, callables, **kwargs)
        return await self._ctx.send(embed=self._renderer.render(key, **kwargs), view=view)

    async def display(self, key: str, **kwargs) -> None:
        """this is the main function that we use to send one message, and one message only.
           However, edits to that message can take place.

        Args:
            key (str): Unique identifier for the desired embed in the xml file
            **kwargs: arguments that are passed to the xml renderers to format the text

        """

        if self.message is None:
            self.message = await self.send(key, **kwargs)
        else:
            await self.message.edit(embed=self._renderer.render(key, **kwargs))
