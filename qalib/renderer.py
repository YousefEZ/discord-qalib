from __future__ import annotations

from enum import Enum, auto
from typing import Any, Dict, Generic, Optional, cast

from qalib.template_engines.template_engine import TemplateEngine
from qalib.translators import Callback
from qalib.translators.deserializer import ReturnType, K_contra, Deserializer
from qalib.translators.factory import DeserializerFactory, TemplaterFactory
from qalib.translators.templater import Templater


class RenderingOptions(Enum):
    """Options for the renderer."""

    PRE_TEMPLATE = auto()


class Renderer(Generic[K_contra]):
    """This object is responsible for rendering the embeds, views, and menus, by first using the templating engine to
    template the document, and then using the deserializer to deserialize the document into embeds and views.
    """

    __slots__ = "_template_engine", "_parser", "_filename", "_deserializer"

    def __init__(self, template_engine: TemplateEngine, filename: str, *rendering_options: RenderingOptions):
        self._template_engine = template_engine
        self._parser: Optional[Templater] = None
        if RenderingOptions.PRE_TEMPLATE not in rendering_options:
            self._parser = TemplaterFactory.get_templater(filename)
        self._filename = filename
        self._deserializer = cast(Deserializer[K_contra], DeserializerFactory.get_deserializer(filename))

    def _pre_template(self, keywords: Dict[str, Any]) -> Templater:
        """Pre-Template templates the document before further processing. It returns a Parser instance that contains
        the data that is used to render the embeds and views.

        Args:
            keywords (Dict[str, Any]): keywords that are passed to the templating engine to template the document.

        Returns (Parser): Parser instance that contains the data that is used to render the embeds and views.
        """
        if self._parser is None:
            with open(self._filename, "r", encoding="utf-8") as file:
                return TemplaterFactory.get_templater(
                    self._filename,
                    source=self._template_engine.template(file.read(), keywords),
                )
        return self._parser

    def render(
            self,
            key: K_contra,
            callbacks: Optional[Dict[str, Callback]] = None,
            keywords: Optional[Dict[str, Any]] = None,
    ) -> ReturnType:
        """This method is used to render an embed and a view, and places it in a NamedTuple

        Args:
            key (K): key of the embed,
            callbacks (Optional[Dict[str, Callable]]): callbacks that are attached to the components of the view,
            keywords (Dict[str, Any]): keywords that are passed to the embed renderer to format the text,

        Returns (ReturnType): All possible deserialized types
        """
        if callbacks is None:
            callbacks = {}

        if keywords is None:
            keywords = {}

        source = self._pre_template(keywords).template(self._template_engine, keywords)
        return self._deserializer.deserialize(source, key, callbacks)
