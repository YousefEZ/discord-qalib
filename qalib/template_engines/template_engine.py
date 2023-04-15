from typing import Any, Dict, Protocol


class TemplateEngine(Protocol):
    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        """Method that is used to template a string using the template method.

        Args:
            document (str): string that is going to be templated upon
            keywords (Dict[str, Any]): keywords that are used to template the string

        Returns (str): templated string
        """
        raise NotImplementedError
