from discord.ext import commands

from qalib.renderers.file_renderers._xml_renderer import XMLRenderer


class ResponseManager:
    """ResponseManager object is responsible for handling messages that are to be sent to the client.
       Data is stored in .xml files, where they are called and parsed. """

    def __init__(self, ctx: commands.context, renderer: XMLRenderer):

        self._ctx = ctx
        self._renderer = renderer
        self.message = None

    def verify(self, message):
        """Method verifies if the content of the message is in the contents

        Args:
            message (discord.message.Message): message that is getting verified

        Returns:
            bool: true of false that indicates whether the data is valid.
        """

        return message.author == self._ctx.message.author and message.channel == self._ctx.message.channel

    async def get_message(self):
        """This method waits for a message to be sent by the user"""

        confirm = await self._ctx.bot.wait_for('message', timeout=59.0, check=self.verify)
        return confirm.content if confirm is not None else None

    async def send(self, key: str, **kwargs):
        return await self._ctx.send(embed=self._renderer.render(key, **kwargs))

    async def display(self, key: str, **kwargs):
        """this is the main function that we use to send one message, and one message only.
           However edits to that message can take place.

        Args:
            key (str): Unique identifier for the desired embed in the xml file
            **kwargs: arguments that are passed to the xml renderers to format the text

        """

        if self.message is None:
            self.message = await self.send(key, **kwargs)
        else:
            await self.message.edit(embed=self._renderer.render(key, **kwargs))
