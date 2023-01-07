from typing import Protocol, Dict, Any


class TemplateEngine(Protocol):

    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        ...
