"""
Extensions to the Rapptz Discord.py library, adding the use of templating on embeds stored in files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""
from functools import wraps
from typing import Any

import discord
import discord.ext.commands

from .context import QalibContext
from .interaction import QalibInteraction
from .renderer import Renderer, RenderingOptions
from .template_engines.formatter import Formatter
from .template_engines.jinja2 import Jinja2
from .template_engines.template_engine import TemplateEngine

__title__ = "qalib"
__author__ = "YousefEZ"
__license__ = "MIT"
__copyright__ = "Copyright 2022-present YousefEZ"
__version__ = "2.0.0"


def qalib_context(template_engine: TemplateEngine, filename: str, *renderer_options: RenderingOptions):
    """This decorator is used to create a QalibContext object, and pass it to the function as it's first argument,
    overriding the default context.

    Args:
        template_engine (TemplateEngine): template engine that is used to template the document
        filename (str): filename of the document
        renderer_options (RenderingOptions): options for the renderer

    Returns (QalibContext): decorated function that takes the Context object and using the extended QalibContext object
    """
    renderer_instance = Renderer(template_engine, filename, *renderer_options)

    def command(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            arguments = list(args)
            for i, argument in enumerate(arguments):
                if isinstance(argument, discord.ext.commands.Context):
                    arguments[i] = QalibContext(argument, renderer_instance)
                    break
            else:
                raise TypeError("Interaction object not found in arguments")

            return await func(*arguments, **kwargs)

        return wrapper

    return command


def qalib_interaction(template_engine: TemplateEngine, filename: str, *renderer_options: RenderingOptions):
    """This decorator is used to create a QalibInteraction object, and pass it to the function as it's first argument,
    overriding the default interaction.

    Args:
        template_engine (TemplateEngine): template engine that is used to template the document
        filename (str): filename of the document
        renderer_options (RenderingOptions): options for the renderer

    Returns (Callable): decorated function that takes the Interaction object and using the extended
    QalibInteraction object
    """
    renderer_instance = Renderer(template_engine, filename, *renderer_options)

    def command(func):
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            """Wrapper function that intercepts the interaction object and replaces it with the extended
            QalibInteraction."""
            arguments = list(args)
            for i, argument in enumerate(arguments):
                if isinstance(argument, discord.Interaction):
                    arguments[i] = QalibInteraction(argument, renderer_instance)
                    break
            else:
                raise TypeError("Interaction object not found in arguments")

            return await func(*arguments, **kwargs)

        return wrapper

    return command
