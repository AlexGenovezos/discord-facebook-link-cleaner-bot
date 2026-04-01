import unittest

from bot.url_cleaner import clean_facebook_url, first_facebook_url, is_facebook_url


class UrlCleanerTests(unittest.TestCase):
    def test_detects_facebook_url(self) -> None:
        text = "hello https://www.facebook.com/share/p/abc123/?mibextid=wwXIfr&fbclid=123"
        self.assertEqual(
            first_facebook_url(text),
            "https://www.facebook.com/share/p/abc123/?mibextid=wwXIfr&fbclid=123",
        )

    def test_ignores_non_facebook_url(self) -> None:
        text = "https://example.com/test"
        self.assertIsNone(first_facebook_url(text))

    def test_mobile_host_is_normalized(self) -> None:
        cleaned = clean_facebook_url("https://m.facebook.com/story.php?story_fbid=1&id=2")
        self.assertTrue(cleaned.startswith("https://www.facebook.com/story.php"))

    def test_junk_params_removed(self) -> None:
        cleaned = clean_facebook_url(
            "https://www.facebook.com/share/p/abc123/?mibextid=wwXIfr&fbclid=999&id=1"
        )
        self.assertEqual(cleaned, "https://www.facebook.com/share/p/abc123/?id=1")

    def test_is_facebook_url(self) -> None:
        self.assertTrue(is_facebook_url("https://fb.watch/abc123"))
        self.assertFalse(is_facebook_url("https://youtube.com/watch?v=1"))


if __name__ == "__main__":
    unittest.main()
