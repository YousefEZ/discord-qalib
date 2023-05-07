from typing import Any, Dict, Optional

from jinja2 import BaseLoader, Environment

from qalib.template_engines.template_engine import TemplateEngine


class Jinja2(TemplateEngine):

    def __init__(self, environment: Optional[Environment] = None):
        self._environment = environment or Environment(loader=BaseLoader(), autoescape=True)

    @property
    def environment(self) -> Environment:
        """This property is used to get the environment of the template engine.

        Returns (Environment): environment of the template engine
        """
        return self._environment

    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        """This method is used to format a string using the format method.

        Parameters:
            document (str): string that is formatted
            keywords (Dict[str, Any]): keywords that are used to format the string

        Returns (str): formatted string
        """
        return self._environment.from_string(document).render(**keywords)
