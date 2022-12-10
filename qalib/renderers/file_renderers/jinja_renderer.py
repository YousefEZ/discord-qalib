from typing import Any, Dict
from xml.etree import ElementTree as ElementTree

import jinja2

from ._xml_renderer import XMLRenderer


class JinjaXMLTemplate(XMLRenderer):

    def __init__(self, path: str, environment: jinja2.Environment, keywords: Dict[str, Any]):
        self._environment = environment
        super().__init__(ElementTree.fromstring(self._environment.get_template(path).render(**keywords)))

    @staticmethod
    def _render_element(element: ElementTree.Element, *_) -> str:
        if element is None:
            return ""
        return element.text

    @staticmethod
    def _render_attribute(element: ElementTree.Element, attribute: str, *_) -> str:
        if (value := element.get(attribute)) is None:
            return ""
        return value
