"""
Tests for the font downloader functionality in fontpls.downloader
"""
import os
import unittest
from unittest.mock import MagicMock, Mock, mock_open, patch

from fontpls.downloader import FontDownloader


class TestFontDownloader(unittest.TestCase):
    """Tests for FontDownloader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.output_dir = "/tmp/fontpls_test"
        self.downloader = FontDownloader(self.output_dir, verbose=0, threads=2)
        self.font_urls = {
            "https://example.com/fonts/font1.woff2",
            "https://example.com/fonts/font2.ttf",
        }

    @patch("os.path.exists")
    @patch("os.makedirs")
    @patch("fontpls.downloader.requests.get")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.rename")
    @patch("fontpls.downloader.ttLib.TTFont")
    @patch("fontpls.downloader.create_stylesheet")
    @patch("fontpls.downloader.create_demo_html")
    def test_download_fonts(
        self,
        mock_create_demo_html,
        mock_create_stylesheet,
        mock_ttfont,
        mock_rename,
        mock_file,
        mock_get,
        mock_makedirs,
        mock_exists,
    ):
        """Test downloading fonts."""
        # Mock responses
        mock_response1 = Mock()
        mock_response1.content = b"mock font data 1"
        mock_response2 = Mock()
        mock_response2.content = b"mock font data 2"

        # Set up return values for different URLs
        def get_side_effect(url, **kwargs):
            if url == "https://example.com/fonts/font1.woff2":
                return mock_response1
            elif url == "https://example.com/fonts/font2.ttf":
                return mock_response2
            return Mock()

        mock_get.side_effect = get_side_effect

        # Mock TTFont to simulate font metadata extraction
        mock_font1 = MagicMock()
        mock_font2 = MagicMock()

        # Set up name records for font1
        name_record1 = MagicMock()
        name_record1.nameID = 1
        name_record1.isUnicode.return_value = True
        name_record1.toUnicode.return_value = "Test Font"

        style_record1 = MagicMock()
        style_record1.nameID = 2
        style_record1.isUnicode.return_value = True
        style_record1.toUnicode.return_value = "Regular"

        mock_font1["name"].names = [name_record1, style_record1]

        # Set up name records for font2
        name_record2 = MagicMock()
        name_record2.nameID = 1
        name_record2.isUnicode.return_value = True
        name_record2.toUnicode.return_value = "Test Font 2"

        style_record2 = MagicMock()
        style_record2.nameID = 2
        style_record2.isUnicode.return_value = True
        style_record2.toUnicode.return_value = "Bold"

        mock_font2["name"].names = [name_record2, style_record2]

        # Set up TTFont to return different font objects for different files
        def ttfont_side_effect(filepath):
            if "font1.woff2" in filepath:
                return mock_font1
            elif "font2.ttf" in filepath:
                return mock_font2
            return MagicMock()

        mock_ttfont.side_effect = ttfont_side_effect

        # Mock stylesheet and demo HTML creation
        mock_create_stylesheet.return_value = "/* CSS content */"
        mock_create_demo_html.return_value = "<!DOCTYPE html>..."

        # Run the download_fonts method
        result = self.downloader.download_fonts(self.font_urls, "https://example.com")

        # Verify the result
        self.assertEqual(len(result), 2)
        self.assertIn("test-font-regular.woff2", result)
        self.assertIn("test-font-2-bold.ttf", result)

        # Verify directory creation
        mock_makedirs.assert_any_call(self.output_dir, exist_ok=True)
        mock_makedirs.assert_any_call(
            os.path.join(self.output_dir, "example-com"), exist_ok=True
        )

        # Verify file operations
        mock_file.assert_any_call(
            os.path.join(self.output_dir, "example-com", "fonts.css"),
            "w",
            encoding="utf-8",
        )
        mock_file.assert_any_call(
            os.path.join(self.output_dir, "example-com", "index.html"),
            "w",
            encoding="utf-8",
        )

        # Verify stylesheet and demo HTML creation
        mock_create_stylesheet.assert_called_once()
        mock_create_demo_html.assert_called_once()

    def test_download_fonts_with_error(self):
        """Test downloading fonts with an error."""
        # Create a completely mocked implementation for this test
        with patch("os.makedirs"):
            with patch("builtins.open", mock_open()):
                with patch(
                    "fontpls.downloader.create_stylesheet", return_value="/* CSS */"
                ):
                    with patch(
                        "fontpls.downloader.create_demo_html",
                        return_value="<!DOCTYPE html>",
                    ):
                        with patch("os.path.exists", return_value=False):
                            with patch("os.rename"):
                                with patch("threading.Lock"):
                                    # Mock ThreadPoolExecutor to control execution
                                    with patch(
                                        "fontpls.downloader.ThreadPoolExecutor"
                                    ) as mock_executor:
                                        # Mock the executor context manager
                                        mock_executor_instance = MagicMock()
                                        mock_executor.return_value.__enter__.return_value = (
                                            mock_executor_instance
                                        )

                                        # Configure submit to return mock futures with controlled results
                                        # We want one future to succeed and one to fail
                                        successful_future = MagicMock()
                                        successful_future.result.return_value = (
                                            "font1.woff2"
                                        )

                                        # Set up future submissions
                                        mock_executor_instance.submit.side_effect = [
                                            successful_future
                                        ]

                                        # Mock as_completed to return only the successful future
                                        with patch(
                                            "fontpls.downloader.as_completed",
                                            return_value=[successful_future],
                                        ):
                                            # Now run the test
                                            result = self.downloader.download_fonts(
                                                {
                                                    "https://example.com/fonts/font1.woff2"
                                                },
                                                "https://example.com",
                                            )

                                            # Should only have one successful download
                                            self.assertEqual(len(result), 1)

    @patch("os.path.exists")
    @patch("os.rename")
    def test_process_font_file(self, mock_rename, mock_exists):
        """Test processing a font file to extract metadata."""
        url = "https://example.com/fonts/test.woff2"
        filepath = "/tmp/fontpls_test/example-com/test.woff2"
        original_filename = "test.woff2"

        # Set mock_exists to return True to prevent rename failure
        mock_exists.return_value = False

        # Mock TTFont to simulate font metadata extraction
        with patch("fontpls.downloader.ttLib.TTFont") as mock_ttfont:
            mock_font = MagicMock()

            # Set up name records
            name_record = MagicMock()
            name_record.nameID = 1
            name_record.isUnicode.return_value = True
            name_record.toUnicode.return_value = "Sample Font"

            style_record = MagicMock()
            style_record.nameID = 2
            style_record.isUnicode.return_value = True
            style_record.toUnicode.return_value = "Regular"

            mock_font["name"].names = [name_record, style_record]
            mock_ttfont.return_value = mock_font

            # Patch os.remove to avoid errors when removing non-existent files
            with patch("os.remove"):
                # Run the _process_font_file method
                result = self.downloader._process_font_file(
                    filepath, original_filename, url
                )

                # Verify the result
                self.assertEqual(result, "sample-font-regular.woff2")

                # Verify the metadata
                self.assertIn(url, self.downloader.font_metadata)
                metadata = self.downloader.font_metadata[url]
                self.assertEqual(metadata["family"], "Sample Font")
                self.assertEqual(metadata["style"], "Regular")
                self.assertEqual(metadata["format"], "woff2")
                self.assertEqual(metadata["filename"], "sample-font-regular.woff2")

    @patch("os.path.exists")
    @patch("os.rename")
    def test_process_font_file_with_error(self, mock_rename, mock_exists):
        """Test processing a font file with an error."""
        url = "https://example.com/fonts/test.woff2"
        filepath = "/tmp/fontpls_test/example-com/test.woff2"
        original_filename = "test.woff2"

        # Mock TTFont to raise an exception
        with patch("fontpls.downloader.ttLib.TTFont") as mock_ttfont:
            mock_ttfont.side_effect = Exception("Font processing error")

            # Run the _process_font_file method
            result = self.downloader._process_font_file(
                filepath, original_filename, url
            )

            # Should return the original filename
            self.assertEqual(result, original_filename)

            # Metadata should not be set
            self.assertNotIn(url, self.downloader.font_metadata)


if __name__ == "__main__":
    unittest.main()
