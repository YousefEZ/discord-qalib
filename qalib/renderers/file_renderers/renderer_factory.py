from qalib.renderers.file_renderers._json_renderer import JSONRenderer
from qalib.renderers.file_renderers._xml_renderer import XMLRenderer
from qalib.renderers.file_renderers.renderer import Renderer


class RendererFactory:
    """Factory class for creating renderers"""

    @staticmethod
    def get_renderer(path: str) -> Renderer:
        if path.endswith(".xml"):
            return XMLRenderer(path)
        elif path.endswith(".json"):
            return JSONRenderer(path)

        raise ValueError("File type not supported")
