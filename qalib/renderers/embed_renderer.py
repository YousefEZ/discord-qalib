from discord import Embed

from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class EmbedRenderer:
    """Renderer for embeds"""

    def __init__(self, path: str):
        self._renderer = RendererFactory.get_renderer(path)

    def render(self, key: str, **kwargs) -> Embed:
        return self._renderer.render(key, **kwargs)
