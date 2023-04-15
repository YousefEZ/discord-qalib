"""
Extensions to the Rapptz Discord.py library, adding the use of templating on embeds stored in files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""
from __future__ import annotations

from typing import Any, Callable, Concatenate, Coroutine, ParamSpec, TypeVar, Union, cast, overload

import discord
import discord.ext.commands
from discord.ext.commands import Context

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

from .translators.parser import K

ContextT = TypeVar("ContextT", bound=Context[Any])
CogT = TypeVar("CogT", bound=discord.ext.commands.Cog)
T = TypeVar("T")
P = ParamSpec("P")
Coro = Coroutine[Any, Any, T]

PreWrappedContextFunction = Callable[Concatenate[QalibContext, P], Coro[T]]
PreWrappedContextMethod = Callable[Concatenate[CogT, QalibContext, P], Coro[T]]

PostWrappedContextFunction = Callable[Concatenate[ContextT, P], Coro[T]]
PostWrappedContextMethod = Callable[Concatenate[CogT, ContextT, P], Coro[T]]

PreWrappedInteractionFunction = Callable[Concatenate[QalibInteraction, P], Coro[T]]
PreWrappedInteractionMethod = Callable[Concatenate[CogT, QalibInteraction, P], Coro[T]]

PostWrappedInteractionFunction = Callable[Concatenate[discord.Interaction, P], Coro[T]]
PostWrappedInteractionMethod = Callable[Concatenate[CogT, discord.Interaction, P], Coro[T]]


def qalib_context(
    template_engine: TemplateEngine, filename: str, *renderer_options: RenderingOptions
) -> Union[
    Callable[[PreWrappedContextFunction[P, T]], PostWrappedContextFunction[ContextT, P, T]],
    Callable[
        [PreWrappedContextMethod[CogT, P, T]],
        PostWrappedContextMethod[CogT, ContextT, P, T],
    ],
]:
    """This decorator is used to create a QalibContext object, and pass it to the function as it's first argument,
    overriding the default context.

    Args:
        template_engine (TemplateEngine): template engine that is used to template the document
        filename (str): filename of the document
        renderer_options (RenderingOptions): options for the renderer

    Returns (QalibContext): decorated function that takes the Context object and using the extended QalibContext object
    """
    renderer_instance: Renderer[str] = Renderer(template_engine, filename, *renderer_options)

    @overload
    def command(func: PreWrappedContextFunction[P, T]) -> PostWrappedContextFunction[ContextT, P, T]:
        ...

    @overload
    def command(func: PreWrappedContextMethod[CogT, P, T]) -> PostWrappedContextMethod[CogT, ContextT, P, T]:
        ...

    def command(
        func: Union[PreWrappedContextFunction[P, T], PreWrappedContextMethod[CogT, P, T]]
    ) -> Union[PostWrappedContextFunction[ContextT, P, T], PostWrappedContextMethod[CogT, ContextT, P, T]]:
        if discord.utils.is_inside_class(func):

            async def method(self: CogT, ctx: ContextT, *args: P.args, **kwargs: P.kwargs) -> T:
                cog_method = cast(PreWrappedContextMethod[CogT, P, T], func)
                return await cog_method(self, QalibContext(ctx, renderer_instance), *args, **kwargs)

            return method

        async def function(ctx: ContextT, *args: P.args, **kwargs: P.kwargs) -> T:
            bot_command = cast(PreWrappedContextFunction[P, T], func)
            return await bot_command(QalibContext(ctx, renderer_instance), *args, **kwargs)

        return function

    return command


def qalib_interaction(
    template_engine: TemplateEngine, filename: str, *renderer_options: RenderingOptions
) -> Union[
    Callable[[PreWrappedInteractionFunction[P, T]], PostWrappedInteractionFunction[P, T]],
    Callable[[PreWrappedInteractionMethod[CogT, P, T]], PostWrappedInteractionMethod[CogT, P, T]],
]:
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

    @overload
    def command(func: PreWrappedInteractionFunction[P, T]) -> PostWrappedInteractionFunction[P, T]:
        ...

    @overload
    def command(func: PreWrappedInteractionMethod[CogT, P, T]) -> PostWrappedInteractionMethod[CogT, P, T]:
        ...

    def command(
        func: Union[PreWrappedInteractionFunction[P, T], PreWrappedInteractionMethod[CogT, P, T]]
    ) -> Union[PostWrappedInteractionFunction[P, T], PostWrappedInteractionMethod[CogT, P, T]]:
        if discord.utils.is_inside_class(func):

            async def method(
                self: CogT,
                inter: discord.Interaction,
                *args: P.args,
                **kwargs: P.kwargs,
            ) -> T:
                cog_method = cast(PreWrappedInteractionMethod[CogT, P, T], func)
                return await cog_method(self, QalibInteraction(inter, renderer_instance), *args, **kwargs)

            return method

        async def function(inter: discord.Interaction, *args: P.args, **kwargs: P.kwargs) -> T:
            bot_command = cast(PreWrappedInteractionFunction[P, T], func)
            return await bot_command(QalibInteraction(inter, renderer_instance), *args, **kwargs)

        return function

    return command
