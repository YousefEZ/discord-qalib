from typing import Optional

from qalib.renderers.file_renderers.component_renderers.item import Item


class Button(Item):

    def __init__(self, item_id: Optional[str] = None, style: str = "secondary", label: str = None,
                 disabled: bool = False,
                 custom_id=None, url=None, emoji=None, row: int = None):
        super().__init__(item_id)
