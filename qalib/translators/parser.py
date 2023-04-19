from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar

from qalib.template_engines.template_engine import TemplateEngine

K = TypeVar("K", bound=str, contravariant=True)


class Parser(ABC, Generic[K]):
    """Protocol that represents the parser. It is meant to be placed into a Renderer, and is responsible for parsing the
    document into a menu and a list of callables."""

    @abstractmethod
    def __init__(self, source: str):
        """This method is used to initialize the parser by parsing the source text.

        Args:
            source (str): source text that is parsed
        """
        raise NotImplementedError

    @abstractmethod
    def template_message(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """This method is used to template the embed by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (str): key of the embed
            template_engine (TemplateEngine): template engine that is used to template the embed
            keywords (Dict[str, Any]): keywords that are used to template the embed

        Returns (str): templated embed in the form of string.
        """
        raise NotImplementedError

    @abstractmethod
    def template_menu(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """Method that is used to template the menu by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (str): key of the menu
            template_engine (TemplateEngine): template engine that is used to template the menu
            keywords (Dict[str, Any]): keywords that are used to template the menu

        Returns (str): templated menu in the form of string.
        """
        raise NotImplementedError

    @abstractmethod
    def template_modal(self, key: K, template_engine: TemplateEngine, keywords: Dict[str, Any]) -> str:
        """Method that is used to template the modal by first retrieving it using its key, and then templating it using
        the template_engine

        Args:
            key (str): key of the modal
            template_engine (TemplateEngine): template engine that is used to template the modal
            keywords (Dict[str, Any]): keywords that are used to template the modal

        Returns (str): templated modal in the form of string.
        """
        raise NotImplementedError
