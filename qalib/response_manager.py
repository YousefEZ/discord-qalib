from discord.ext import commands

from qalib.xml_renderer import Renderer


class ResponseManager:
    """ResponseManager object is responsible for handling messages that are to be sent to the client.
       Data is stored in .ini files, where they are called and parsed. """

    def __init__(self, ctx: commands.context, bot: commands.AutoShardedBot,
                 xml_path: str):

        self.__ctx = ctx
        self.__bot = bot
        self.__renderer = Renderer(xml_path)
        self.__pages = {}
        self.message = None

    def verify(self, message):
        """Method verifies if the content of the message is in the contents

        Args:
            message (discord.message.Message): message that is getting verified

        Returns:
            bool: true of false that indicates whether the data is valid.
        """

        return message.author == self.__ctx.message.author and message.channel == self.__ctx.message.channel

    async def get_message(self):
        """This method waits for a message to be sent by the user"""

        confirm = await self.__bot.wait_for('message', timeout=59.0, check=self.verify)

        if confirm is not None:
            return confirm.content
        return None

    async def send(self, key: str, **kwargs):
        return await self.__ctx.send(embed=self.__renderer.render(key, **kwargs))

    async def display(self, key: str, **kwargs):
        """this is the main function that we use to send one message, and one message only.
           However edits to that message can take place.

        Args:
            key (str): Unique identifier for the desired embed in the xml file
            **kwargs: arguments that are passed to the xml renderer to format the text

        """

        if self.message is None:
            self.message = await self.send(key, **kwargs)
        else:
            await self.message.edit(embed=self.__renderer.render(key, **kwargs))

    def retrieve_menu(self, flow_type: str):
        """Method that gets the menu specified

        Args:
            flow_type (str): string that labels the flow

        Returns:
        Menu : Object that contains the menu
        """

        pointer = self.__pages[flow_type].pointer
        menu = [(flow_type, self.__pages[flow_type])]

        while pointer is not None:
            # gets all the pages in the menu.
            menu.append((pointer.flow, pointer))
            pointer = pointer.pointer

        return Menu(menu, self.__ctx, self.__bot)
