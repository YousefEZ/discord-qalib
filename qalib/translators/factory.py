from typing import Type, Optional

from .deserializer import Deserializer
from .json import JSONParser, JSONDeserializer
from .parser import Parser
from .xml import XMLParser, XMLDeserializer


class ParserFactory:
    """Factory class for creating renderers"""

    parsers = {".xml": XMLParser, ".json": JSONParser}

    @staticmethod
    def get_parser_type(path: str) -> Type[Parser]:
        for extension, parser_type in ParserFactory.parsers.items():
            if path.endswith(extension):
                return parser_type

        raise ValueError("No parser found for the given file")

    @staticmethod
    def get_parser(path: str, *, source: Optional[str] = None) -> Parser:
        """This function returns a parser for the file"""
        parser = ParserFactory.get_parser_type(path)
        if source is not None:
            return parser(source=source)
        with open(path, encoding="utf8", mode="r") as f:
            return parser(source=f.read())


class DeserializerFactory:
    deserializers = {".xml": XMLDeserializer, ".json": JSONDeserializer}

    @staticmethod
    def get_deserializer_type(path: str) -> Type[Deserializer]:
        """This function returns the correct translators for the given file.

        Args:
            path (str): path to the file

        Returns (Deserializer): th deserializer for the given file
        """
        for extension, deserializer_type in DeserializerFactory.deserializers.items():
            if path.endswith(extension):
                return deserializer_type

        raise ValueError("No deserializer found for the given file")

    @staticmethod
    def get_deserializer(path: str) -> Deserializer:
        return DeserializerFactory.get_deserializer_type(path)()
