from typing import Optional

from qalib.renderers.renderer_proxy import RendererProxy


class EmbedProxy(RendererProxy):
    """Renderer for embeds"""

    def __init__(self, path: str, root: Optional[str] = None):
        super().__init__(path, root)
