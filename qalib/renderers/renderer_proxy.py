from typing import List, Dict, Callable, Optional

from discord.ui import View
from discord.ui.item import Item

from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class RendererProxy:
    __slots__ = ("_renderer",)

    def __init__(self, path):
        self._renderer = RendererFactory.get_renderer(path)

    def render(self, key, **kwargs):
        return self._renderer.render(key, **kwargs)

    def render_view(
            self,
            identifier: str,
            callbacks: Optional[Dict[str, Callable]],
            timeout: Optional[int] = 180,
            **kwargs
    ) -> Optional[View]:

        if callbacks is None:
            callbacks = {}

        components: Optional[List[Item]] = self._renderer.render_components(identifier, callbacks, **kwargs)
        if components is None:
            return None

        view = View(timeout=timeout)
        for component in components:
            view.add_item(component)
        return view

    @property
    def size(self) -> int:
        return self._renderer.size

    @property
    def keys(self) -> List[str]:
        return self._renderer.keys
