"""
Extensions to the Rapptz Discord.py library, adding the use of templating on
embeds stored in the format of .xml files.

:copyright: (c) 2022-present YousefEZ
:license: MIT, see LICENSE for more details.
"""
from functools import wraps
from typing import Optional

from .qalib_context import QalibContext

__title__ = 'qalib'
__author__ = 'YousefEZ'
__license__ = 'MIT'
__copyright__ = 'Copyright 2022-present YousefEZ'
__version__ = '1.0.0'

from .renderer import Renderer, RenderingOptions
from .template_engines.formatter import Formatter
from .template_engines.jinja2 import Jinja2
from .template_engines.template_engine import TemplateEngine


def qalib_context(template_engine: TemplateEngine, filename: str, renderer_options: Optional[RenderingOptions] = None):
    def manager(func):
        renderer_instance = Renderer(template_engine, filename, renderer_options)

        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(QalibContext(args[0], renderer_instance), *args[1:], **kwargs)

        return wrapper

    return manager
