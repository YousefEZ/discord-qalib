import unittest

from qalib.template_engines.formatter import Formatter


class TestFormatter(unittest.TestCase):
    def test_format(self):
        formatter = Formatter()
        document = "Hello {w}, This is a {t}"
        self.assertEqual(formatter.template(document, {"w": "World"}), "Hello World, This is a {t}")

    def test_attr(self):
        k = type("K", (), {"a": type("R", (), {"b": "k"})})()
        formatter = Formatter()
        document = "Hello {w.a.b}, This is a {t}"
        self.assertEqual(formatter.template(document, {"w": k}), "Hello k, This is a {t}")

    def test_missing_attr(self):
        formatter = Formatter()
        document = "Hello {w.a.b}, This is a {t}"
        self.assertEqual(formatter.template(document, {}), "Hello {w.a.b}, This is a {t}")

    def test_index(self):
        formatter = Formatter()
        document = "Hello {w[0]}, This is a {t}"
        self.assertEqual(formatter.template(document, {}), "Hello {w[0]}, This is a {t}")
