from typing import List, Dict, Callable

from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class RendererProxy:

    def __init__(self, path):
        self._renderer = RendererFactory.get_renderer(path)

    def render(self, key, **kwargs):
        return self._renderer.render(key, **kwargs)

    def render_components(self, key, callables: Dict[str, Callable], **kwargs):
        return self._renderer.render_components(key, callables, **kwargs)

    @property
    def size(self) -> int:
        return self._renderer.size

    @property
    def keys(self) -> List[str]:
        return self._renderer.keys
