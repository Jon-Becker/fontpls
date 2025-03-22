"""
Tests for the HTML extractor functionality in fontpls.extractors.html_extractor
"""
import unittest
from unittest.mock import MagicMock, Mock, patch

import cssutils
import requests

from fontpls.extractors.html_extractor import FontExtractor


class TestFontExtractor(unittest.TestCase):
    """Tests for FontExtractor class."""

    def setUp(self):
        """Set up test fixtures."""
        self.url = "https://example.com"
        self.extractor = FontExtractor(self.url)

    @patch("fontpls.extractors.html_extractor.requests.get")
    def test_successful_extraction(self, mock_get):
        """Test successful font extraction from HTML."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <link rel="stylesheet" href="https://example.com/styles.css">
                <style>
                    @font-face {
                        font-family: 'Internal Font';
                        src: url('/fonts/internal.woff2') format('woff2');
                    }
                </style>
            </head>
            <body>
                <div style="font-family: 'Inline Font'; src: url('/fonts/inline.woff');">Test</div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock CSS response for external stylesheet
        with patch(
            "fontpls.extractors.html_extractor.cssutils.parseString"
        ) as mock_parse:
            # Configure the mock to return realistic CSS objects
            mock_sheet = MagicMock()
            mock_rule = MagicMock()
            mock_rule.type = cssutils.css.CSSFontFaceRule.FONT_FACE_RULE

            # Mock style property
            mock_property = MagicMock()
            mock_property.name = "src"
            mock_property.value = (
                "url('https://example.com/fonts/external.woff2') format('woff2')"
            )

            # Connect mocks
            mock_rule.style = [mock_property]
            mock_sheet.__iter__ = Mock(return_value=iter([mock_rule]))
            mock_parse.return_value = mock_sheet

            # Call the extract method
            result = self.extractor.extract()

            # Verify results
            self.assertEqual(len(result), 1)
            self.assertIn("https://example.com/fonts/external.woff2", result)

    @patch("fontpls.extractors.html_extractor.requests.get")
    def test_extraction_with_included_tags(self, mock_get):
        """Test font extraction with included tags filter."""
        # Create extractor with included tags
        extractor = FontExtractor(self.url, included_tags=["h1", "p"])

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <style>
                    h1 { font-family: 'Heading Font'; src: url('/fonts/heading.woff2'); }
                    p { font-family: 'Paragraph Font'; src: url('/fonts/paragraph.woff2'); }
                    div { font-family: 'Div Font'; src: url('/fonts/div.woff2'); }
                </style>
            </head>
            <body>
                <h1>Heading</h1>
                <p>Paragraph</p>
                <div>Division</div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock CSS rule for the stylesheet
        with patch(
            "fontpls.extractors.html_extractor.cssutils.parseString"
        ) as mock_parse:
            # Configure the mock to return CSS style rules
            mock_sheet = MagicMock()

            # Create h1 rule
            h1_rule = MagicMock()
            h1_rule.type = cssutils.css.CSSStyleRule.STYLE_RULE
            h1_rule.selectorText = "h1"
            h1_property = MagicMock()
            h1_property.name = "font-family"
            h1_property.value = "url('/fonts/heading.woff2')"
            h1_rule.style = [h1_property]

            # Create p rule
            p_rule = MagicMock()
            p_rule.type = cssutils.css.CSSStyleRule.STYLE_RULE
            p_rule.selectorText = "p"
            p_property = MagicMock()
            p_property.name = "font-family"
            p_property.value = "url('/fonts/paragraph.woff2')"
            p_rule.style = [p_property]

            # Create div rule
            div_rule = MagicMock()
            div_rule.type = cssutils.css.CSSStyleRule.STYLE_RULE
            div_rule.selectorText = "div"
            div_property = MagicMock()
            div_property.name = "font-family"
            div_property.value = "url('/fonts/div.woff2')"
            div_rule.style = [div_property]

            # Connect mocks
            mock_sheet.__iter__ = Mock(return_value=iter([h1_rule, p_rule, div_rule]))
            mock_parse.return_value = mock_sheet

            # Patch the _extract_urls_from_property method to track calls
            with patch.object(extractor, "_extract_urls_from_property") as mock_extract:
                # Call the extract method
                extractor.extract()

                # Verify that _extract_urls_from_property was called only for h1 and p rules
                self.assertEqual(mock_extract.call_count, 2)
                mock_extract.assert_any_call("url('/fonts/heading.woff2')", self.url)
                mock_extract.assert_any_call("url('/fonts/paragraph.woff2')", self.url)

    @patch("fontpls.extractors.html_extractor.requests.get")
    def test_extraction_with_excluded_tags(self, mock_get):
        """Test font extraction with excluded tags filter."""
        # Create extractor with excluded tags
        extractor = FontExtractor(self.url, excluded_tags=["div"])

        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <style>
                    h1 { font-family: 'Heading Font'; src: url('/fonts/heading.woff2'); }
                    p { font-family: 'Paragraph Font'; src: url('/fonts/paragraph.woff2'); }
                    div { font-family: 'Div Font'; src: url('/fonts/div.woff2'); }
                </style>
            </head>
            <body>
                <h1>Heading</h1>
                <p>Paragraph</p>
                <div>Division</div>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Mock CSS rule for the stylesheet
        with patch(
            "fontpls.extractors.html_extractor.cssutils.parseString"
        ) as mock_parse:
            # Configure the mock to return CSS style rules
            mock_sheet = MagicMock()

            # Create h1 rule
            h1_rule = MagicMock()
            h1_rule.type = cssutils.css.CSSStyleRule.STYLE_RULE
            h1_rule.selectorText = "h1"
            h1_property = MagicMock()
            h1_property.name = "font-family"
            h1_property.value = "url('/fonts/heading.woff2')"
            h1_rule.style = [h1_property]

            # Create p rule
            p_rule = MagicMock()
            p_rule.type = cssutils.css.CSSStyleRule.STYLE_RULE
            p_rule.selectorText = "p"
            p_property = MagicMock()
            p_property.name = "font-family"
            p_property.value = "url('/fonts/paragraph.woff2')"
            p_rule.style = [p_property]

            # Create div rule
            div_rule = MagicMock()
            div_rule.type = cssutils.css.CSSStyleRule.STYLE_RULE
            div_rule.selectorText = "div"
            div_property = MagicMock()
            div_property.name = "font-family"
            div_property.value = "url('/fonts/div.woff2')"
            div_rule.style = [div_property]

            # Connect mocks
            mock_sheet.__iter__ = Mock(return_value=iter([h1_rule, p_rule, div_rule]))
            mock_parse.return_value = mock_sheet

            # Patch the _extract_urls_from_property method to track calls
            with patch.object(extractor, "_extract_urls_from_property") as mock_extract:
                # Call the extract method
                extractor.extract()

                # Verify that _extract_urls_from_property was called only for h1 and p rules
                self.assertEqual(mock_extract.call_count, 2)
                mock_extract.assert_any_call("url('/fonts/heading.woff2')", self.url)
                mock_extract.assert_any_call("url('/fonts/paragraph.woff2')", self.url)

    @patch("fontpls.extractors.html_extractor.requests.get")
    def test_extraction_google_fonts(self, mock_get):
        """Test extraction of Google Fonts."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <link href="https://fonts.googleapis.com/css2?family=Roboto" rel="stylesheet">
            </head>
            <body>
                <h1>Heading</h1>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()

        # Set up return values for different URLs
        def get_side_effect(url, **kwargs):
            if url == self.url:
                return mock_response
            elif url == "https://fonts.googleapis.com/css2?family=Roboto":
                # Mock Google Fonts CSS response
                google_response = Mock()
                google_response.status_code = 200
                google_response.text = """
                @font-face {
                    font-family: 'Roboto';
                    src: url(https://fonts.gstatic.com/s/roboto/v27/Roboto-Regular.woff2) format('woff2');
                }
                """
                google_response.raise_for_status = Mock()
                return google_response
            return Mock()

        mock_get.side_effect = get_side_effect

        # Mock CSS parsing
        with patch(
            "fontpls.extractors.html_extractor.cssutils.parseString"
        ) as mock_parse:
            # Configure the mock to return a font-face rule for Google Fonts
            google_sheet = MagicMock()
            font_face_rule = MagicMock()
            font_face_rule.type = cssutils.css.CSSFontFaceRule.FONT_FACE_RULE

            # Mock font property
            src_property = MagicMock()
            src_property.name = "src"
            src_property.value = "url(https://fonts.gstatic.com/s/roboto/v27/Roboto-Regular.woff2) format('woff2')"

            # Connect mocks
            font_face_rule.style = [src_property]
            google_sheet.__iter__ = Mock(return_value=iter([font_face_rule]))
            mock_parse.return_value = google_sheet

            # Call the extract method
            result = self.extractor.extract()

            # Verify results
            self.assertEqual(len(result), 1)
            self.assertIn(
                "https://fonts.gstatic.com/s/roboto/v27/Roboto-Regular.woff2", result
            )

    @patch("fontpls.extractors.html_extractor.requests.get")
    def test_handle_request_exception(self, mock_get):
        """Test handling of request exceptions."""
        # Mock a request exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        # Test that the exception is propagated
        with self.assertRaises(requests.exceptions.RequestException):
            self.extractor.extract()

    def test_extract_fonts_with_regex(self):
        """Test the regex fallback for font extraction."""
        # CSS with font URLs
        css_text = """
        @font-face {
            font-family: 'Test Font';
            src: url('/fonts/test.woff2') format('woff2'),
                 url('/fonts/test.woff') format('woff');
        }
        """

        # Call the regex extraction method
        self.extractor._extract_fonts_with_regex(css_text, self.url)

        # Verify that font URLs were extracted
        self.assertEqual(len(self.extractor.font_urls), 2)
        self.assertIn("https://example.com/fonts/test.woff2", self.extractor.font_urls)
        self.assertIn("https://example.com/fonts/test.woff", self.extractor.font_urls)


if __name__ == "__main__":
    unittest.main()
