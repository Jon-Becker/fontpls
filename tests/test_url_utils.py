"""
Tests for the URL utility functions in fontpls.utils.url
"""
import unittest

from fontpls.utils.url import (
    get_filename_from_url,
    is_font_url,
    normalize_url_to_filename,
)


class TestNormalizeUrlToFilename(unittest.TestCase):
    """Tests for normalize_url_to_filename function."""

    def test_basic_url(self):
        """Test basic URL normalization."""
        url = "https://example.com/fonts"
        result = normalize_url_to_filename(url)
        self.assertEqual(result, "example-com")

    def test_url_with_www(self):
        """Test URL with www prefix."""
        url = "https://www.example.com/fonts"
        result = normalize_url_to_filename(url)
        self.assertEqual(result, "example-com")

    def test_url_with_port(self):
        """Test URL with port number."""
        url = "https://example.com:8080/fonts"
        result = normalize_url_to_filename(url)
        self.assertEqual(result, "example-com")

    def test_url_with_subdomains(self):
        """Test URL with subdomains."""
        url = "https://fonts.google.com/specimen/Roboto"
        result = normalize_url_to_filename(url)
        self.assertEqual(result, "fonts-google-com")

    def test_url_with_special_chars(self):
        """Test URL with special characters."""
        url = "https://example.com/fonts?query=1&param=2"
        result = normalize_url_to_filename(url)
        self.assertEqual(result, "example-com")

    def test_empty_url(self):
        """Test with empty URL."""
        result = normalize_url_to_filename("")
        self.assertEqual(result, "fonts")

    def test_none_url(self):
        """Test with None URL."""
        result = normalize_url_to_filename(None)
        self.assertEqual(result, "fonts")

    def test_consecutive_hyphens(self):
        """Test URL that would result in consecutive hyphens."""
        url = "https://test..example...com/fonts"
        result = normalize_url_to_filename(url)
        self.assertEqual(result, "test-example-com")


class TestGetFilenameFromUrl(unittest.TestCase):
    """Tests for get_filename_from_url function."""

    def test_basic_font_url(self):
        """Test basic font URL."""
        url = "https://example.com/fonts/roboto.woff2"
        result = get_filename_from_url(url)
        self.assertEqual(result, "roboto.woff2")

    def test_url_with_query_params(self):
        """Test URL with query parameters."""
        url = "https://example.com/fonts/roboto.woff2?v=2.0"
        result = get_filename_from_url(url)
        self.assertEqual(result, "roboto.woff2")

    def test_url_with_encoded_chars(self):
        """Test URL with encoded characters."""
        url = "https://example.com/fonts/Roboto%20Regular.woff2"
        result = get_filename_from_url(url)
        self.assertEqual(result, "Roboto Regular.woff2")

    def test_url_without_filename(self):
        """Test URL without a filename."""
        url = "https://example.com/fonts/"
        result = get_filename_from_url(url)
        self.assertTrue(result.endswith(".font"))
        self.assertEqual(len(result), 37)  # MD5 hash (32) + ".font" (5)

    def test_url_without_extension(self):
        """Test URL without a file extension."""
        url = "https://example.com/fonts/roboto"
        result = get_filename_from_url(url)
        self.assertTrue(result.endswith(".font"))
        self.assertEqual(len(result), 37)  # MD5 hash (32) + ".font" (5)

    def test_url_with_invalid_chars(self):
        """Test URL with invalid filename characters."""
        # Use a URL with fewer invalid chars (just * which is invalid in filenames)
        url = "https://example.com/fonts/roboto*.woff2"
        result = get_filename_from_url(url)
        # Verify that invalid characters are removed
        self.assertFalse(any(c in result for c in "*"))
        # Verify the extension is kept
        self.assertTrue(
            result.endswith(".woff2"),
            f"Expected filename to end with .woff2, got {result}",
        )


class TestIsFontUrl(unittest.TestCase):
    """Tests for is_font_url function."""

    def test_woff_url(self):
        """Test WOFF URL."""
        url = "https://example.com/fonts/roboto.woff"
        self.assertTrue(is_font_url(url))

    def test_woff2_url(self):
        """Test WOFF2 URL."""
        url = "https://example.com/fonts/roboto.woff2"
        self.assertTrue(is_font_url(url))

    def test_ttf_url(self):
        """Test TTF URL."""
        url = "https://example.com/fonts/roboto.ttf"
        self.assertTrue(is_font_url(url))

    def test_otf_url(self):
        """Test OTF URL."""
        url = "https://example.com/fonts/roboto.otf"
        self.assertTrue(is_font_url(url))

    def test_eot_url(self):
        """Test EOT URL."""
        url = "https://example.com/fonts/roboto.eot"
        self.assertTrue(is_font_url(url))

    def test_svg_url(self):
        """Test SVG URL."""
        url = "https://example.com/fonts/roboto.svg"
        self.assertTrue(is_font_url(url))

    def test_uppercase_extension(self):
        """Test URL with uppercase extension."""
        url = "https://example.com/fonts/roboto.WOFF2"
        self.assertTrue(is_font_url(url))

    def test_non_font_url(self):
        """Test non-font URL."""
        url = "https://example.com/images/logo.png"
        self.assertFalse(is_font_url(url))

    def test_url_with_query_params(self):
        """Test font URL with query parameters."""
        url = "https://example.com/fonts/roboto.woff2?v=2.0"
        self.assertTrue(is_font_url(url))


if __name__ == "__main__":
    unittest.main()
