from qalib.renderers.renderer_proxy import RendererProxy


class EmbedRenderer(RendererProxy):
    """Renderer for embeds"""

    def __init__(self, path: str):
        super().__init__(path)
