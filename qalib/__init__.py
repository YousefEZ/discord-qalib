"""
Extensions to the Rapptz Discord.py library, adding the use of templating on
embeds stored in the format of .xml files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""
from functools import wraps
from typing import Optional

import discord.ext.commands
import discord.ext.commands
import jinja2

from .qalib_context import QalibContext
from .renderers.embed_proxy import EmbedProxy
from .renderers.jinja_proxy import JinjaProxy
from .utils import *

__title__ = 'qalib'
__author__ = 'YousefEZ'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022-present YousefEZ'
__version__ = '1.0.0'


class EmbedManager(QalibContext):

    def __init__(self, ctx: discord.ext.commands.Context, file_path: str, root: Optional[str] = None):
        super().__init__(ctx, EmbedProxy(file_path, root))


class JinjaManager(QalibContext):

    def __init__(
            self,
            ctx: discord.ext.commands.Context,
            environment: jinja2.Environment,
            template: str,
            root: Optional[str] = None
    ):
        super().__init__(ctx, JinjaProxy(environment, template, root))


def embed_manager(*manager_args):
    def manager(func):
        proxy = EmbedProxy(*manager_args)

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
