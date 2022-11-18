from typing import List, Dict, Callable, Optional

from qalib.renderers.file_renderers.renderer_factory import RendererFactory

from discord.ui.item import Item
from discord.ui import View


class RendererProxy:

    def __init__(self, path):
        self._renderer = RendererFactory.get_renderer(path)

    def render(self, key, **kwargs):
        return self._renderer.render(key, **kwargs)

    def render_view(self, key, callables: Optional[Dict[str, Callable]], **kwargs) -> View:
        if callables is None:
            callables = {}
        components: Optional[List[Item]] = self._renderer.render_components(key, callables, **kwargs)
        view = View()
        for component in components:
            component.callback = callables.get(component.key)
            view.add_item(component)
        return view

    @property
    def size(self) -> int:
        return self._renderer.size

    @property
    def keys(self) -> List[str]:
        return self._renderer.keys
