import asyncio

import discord.ext
from response_manager import ResponseManager


import utils


class Menu:
    """Object that manages embed in a form of a menu."""

    def __init__(self, pages: list, ctx: discord.ext.commands.context = None,
                 client: discord.ext.commands.AutoShardedBot = None):
        """Initialisation method of the Menu object.
        Args:
            pages (dict): (str) name of the flow type that will map to its embed. -> (Embed) it's embed
            ctx (discord.ext.commands.context): context, required to display the menu. Defaults to None.
            client (discord.ext.commands.AutoShardedBot) : bot, required to control action (reactions). Defaults to None
        """
        self.__main = pages[0][0]
        self.__pages = dict(pages)
        self.__ctx = ctx
        self.__client = client
        self.__handler = ResponseManager(ctx, client, self.__pages)
        self.__reactions = {}
        self.__message = None
        self.__exit = False
        self.__debug = False
        self.__close = None

    def debug(self, mode: bool = True):
        self.__debug = mode
        print(f"*[HANDLER][DEBUG] MODE <- {mode}")

    def log(self, string):
        if self.__debug:
            print(string)

    def reload_handler(self):
        self.__handler = ResponseManager(self.__ctx, self.__client, self.__pages)

    def attach_context(self, ctx: discord.ext.commands.context):
        self.__ctx = ctx

    def get_context(self) -> discord.ext.commands.context:
        return self.__ctx

    def attach_client(self, client: discord.ext.commands.AutoShardedBot):
        self.__client = client

    def attach_function(self, reaction, function, *args):
        """Attaches a function to the reaction. The function will run if
           the reaction is triggered by the user.

        Args:
            reaction (emoji): unicode string of the emoji.
            function (function): function that is going to be attached to that emoji
            args (tuple): arguments that need to be run as the arguments of the function.
        """
        self.log(f'*[HANDLER][REACTION][ATTACH] {reaction} <- {function} <- {args}')
        self.__reactions[reaction] = (function, *args)
        self.log(f'*[HANDLER][REACTION][ATTACH] SUCCESS')

    def attach_closing(self, page, *args):
        self.__close = (Menu.change_page, self, page, *args)

    async def attach_numbers(self, obj=None):
        """makes the pages behave in a page form."""
        if len(self.__pages) == 1:
            return
        for page, i in zip(self.__pages.keys(), range(1, 10)):
            self.__reactions[utils.PAGES[i]] = (Menu.change_page, self, page, obj)

    def verify(self, reaction: discord.reaction.Reaction, user: discord.member.Member):
        """method that checks that the reaction is sent from the user.

        Args:
            reaction (discord.reaction.Reaction): Reaction object that is sent from discord
            user (discord.member.Member): Member object that contains user info. Sent from discord

        Returns:
            boolean: Flag that indicates whether it satisfies the verification function.
        """
        return user == self.__ctx.message.author

    async def attach_reactions(self, message):
        """Attach reactions

        Args:
            message (discord.message.Message): discord object representing a message.
        """
        for reaction in self.__reactions.keys():
            await message.add_reaction(reaction)

        await asyncio.sleep(2)

    async def hook_message(self, message):
        """Method that allows you to hook a message, instead of making a new message"""
        self.__handler.message = message
        await self.clear_reactions()

    def get_message(self):
        return self.__handler.message

    async def deploy_menu(self, obj=None):
        """This method deploys the menu into the ctx.channel and manages the menu."""

        await self.__handler.display(self.__main, obj)
        self.log(f"*[HANDLER][MENU] DEPLOYED")

        while not self.__exit:

            try:

                for i in self.__reactions.keys():
                    await self.__handler.message.add_reaction(i)

                self.log(f"*[HANDLER][RESPONSE] REACTIONS ATTACHED")
                reaction, user = await self.__client.wait_for('reaction_add', timeout=60.0, check=self.verify)
                self.log(f"*[HANDLER][REACTION] READ: {reaction}")

            except asyncio.futures.TimeoutError:

                self.log(f"*[HANDLER][MENU] TIMED OUT")
                self.__exit = True

            else:

                emoji = reaction.emoji
                self.log(f"*[HANDLER][CONVERSION] {emoji}")
                if str(emoji) in self.__reactions.keys():
                    func, *args = self.__reactions[str(emoji)]
                    self.log(f"*[HANDLER][MENU][FUNCTION_TRIGGER] {func} <- {args})")
                    await func(*args)
                else:
                    self.log(f"*[HANDLER][EMOJI] {emoji} NOT IN {self.__reactions.keys()}")
                await reaction.remove(user)

        await self.exit()

    async def clear_reactions(self):
        self.__ctx.message.clear_reactions()

    async def exit(self):
        """Method that exits the menu loop, and begins the closure function"""
        self.__exit = True
        if self.__close is None:
            return

        func, *args = self.__close
        self.log(f"*[HANDLER][MENU][FUNCTION_TRIGGER] {func} <- {args})")
        await func(*args)

    async def change_page(self, page, obj=None, *args):
        """Method that changes the embed on display

        Args:
            page (str): flow state that identifies the page embed in the page
            obj (object): obj that the page might require
        """
        self.log(f"*[HANDLER][PAGE] CHANGING -> {page}")
        await self.__handler.display(page, obj, *args)
        self.log(f"*[HANDLER][PAGE] CHANGED")

    async def get_input(self):
        """This method waits for a message to be sent by the user"""
        confirm = await self.__client.wait_for('message', timeout=60.0, check=self.verify)

        if confirm is not None:
            return confirm.content
        return None
