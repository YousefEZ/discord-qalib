"""
Extensions to the Rapptz Discord.py library, adding the use of templating on
embeds stored in the format of .xml files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""

import discord.ext.commands
import discord.ext.commands
import jinja2

from .renderers.embed_proxy import EmbedProxy
from .renderers.jinja_proxy import JinjaProxy
from .renderers.menu_proxy import MenuProxy
from .qalib_context import QalibContext
from .utils import *

__title__ = 'qalib'
__author__ = 'YousefEZ'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022-present YousefEZ'
__version__ = '1.0.0'


class EmbedManager(QalibContext):

    def __init__(self, ctx: discord.ext.commands.Context, file_path: str):
        super().__init__(ctx, EmbedProxy(file_path))


class MenuManager(QalibContext):

    def __init__(self, ctx: discord.ext.commands.Context, file_path: str, menu_key: str):
        super().__init__(ctx, MenuProxy(file_path, menu_key))


class JinjaManager(QalibContext):

    def __init__(self, ctx: discord.ext.commands.Context, template: str, environment: jinja2.Environment):
        super().__init__(ctx, JinjaProxy(template, environment))


def embed_manager(*manager_args):
    def manager(func):
        def wrapper(*args, **kwargs):
            return func(EmbedManager(args[0], *manager_args), *args[1:], **kwargs)

        return wrapper

    return manager


def menu_manager(*manager_args):
    def manager(func):
        def wrapper(*args, **kwargs):
            return func(MenuManager(args[0], *manager_args), *args[1:], **kwargs)
        return wrapper
    return manager


def jinja_manager(*manager_args):
    def manager(func):
        def wrapper(*args, **kwargs):
            return func(JinjaManager(args[0], *manager_args), *args[1:], **kwargs)
        return wrapper
    return manager
