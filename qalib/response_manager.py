import discord.ext
from discord import Embed

import utils
from menu import Menu


class ResponseManager:
    """ResponseManager object is responsible for handling messages that are to be sent to the client.
       Data is stored in .ini files, where they are called and parsed. """

    def __init__(self, ctx: discord.ext.commands.context, bot: discord.ext.commands.AutoShardedBot,
                 pages: dict):

        self.__ctx = ctx
        self.__bot = bot
        self.__pages = pages
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

    async def send(self, flow: str, obj, *args):
        return await self.__ctx.send(embed=self.retrieve_embed(flow, obj, *args))

    async def display(self, flow, obj=None, *args):
        """this is the main function that we use to send one message, and one message only.
           However edits to that message can take place.

        Args:
            flow (str): name of the flow key.
            obj (Object): an instance/object containing data that is used for the response. Defaults to None
        """

        if self.message is None:
            self.message = await self.send(flow, obj, *args)
        else:
            await self.message.edit(embed=self.retrieve_embed(flow, obj, *args))

    def retrieve_embed(self, flow_type, obj=None, *args):
        """Reads the contents of the section in the .ini file, and
        creates an embed with that data.

        Args:
            flow_type (str): Name of the section in the .ini state
            obj (Object): an instance/object containing data that is used for the response. Defaults to None

        Returns:
            Embed: Embed Object, discord compatible.
        """
        flow = self.__pages[flow_type](obj, *args)

        colour = utils.get_colour(flow.colour)
        embed = Embed(title=flow.title, colour=colour)
        fields = flow.fields
        if type(fields[-1]) != tuple:
            fields = (fields,)

        for field in fields:
            if len(field) == 1:
                embed.add_field(name=field[-1], value=field[1].replace('\t', ''), inline=True)
            else:
                embed.add_field(name=field[-1], value=field[1].replace('\t', ''), inline=field[2])

        embed.set_footer(text=flow.footer_text, icon_url=flow.footer_icon)
        embed.set_thumbnail(url=flow.thumbnail)
        embed.set_image(url=flow.image)

        return embed

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
