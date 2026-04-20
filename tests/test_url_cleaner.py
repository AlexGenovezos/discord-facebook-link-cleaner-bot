import unittest

from bot.url_cleaner import clean_facebook_url, clean_url, first_facebook_url, first_supported_url, is_facebook_url, is_supported_url


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

    def test_marketplace_tracking_params_removed(self) -> None:
        cleaned = clean_facebook_url(
            "https://www.facebook.com/marketplace/item/1262773558658137/"
            "?ref=product_details&referral_code=marketplace_general"
            "&referral_story_type=general_listing&tracking=%7Babc%7D"
        )
        self.assertEqual(
            cleaned,
            "https://www.facebook.com/marketplace/item/1262773558658137/",
        )

    def test_common_ref_params_removed_globally(self) -> None:
        cleaned = clean_facebook_url(
            "https://www.facebook.com/share/p/abc123/?ref=share&refsrc=deprecated&id=1"
        )
        self.assertEqual(cleaned, "https://www.facebook.com/share/p/abc123/?id=1")

    def test_detects_carsandbids_url(self) -> None:
        text = "check this out https://carsandbids.com/auctions/9emlXpv8/1989-bmw-325is-coupe"
        self.assertEqual(
            first_supported_url(text),
            "https://carsandbids.com/auctions/9emlXpv8/1989-bmw-325is-coupe",
        )

    def test_is_supported_url_carsandbids(self) -> None:
        self.assertTrue(is_supported_url("https://carsandbids.com/auctions/abc"))
        self.assertTrue(is_supported_url("https://www.carsandbids.com/auctions/abc"))

    def test_clean_url_carsandbids_passthrough(self) -> None:
        url = "https://carsandbids.com/auctions/9emlXpv8/1989-bmw-325is-coupe"
        cleaned = clean_url(url)
        self.assertEqual(cleaned, url)

    def test_clean_url_carsandbids_https_normalization(self) -> None:
        url = "http://carsandbids.com/auctions/abc#fragment"
        cleaned = clean_url(url)
        self.assertEqual(cleaned, "https://carsandbids.com/auctions/abc")

    def test_clean_url_facebook_uses_facebook_logic(self) -> None:
        url = "https://www.facebook.com/marketplace/item/123/?fbclid=abc&id=1"
        cleaned = clean_url(url)
        self.assertEqual(cleaned, "https://www.facebook.com/marketplace/item/123/")


if __name__ == "__main__":
    unittest.main()
