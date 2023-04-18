from typing import Any

from qalib import Renderer, Formatter
from qalib.translators import Message


def render_message(path: str, key: str, **kwargs: Any) -> Message:
    renderer: Renderer[str] = Renderer(Formatter(), path)
    message = renderer.render("Launch", keywords=kwargs)
    return message
