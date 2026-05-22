import unittest

from page_generator import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_simple_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_title_with_whitespace(self):
        self.assertEqual(extract_title("#   Spaced out title   "), "Spaced out title")

    def test_title_not_first_line(self):
        md = "Some intro text\n\n# Real title\n\nMore content"
        self.assertEqual(extract_title(md), "Real title")

    def test_ignores_h2_and_below(self):
        # ## не повинен підходити, шукаємо тільки h1
        md = "## This is h2\n\n# This is h1"
        self.assertEqual(extract_title(md), "This is h1")

    def test_no_title_raises(self):
        with self.assertRaises(ValueError):
            extract_title("No header here\nJust text")


if __name__ == "__main__":
    unittest.main()
