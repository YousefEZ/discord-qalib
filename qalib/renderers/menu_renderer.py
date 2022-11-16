from discord import Embed

from qalib.renderers.renderer_proxy import RendererProxy


class MenuRenderer(RendererProxy):

    def __init__(self, path: str, menu_key: str):
        super().__init__(path)
        self._renderer.set_menu(menu_key)

    def render(self, key: str, **kwargs) -> Embed:
        return self._renderer.render(key, **kwargs)
