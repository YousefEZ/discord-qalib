from typing import Any

from qalib import Renderer
from qalib.template_engines.formatter import Formatter
from qalib.translators.deserializer import ReturnType


def render_message(path: str, key: str, **kwargs: Any) -> ReturnType:
    renderer: Renderer[str] = Renderer(Formatter(), path)
    return renderer.render(key, keywords=kwargs)
