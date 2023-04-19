import string
from typing import Any, Dict

from qalib.template_engines.template_engine import TemplateEngine


class FormatPlaceholder:
    def __init__(self, key):
        self.key = key

    def __format__(self, spec):
        return f"{{{self.key}:{spec}}}" if spec else f"{{{self.key}}}"

    def __getitem__(self, index):
        self.key = f"{self.key}[{index}]"
        return self

    def __getattr__(self, attr):
        self.key = f"{self.key}.{attr}"
        return self


class FormatDict(dict):
    """This class is used to format a string using the format method, and will use the FormatPlaceholder class to
    handle missing keys, so that if they do not raise a KeyError, and are not removed.
    """

    def __missing__(self, key):
        return FormatPlaceholder(key)


class Formatter(TemplateEngine):
    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        """This method is used to format a string using the format method.

        Parameters:
            document (str): string that is formatted
            keywords (Dict[str, Any]): keywords that are used to format the string

        Returns (str): formatted string
        """
        formatter = string.Formatter()
        return formatter.vformat(document, (), FormatDict(keywords))
