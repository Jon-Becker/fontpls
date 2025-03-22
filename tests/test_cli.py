"""
Tests for the CLI functionality in fontpls.cli
"""
import unittest
from unittest.mock import Mock, call, patch

from fontpls.cli import main


class TestCLI(unittest.TestCase):
    """Tests for CLI functionality."""

    @patch("fontpls.cli.configure_logging")
    @patch("fontpls.cli.FontExtractor")
    @patch("fontpls.cli.FontDownloader")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_cli_basic(
        self,
        mock_makedirs,
        mock_exists,
        mock_downloader_class,
        mock_extractor_class,
        mock_configure_logging,
    ):
        """Test basic CLI execution."""
        # Set up mock objects
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            "https://example.com/fonts/font1.woff2",
            "https://example.com/fonts/font2.ttf",
        }
        mock_extractor_class.return_value = mock_extractor

        mock_downloader = Mock()
        mock_downloader.download_fonts.return_value = [
            "test-font-regular.woff2",
            "test-font-regular.ttf",
        ]
        mock_downloader_class.return_value = mock_downloader

        # Mock argparse to return predefined arguments
        with patch("sys.argv", ["fontpls", "https://example.com"]):
            with patch("os.getcwd", return_value="/current/dir"):
                # Output directory exists
                mock_exists.return_value = True

                # Run the main function
                main()

                # Verify logging configuration
                mock_configure_logging.assert_called_once_with(0)

                # Verify extractor was called correctly
                mock_extractor_class.assert_called_once_with(
                    "https://example.com", None, None
                )
                mock_extractor.extract.assert_called_once()

                # Verify downloader was called correctly
                mock_downloader_class.assert_called_once_with(
                    "/current/dir",
                    verbose=0,
                    threads=mock_downloader_class.call_args[1]["threads"],
                )
                mock_downloader.download_fonts.assert_called_once_with(
                    {
                        "https://example.com/fonts/font1.woff2",
                        "https://example.com/fonts/font2.ttf",
                    },
                    source_url="https://example.com",
                )

                # Verify output directory was not created (already existed)
                mock_makedirs.assert_not_called()

    @patch("fontpls.cli.configure_logging")
    @patch("fontpls.cli.FontExtractor")
    @patch("fontpls.cli.FontDownloader")
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_cli_with_options(
        self,
        mock_makedirs,
        mock_exists,
        mock_downloader_class,
        mock_extractor_class,
        mock_configure_logging,
    ):
        """Test CLI execution with various options."""
        # Set up mock objects
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            "https://example.com/fonts/font1.woff2",
            "https://example.com/fonts/font2.ttf",
        }
        mock_extractor_class.return_value = mock_extractor

        mock_downloader = Mock()
        mock_downloader.download_fonts.return_value = [
            "test-font-regular.woff2",
            "test-font-regular.ttf",
        ]
        mock_downloader_class.return_value = mock_downloader

        # Mock argparse to return predefined arguments
        with patch(
            "sys.argv",
            [
                "fontpls",
                "https://example.com",
                "--tags",
                "h1,p,div",
                "--exclude",
                "footer,header",
                "--output",
                "/custom/output/dir",
                "--threads",
                "4",
                "-vv",
            ],
        ):
            # Output directory doesn't exist
            mock_exists.return_value = False

            # Run the main function
            main()

            # Verify logging configuration
            mock_configure_logging.assert_called_once_with(2)  # -vv means verbosity 2

            # Verify extractor was called correctly with tags and exclude
            mock_extractor_class.assert_called_once_with(
                "https://example.com",
                ["h1", "p", "div"],  # included tags
                ["footer", "header"],  # excluded tags
            )
            mock_extractor.extract.assert_called_once()

            # Verify downloader was called correctly
            mock_downloader_class.assert_called_once_with(
                "/custom/output/dir", verbose=2, threads=4
            )
            mock_downloader.download_fonts.assert_called_once_with(
                {
                    "https://example.com/fonts/font1.woff2",
                    "https://example.com/fonts/font2.ttf",
                },
                source_url="https://example.com",
            )

            # Verify output directory was created
            mock_makedirs.assert_called_once_with("/custom/output/dir")

    @patch("fontpls.cli.configure_logging")
    @patch("fontpls.cli.FontExtractor")
    @patch("fontpls.cli.logger")
    def test_cli_no_fonts_found(
        self, mock_logger, mock_extractor_class, mock_configure_logging
    ):
        """Test CLI when no fonts are found."""
        # Set up mock objects
        mock_extractor = Mock()
        mock_extractor.extract.return_value = set()  # No fonts found
        mock_extractor_class.return_value = mock_extractor

        # Mock argparse to return predefined arguments
        with patch("sys.argv", ["fontpls", "https://example.com"]):
            with patch("os.getcwd", return_value="/current/dir"):
                with patch("os.path.exists", return_value=True):
                    # Run the main function
                    main()

                    # Verify warning was logged
                    mock_logger.warning.assert_called_once_with(
                        "no fonts found on the specified url"
                    )

                    # Verify no downloader was created
                    self.assertNotIn(
                        call("fontpls.cli.FontDownloader"), mock_logger.mock_calls
                    )

    @patch("fontpls.cli.configure_logging")
    @patch("fontpls.cli.FontExtractor")
    @patch("sys.exit")
    @patch("fontpls.cli.logger")
    def test_cli_error_handling(
        self, mock_logger, mock_exit, mock_extractor_class, mock_configure_logging
    ):
        """Test CLI error handling."""
        # Set up mock objects
        mock_extractor = Mock()
        mock_extractor.extract.side_effect = Exception("Test error")
        mock_extractor_class.return_value = mock_extractor

        # Mock argparse to return predefined arguments
        with patch("sys.argv", ["fontpls", "https://example.com"]):
            with patch("os.getcwd", return_value="/current/dir"):
                with patch("os.path.exists", return_value=True):
                    # Run the main function
                    main()

                    # Verify error was logged
                    mock_logger.error.assert_called_once()
                    self.assertIn("Test error", mock_logger.error.call_args[0][0])

                    # Verify exit was called with status 1
                    mock_exit.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
