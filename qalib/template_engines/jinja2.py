from typing import Any, Dict

from jinja2 import BaseLoader, Environment

from qalib.template_engines.template_engine import TemplateEngine


class Jinja2(TemplateEngine):
    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        """This method is used to format a string using the format method.

        Parameters:
            document (str): string that is formatted
            keywords (Dict[str, Any]): keywords that are used to format the string

        Returns (str): formatted string
        """
        return Environment(loader=BaseLoader()).from_string(document).render(**keywords)
