from typing import Dict, Any

from jinja2 import Environment, BaseLoader

from qalib.template_engines.template_engine import TemplateEngine


class Jinja2(TemplateEngine):

    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        return Environment(loader=BaseLoader()).from_string(document).render(**keywords)
