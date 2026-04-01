import unittest

from bot.formatter import format_clean_post


class FormatterTests(unittest.TestCase):
    def test_format_with_title(self) -> None:
        result = format_clean_post("Parish Fish Fry Photos", "https://www.facebook.com/share/p/abc123/")
        self.assertEqual(result, "**Parish Fish Fry Photos**\nhttps://www.facebook.com/share/p/abc123/")

    def test_format_fallback_title(self) -> None:
        result = format_clean_post("", "https://www.facebook.com/share/p/abc123/")
        self.assertEqual(result, "**Facebook Link**\nhttps://www.facebook.com/share/p/abc123/")


if __name__ == "__main__":
    unittest.main()
