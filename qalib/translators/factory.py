from typing import Optional, Type, cast, Literal, Dict

from .deserializer import Deserializer
from .json import JSONDeserializer, JSONTemplater
from .templater import Templater
from .xml import XMLDeserializer, XMLTemplater

Extensions = Literal[".xml", ".json"]


class TemplaterFactory:
    """Factory class for creating Parsers"""

    parsers: Dict[Extensions, Type[Templater]] = {".xml": XMLTemplater, ".json": JSONTemplater}

    @staticmethod
    def get_templater_type(path: str) -> Type[Templater]:
        """Returns the parser type based on the file extension of the path.

        Args:
            path (str): path of the file that is parsed

        Returns (Type[Parser]): parser type that is used to parse the file
        """
        for extension, parser_type in TemplaterFactory.parsers.items():
            if path.endswith(extension):
                return cast(Type[Templater], parser_type)

        raise ValueError("No parser found for the given file")

    @staticmethod
    def get_templater(path: str, *, source: Optional[str] = None) -> Templater:
        """Returns an instantiated Parser based on the file extension of the path using either the source contents or
        the path.

        Args:
            path (str): path of the file that is parsed
            source (Optional[str]): source contents that are parsed

        Returns (Parser): parser that is used to parse the file
        """
        parser = TemplaterFactory.get_templater_type(path)
        if source is not None:
            return parser(source=source)
        with open(path, encoding="utf8", mode="r") as file:
            return parser(source=file.read())


class DeserializerFactory:
    """Factory class for creating Deserializers"""

    deserializers: Dict[Extensions, Type[Deserializer[str]]] = {".xml": XMLDeserializer, ".json": JSONDeserializer}

    @staticmethod
    def get_deserializer_type(path: str) -> Type[Deserializer[str]]:
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
    def get_deserializer(path: str) -> Deserializer[str]:
        """This static method returns the deserializer based on the given path's file extension.

        Args:
            path (str): path to the file

        Returns (Deserializer): deserializer for the given file
        """
        return DeserializerFactory.get_deserializer_type(path)()
