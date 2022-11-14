from qalib.renderers.file_renderers.renderer_factory import RendererFactory


class RendererProxy:

    def __init__(self, path):
        self._renderer = RendererFactory.get_renderer(path)

    def render(self, key, **kwargs):
        return self._renderer.render(key, **kwargs)

    def set_root_to(self, key):
        self._renderer.set_root_to(key)
