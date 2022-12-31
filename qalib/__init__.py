"""
Extensions to the Rapptz Discord.py library, adding the use of templating on
embeds stored in the format of .xml files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""
from functools import wraps

import discord.ext.commands
import discord.ext.commands
import jinja2

from .qalib_context import QalibContext
from .renderers.embed_proxy import EmbedProxy
from .renderers.jinja_proxy import JinjaProxy
from .renderers.menu_proxy import MenuProxy
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
        proxy = EmbedProxy(*manager_args)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(QalibContext(args[0], proxy), *args[1:], **kwargs)

        return wrapper

    return manager


def menu_manager(*manager_args):
    def manager(func):
        proxy = MenuProxy(*manager_args)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(QalibContext(args[0], proxy), *args[1:], **kwargs)

        return wrapper

    return manager


def jinja_manager(*manager_args):
    def manager(func):
        proxy = JinjaProxy(*manager_args)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(QalibContext(args[0], proxy), *args[1:], **kwargs)

        return wrapper

    return manager
