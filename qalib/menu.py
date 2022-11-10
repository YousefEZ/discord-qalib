import asyncio

import discord.ext

from qalib import DEBUG
from qalib.response_manager import ResponseManager
from qalib.utils import emojis
from qalib.xml_renderer import MenuRenderer


class Menu:
    """Object that manages embed in a form of a menu."""

    def __init__(self, embed_xml: str, menu_key: str, ctx: discord.ext.commands.context = None,
                 client: discord.ext.commands.AutoShardedBot = None):
        """Initialisation method of the Menu object.
        Args:
            embed_xml (str): the path to the xml file containing the Menu embed
            menu_key (str): the key of the menu in the xml file
            ctx (discord.ext.commands.context): context, required to display the menu. Defaults to None.
            client (discord.ext.commands.AutoShardedBot) : bot, required to control action (reactions). Defaults to None
        """
        self._renderer = MenuRenderer(embed_xml, menu_key)
        self._ctx = ctx
        self._client = client
        self._manager = ResponseManager(self._ctx, self._client, self._renderer)
        self._reactions = {}
        self._message = None
        self._exit = False
        self._debug = False
        self._close = None

    def log(self, string):
        if DEBUG:
            print(string)

    def attach_context(self, ctx: discord.ext.commands.context):
        self._ctx = ctx

    def get_context(self) -> discord.ext.commands.context:
        return self._ctx

    def attach_client(self, client: discord.ext.commands.AutoShardedBot):
        self._client = client

    def attach_function(self, reaction, function, *args):
        """Attaches a function to the reaction. The function will run if
           the reaction is triggered by the user.

        Args:
            reaction (emoji): unicode string of the emoji.
            function (function): function that is going to be attached to that emoji
            args (tuple): arguments that need to be run as the arguments of the function.
        """
        self.log(f'*[HANDLER][REACTION][ATTACH] {reaction} <- {function} <- {args}')
        self._reactions[reaction] = (function, *args)
        self.log(f'*[HANDLER][REACTION][ATTACH] SUCCESS')

    def attach_closing(self, page, *args):
        self._close = (Menu.change_page, self, page, *args)

    async def attach_numbers(self, *args, **kwargs):
        """makes the pages behave in a page form."""
        if self._renderer.number_of_pages == 1:
            return
        for page, i in zip(self._renderer.keys, range(1, 10)):
            self._reactions[emojis.PAGES[i]] = (Menu.change_page, self, page, args, kwargs)

    def verify(self, reaction: discord.reaction.Reaction, user: discord.member.Member):
        """method that checks that the reaction is sent from the user.

        Args:
            reaction (discord.reaction.Reaction): Reaction object that is sent from discord
            user (discord.member.Member): Member object that contains user info. Sent from discord

        Returns:
            boolean: Flag that indicates whether it satisfies the verification function.
        """
        return user == self._ctx.message.author

    async def attach_reactions(self, message):
        """Attach reactions

        Args:
            message (discord.message.Message): discord object representing a message.
        """
        for reaction in self._reactions.keys():
            await message.add_reaction(reaction)

        await asyncio.sleep(2)

    async def hook_message(self, message):
        """Method that allows you to hook a message, instead of making a new message"""
        self._manager.message = message
        await self.clear_reactions()

    def get_message(self):
        return self._manager.message

    async def deploy_menu(self, main: str, **kwargs):
        """This method deploys the menu into the ctx.channel and manages the menu.

        Args:
            main (str): flow state that identifies the page embed in the page
            **kwargs (dict): dictionary of arguments that are passed to the embed
        """

        await self._manager.display(main, **kwargs)
        self.log(f"*[HANDLER][MENU] DEPLOYED")

        while not self._exit:

            try:

                for i in self._reactions.keys():
                    await self._manager.message.add_reaction(i)

                self.log(f"*[HANDLER][RESPONSE] REACTIONS ATTACHED")
                reaction, user = await self._client.wait_for('reaction_add', timeout=60.0, check=self.verify)
                self.log(f"*[HANDLER][REACTION] READ: {reaction}")

            except asyncio.futures.TimeoutError:

                self.log(f"*[HANDLER][MENU] TIMED OUT")
                self._exit = True

            else:

                emoji = reaction.emoji
                self.log(f"*[HANDLER][CONVERSION] {emoji}")
                if str(emoji) in self._reactions.keys():
                    func, *args = self._reactions[str(emoji)]
                    self.log(f"*[HANDLER][MENU][FUNCTION_TRIGGER] {func} <- {args})")
                    await func(*args)
                else:
                    self.log(f"*[HANDLER][EMOJI] {emoji} NOT IN {self._reactions.keys()}")
                await reaction.remove(user)

        await self.exit()

    async def clear_reactions(self):
        self._ctx.message.clear_reactions()

    async def exit(self):
        """Method that exits the menu loop, and begins the closure function"""
        self._exit = True
        if self._close is None:
            return

        func, *args = self._close
        self.log(f"*[HANDLER][MENU][FUNCTION_TRIGGER] {func} <- {args})")
        await func(*args)

    async def change_page(self, page, **kwargs):
        """Method that changes the embed on display

        Args:
            page (str): flow state that identifies the page embed in the page
            **kwargs (dict): dictionary of arguments that are passed to the embed
        """
        self.log(f"*[HANDLER][PAGE] CHANGING -> {page}")
        await self._manager.display(page, **kwargs)
        self.log(f"*[HANDLER][PAGE] CHANGED")

    async def get_input(self):
        """This method waits for a message to be sent by the user"""
        confirm = await self._client.wait_for('message', timeout=60.0, check=self.verify)

        if confirm is not None:
            return confirm.content
        return None

    def __enter__(self):
        pass

    def __exit__(self):
        pass
