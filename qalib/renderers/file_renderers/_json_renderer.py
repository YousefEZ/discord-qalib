from discord import Embed

from qalib.renderers.file_renderers.renderer import Renderer


class JSONRenderer(Renderer):

    def __init__(self, path: str):
        pass

    def render(self, identifier: str, **kwargs) -> Embed:
        raise NotImplementedError
