import unittest

from qalib.translators.factory import ParserFactory, DeserializerFactory
from qalib.translators.json import JSONParser, JSONDeserializer
from qalib.translators.xml import XMLParser, XMLDeserializer


class TestFactories(unittest.TestCase):
    """Tests the Parser and Deserializer Factories"""

    def test_parser_json(self):
        self.assertIs(ParserFactory.get_parser_type("tests/routes/test.json"), JSONParser)

    def test_parser_xml(self):
        self.assertIs(ParserFactory.get_parser_type("tests/routes/test.xml"), XMLParser)

    def test_parser_json_instance(self):
        self.assertIsInstance(ParserFactory.get_parser("tests/routes/simple_embeds.json"), JSONParser)

    def test_parser_xml_instance(self):
        self.assertIsInstance(ParserFactory.get_parser("tests/routes/simple_embeds.xml"), XMLParser)

    def test_deserializer_json(self):
        self.assertIs(DeserializerFactory.get_deserializer_type("tests/routes/test.json"), JSONDeserializer)

    def test_deserializer_xml(self):
        self.assertIs(DeserializerFactory.get_deserializer_type("tests/routes/test.xml"), XMLDeserializer)

    def test_deserializer_json_instance(self):
        self.assertIsInstance(DeserializerFactory.get_deserializer("tests/routes/simple_embeds.json"), JSONDeserializer)

    def test_deserializer_xml_instance(self):
        self.assertIsInstance(DeserializerFactory.get_deserializer("tests/routes/simple_embeds.xml"), XMLDeserializer)

    def test_parser_random_file(self):
        self.assertRaises(ValueError, ParserFactory.get_parser, "tests/routes/random_file.notafile")

    def test_deserializer_random_file(self):
        self.assertRaises(ValueError, DeserializerFactory.get_deserializer, "tests/routes/random_file.notafile")
