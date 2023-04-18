from qalib import Renderer, Formatter
from qalib.translators import Message


def render_message(path: str) -> Message:
    renderer: Renderer[str] = Renderer(Formatter(), path)
    message = renderer.render("Launch")
    return message
