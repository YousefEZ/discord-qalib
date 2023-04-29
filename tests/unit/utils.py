from typing import Any

from qalib import Renderer, Formatter
from qalib.translators.deserializer import ReturnType


def render_message(path: str, key: str, **kwargs: Any) -> ReturnType:
    renderer: Renderer[str] = Renderer(Formatter(), path)
    return renderer.render(key, keywords=kwargs)
