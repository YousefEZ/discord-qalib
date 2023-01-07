import string
from typing import Any, Dict

from qalib.template_engines.template_engine import TemplateEngine


class FormatPlaceholder:
    def __init__(self, key):
        self.key = key

    def __format__(self, spec):
        return f"{{{self.key}:{spec}}}" if spec else f"{{{self.key}}}"

    def __getitem__(self, index):
        self.key = "{}[{}]".format(self.key, index)
        return self

    def __getattr__(self, attr):
        self.key = "{}.{}".format(self.key, attr)
        return self


class FormatDict(dict):
    def __missing__(self, key):
        return FormatPlaceholder(key)


class Formatter(TemplateEngine):

    def template(self, document: str, keywords: Dict[str, Any]) -> str:
        formatter = string.Formatter()
        return formatter.vformat(document, (), FormatDict(keywords))
