from qalib.renderers.renderer_proxy import RendererProxy


class EmbedProxy(RendererProxy):
    """Renderer for embeds"""

    def __init__(self, path: str):
        super().__init__(path)
