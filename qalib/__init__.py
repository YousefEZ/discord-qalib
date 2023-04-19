"""
Extensions to the Rapptz Discord.py library, adding the use of templating on embeds stored in files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar, Coroutine

import discord
from discord.ext import commands

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
__version__ = "2.1.0"

T = TypeVar("T")
Coro = Coroutine[Any, Any, T]


def qalib_context(
    template_engine: TemplateEngine, filename: str, *renderer_options: RenderingOptions
) -> Callable[[Callable[..., Coro[T]]], Callable[..., Coro[T]]]:
    """This decorator is used to create a QalibContext object, and pass it to the function as it's first argument,
    overriding the default context.

    Args:
        template_engine (TemplateEngine): template engine that is used to template the document
        filename (str): filename of the document
        renderer_options (RenderingOptions): options for the renderer

    Returns (QalibContext): decorated function that takes the Context object and using the extended QalibContext object
    """
    renderer_instance: Renderer[str] = Renderer(template_engine, filename, *renderer_options)

    def command(func: Callable[..., Coro[T]]) -> Callable[..., Coro[T]]:
        if discord.utils.is_inside_class(func):

            @wraps(func)
            async def method(self: commands.Cog, ctx: commands.Context, *args: Any, **kwargs: Any) -> T:
                return await func(self, QalibContext(ctx, renderer_instance), *args, **kwargs)

            return method

        @wraps(func)
        async def function(ctx: commands.Context, *args: Any, **kwargs: Any) -> T:
            return await func(QalibContext(ctx, renderer_instance), *args, **kwargs)

        return function

    return command


def qalib_interaction(
    template_engine: TemplateEngine, filename: str, *renderer_options: RenderingOptions
) -> Callable[[Callable[..., Coro[T]]], Callable[..., Coro[T]]]:
    """This decorator is used to create a QalibInteraction object, and pass it to the function as it's first argument,
    overriding the default interaction.

    Args:
        template_engine (TemplateEngine): template engine that is used to template the document
        filename (str): filename of the document
        renderer_options (RenderingOptions): options for the renderer

    Returns (Callable): decorated function that takes the Interaction object and using the extended
    QalibInteraction object
    """
    renderer_instance: Renderer[str] = Renderer(template_engine, filename, *renderer_options)

    def command(func: Callable[..., Coro[T]]) -> Callable[..., Coro[T]]:
        if discord.utils.is_inside_class(func):

            @wraps(func)
            async def method(
                self: commands.Cog,
                inter: discord.Interaction,
                *args: Any,
                **kwargs: Any,
            ) -> T:
                return await func(self, QalibInteraction(inter, renderer_instance), *args, **kwargs)

            return method

        @wraps(func)
        async def function(inter: discord.Interaction, *args: Any, **kwargs: Any) -> T:
            return await func(QalibInteraction(inter, renderer_instance), *args, **kwargs)

        return function

    return command
