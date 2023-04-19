from typing import Any, Optional, Type, cast

from .deserializer import Deserializer
from .json import JSONDeserializer, JSONParser
from .parser import Parser
from .xml import XMLDeserializer, XMLParser


class ParserFactory:
    """Factory class for creating Parsers"""

    parsers = {".xml": XMLParser, ".json": JSONParser}

    @staticmethod
    def get_parser_type(path: str) -> Type[Parser[str]]:
        """Returns the parser type based on the file extension of the path.

        Args:
            path (str): path of the file that is parsed

        Returns (Type[Parser]): parser type that is used to parse the file
        """
        for extension, parser_type in ParserFactory.parsers.items():
            if path.endswith(extension):
                return cast(Type[Parser[Any]], parser_type)

        raise ValueError("No parser found for the given file")

    @staticmethod
    def get_parser(path: str, *, source: Optional[str] = None) -> Parser[str]:
        """Returns an instantiated Parser based on the file extension of the path using either the source contents or
        the path.

        Args:
            path (str): path of the file that is parsed
            source (Optional[str]): source contents that are parsed

        Returns (Parser): parser that is used to parse the file
        """
        parser = ParserFactory.get_parser_type(path)
        if source is not None:
            return parser(source=source)
        with open(path, encoding="utf8", mode="r") as file:
            return parser(source=file.read())


class DeserializerFactory:
    """Factory class for creating Deserializers"""

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
        """This static method returns the deserializer based on the given path's file extension.

        Args:
            path (str): path to the file

        Returns (Deserializer): deserializer for the given file
        """
        return DeserializerFactory.get_deserializer_type(path)()
