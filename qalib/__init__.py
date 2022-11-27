"""
Extensions to the Rapptz Discord.py library, adding the use of templating on
embeds stored in the format of .xml files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""

__title__ = 'qalib'
__author__ = 'YousefEZ'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022-present YousefEZ'
__version__ = '1.0.0'

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import discord.ext.commands

DEBUG = False

from .embed_manager import *
from .utils import *

import discord.ext.commands


def embed_manager(path):
    def embed_manager(func):
        def wrapper(*args, **kwargs):
            assert type(args[0]) is discord.ext.commands.Context
            return func(EmbedManager(args[0], path), *args[1:], **kwargs)

        return wrapper

    return embed_manager
