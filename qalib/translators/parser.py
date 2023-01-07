from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any

from qalib.template_engines.template_engine import TemplateEngine


class Parser(ABC):

    @abstractmethod
    def __init__(self, source: str):
        ...

    def template_embed(self, key: str, templater: TemplateEngine, keywords: Dict[str, Any]) -> str:
        ...

    def template_menu(self, key: str, templater: TemplateEngine, keywords: Dict[str, Any]) -> str:
        ...
