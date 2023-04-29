import unittest

from qalib.translators.factory import DeserializerFactory, TemplaterFactory
from qalib.translators.json import JSONDeserializer, JSONTemplater
from qalib.translators.xml import XMLDeserializer, XMLTemplater


class TestFactories(unittest.TestCase):
    """Tests the Parser and Deserializer Factories"""

    def test_parser_json(self):
        self.assertIs(TemplaterFactory.get_templater_type("tests/routes/test.json"), JSONTemplater)

    def test_parser_xml(self):
        self.assertIs(TemplaterFactory.get_templater_type("tests/routes/test.xml"), XMLTemplater)

    def test_parser_json_instance(self):
        self.assertIsInstance(TemplaterFactory.get_templater("tests/routes/simple_embeds.json"), JSONTemplater)

    def test_parser_xml_instance(self):
        self.assertIsInstance(TemplaterFactory.get_templater("tests/routes/simple_embeds.xml"), XMLTemplater)

    def test_deserializer_json(self):
        self.assertIs(
            DeserializerFactory.get_deserializer_type("tests/routes/test.json"),
            JSONDeserializer,
        )

    def test_deserializer_xml(self):
        self.assertIs(
            DeserializerFactory.get_deserializer_type("tests/routes/test.xml"),
            XMLDeserializer,
        )

    def test_deserializer_json_instance(self):
        self.assertIsInstance(
            DeserializerFactory.get_deserializer("tests/routes/simple_embeds.json"),
            JSONDeserializer,
        )

    def test_deserializer_xml_instance(self):
        self.assertIsInstance(
            DeserializerFactory.get_deserializer("tests/routes/simple_embeds.xml"),
            XMLDeserializer,
        )

    def test_parser_random_file(self):
        self.assertRaises(ValueError, TemplaterFactory.get_templater, "tests/routes/random_file.notafile")

    def test_deserializer_random_file(self):
        self.assertRaises(
            ValueError,
            DeserializerFactory.get_deserializer,
            "tests/routes/random_file.notafile",
        )
