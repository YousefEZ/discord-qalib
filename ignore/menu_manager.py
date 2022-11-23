import asyncio

import discord.ext

from qalib import DEBUG
from qalib._response_manager import ResponseManager
from qalib.renderers.menu_renderer import MenuRenderer
from qalib.utils import emojis


class Menu(ResponseManager):
    """Object that manages embed in a form of a menu."""

    def __init__(self, path: str, menu_key: str, ctx: discord.ext.commands.context):
        """Initialisation method of the Menu object.
        Args:
            path (str): the path to the containing the Menu embed
            menu_key (str): the key of the menu in the xml file
            ctx (discord.ext.commands.context): context, required to display the menu. Defaults to None.
        """
        super().__init__(MenuRenderer(path, menu_key), ctx)
        self._ctx = ctx
        self._ui_elements = {}
        self._message = None
        self._exit = False
        self._debug = False
        self._close = None

    def log(self, string):
        if DEBUG:
            print(string)

    def get_context(self) -> discord.ext.commands.context:
        return self._ctx

    def attach_function(self, interaction_id: str, function, *args):
        """Attaches a function to the reaction. The function will run if
           the reaction is triggered by the user.

        Args:
            interaction_id (str): the id of the UI element
            function (function): function that is going to be attached to that emoji
            args (tuple): arguments that need to be run as the arguments of the function.
        """
        self.log(f'*[HANDLER][REACTION][ATTACH] {interaction_id} <- {function} <- {args}')
        self._ui_elements[interaction_id] = (function, *args)
        self.log(f'*[HANDLER][REACTION][ATTACH] SUCCESS')

    def attach_closing(self, page, *args):
        self._close = (Menu.change_page, self, page, *args)

    async def attach_numbers(self, *args, **kwargs):
        """makes the pages behave in a page form."""
        if self._renderer.size == 1:
            return
        for page, i in zip(self._renderer.keys, range(1, 10)):
            self._ui_elements[emojis.PAGES[i]] = (Menu.change_page, self, page, args, kwargs)

    def reaction_verify(self, reaction: discord.reaction.Reaction, user: discord.member.Member):
        """method that checks that the reaction is sent from the user.

        Args:
            reaction (discord.reaction.Reaction): Reaction object that is sent from discord
            user (discord.member.Member): Member object that contains user info. Sent from discord

        Returns:
            boolean: Flag that indicates whether it satisfies the verification function.
        """
        return user == self._ctx.message.author and str(reaction.emoji) in self._ui_elements

    def get_message(self):
        return self.message

    def interaction_verify(self, interaction, user):
        return user == self._ctx.message.author and interaction.message.id == self.message.id

    async def deploy_menu(self, main: str, **kwargs):
        """This method deploys the menu into the ctx.channel and manages the menu.

        Args:
            main (str): flow state that identifies the page embed in the page
            **kwargs (dict): dictionary of arguments that are passed to the embed
        """

        await self.display(main, **kwargs)
        self.log(f"*[HANDLER][MENU] DEPLOYED")

        while not self._exit:

            try:

                for i in self._ui_elements.keys():
                    await self.message.add_reaction(i)

                self.log(f"*[HANDLER][RESPONSE] REACTIONS ATTACHED")
                reaction, user = await self._ctx.bot.wait_for('interaction', timeout=60.0,
                                                              check=self.interaction_verify)
                self.log(f"*[HANDLER][REACTION] READ: {reaction}")

            except asyncio.TimeoutError:

                self.log(f"*[HANDLER][MENU] TIMED OUT")
                self._exit = True

            else:

                emoji = reaction.emoji
                self.log(f"*[HANDLER][CONVERSION] {emoji}")
                if str(emoji) in self._ui_elements.keys():
                    func, *args = self._ui_elements[str(emoji)]
                    self.log(f"*[HANDLER][MENU][FUNCTION_TRIGGER] {func} <- {args})")
                    await func(*args)
                else:
                    self.log(f"*[HANDLER][EMOJI] {emoji} NOT IN {self._ui_elements.keys()}")
                await reaction.remove(user)

        await self.exit()

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
        await self.display(page, **kwargs)
        self.log(f"*[HANDLER][PAGE] CHANGED")
