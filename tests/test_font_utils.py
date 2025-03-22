"""
Tests for the font utility functions in fontpls.utils.font
"""
import unittest

from fontpls.utils.font import get_font_format


class TestGetFontFormat(unittest.TestCase):
    """Tests for get_font_format function."""

    def test_woff2_format(self):
        """Test WOFF2 format."""
        self.assertEqual(get_font_format(".woff2"), "woff2")

    def test_woff_format(self):
        """Test WOFF format."""
        self.assertEqual(get_font_format(".woff"), "woff")

    def test_ttf_format(self):
        """Test TTF format."""
        self.assertEqual(get_font_format(".ttf"), "truetype")

    def test_otf_format(self):
        """Test OTF format."""
        self.assertEqual(get_font_format(".otf"), "opentype")

    def test_eot_format(self):
        """Test EOT format."""
        self.assertEqual(get_font_format(".eot"), "embedded-opentype")

    def test_svg_format(self):
        """Test SVG format."""
        self.assertEqual(get_font_format(".svg"), "svg")

    def test_uppercase_extension(self):
        """Test uppercase extension."""
        self.assertEqual(get_font_format(".WOFF2"), "woff2")

    def test_unknown_extension(self):
        """Test unknown extension, should default to truetype."""
        self.assertEqual(get_font_format(".xyz"), "truetype")

    def test_empty_extension(self):
        """Test empty extension, should default to truetype."""
        self.assertEqual(get_font_format(""), "truetype")

    def test_without_dot(self):
        """Test extension without dot."""
        self.assertEqual(get_font_format("woff2"), "truetype")


if __name__ == "__main__":
    unittest.main()
