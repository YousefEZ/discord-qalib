from qalib.renderers.file_renderers.renderer_factory import RendererFactory
from qalib.renderers.renderer_proxy import RendererProxy


class MenuProxy(RendererProxy):

    def __init__(self, path: str, menu_key: str):
        super().__init__(path)
        self._renderer.set_menu(menu_key)
