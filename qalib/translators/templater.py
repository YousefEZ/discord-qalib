from __future__ import annotations

from typing import Any, Dict, Protocol

from qalib.template_engines.template_engine import TemplateEngine


class Templater(Protocol):
    """Protocol that represents the parser. It is meant to be placed into a Renderer, and is responsible for parsing the
    document into a menu and a list of callables."""

    def __init__(self, source: str):
        """This method is used to initialize the parser by parsing the source text.

        Args:
            source (str): source text that is parsed
        """
        raise NotImplementedError

    def template(self, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template the embed by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed in the form of string.
        """
        raise NotImplementedError
