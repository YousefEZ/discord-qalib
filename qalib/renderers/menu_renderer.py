from typing import List

from discord import Embed

from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class MenuRenderer:

    def __init__(self, path: str, menu_key: str):
        self._renderer = RendererFactory.get_renderer(path)
        self._renderer.set_menu(menu_key)

    def render(self, key: str, **kwargs) -> Embed:
        return self._renderer.render(key, **kwargs)

    @property
    def number_of_pages(self) -> int:
        return self._renderer.size

    @property
    def keys(self) -> List[str]:
        return self._renderer.keys
