"""
Command-line interface for fontpls.
"""
import argparse
import multiprocessing
import os
import sys

from .downloader import FontDownloader
from .extractors import FontExtractor
from .utils.logging import configure_logging, logger


def main():
    """
    Download all fonts used on the specified URL.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Download all fonts used on the specified URL.", prog="fontpls"
    )

    # Add arguments and options
    parser.add_argument("url", help="The website URL to extract fonts from")
    parser.add_argument(
        "--tags", help="Only include fonts used in the specified tags (comma-separated)"
    )
    parser.add_argument(
        "--exclude",
        "-x",
        help="Exclude fonts used in the specified tags (comma-separated)",
    )
    parser.add_argument(
        "--output", "-o", help="Output font files to the specified directory"
    )
    parser.add_argument(
        "--threads",
        "-t",
        type=int,
        default=multiprocessing.cpu_count(),
        help=f"Number of download threads (default: {multiprocessing.cpu_count()})",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity level (use multiple times for more detail)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Parse tags if provided
    included_tags = args.tags.split(",") if args.tags else None
    excluded_tags = args.exclude.split(",") if args.exclude else None

    # Set output directory
    output_dir = args.output or os.getcwd()

    try:
        # Configure logging based on verbosity
        configure_logging(args.verbose)

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"created output directory: {output_dir}")

        # Extract fonts
        logger.info("extracting fonts from webpage...")
        extractor = FontExtractor(args.url, included_tags, excluded_tags)
        font_urls = extractor.extract()

        if not font_urls:
            logger.warning("no fonts found on the specified url")
            return

        logger.info(f"found {len(font_urls)} fonts:")
        for url in font_urls:
            logger.info(f" - {url}")

        # Download fonts
        logger.info("downloading fonts...")
        downloader = FontDownloader(
            output_dir, verbose=args.verbose, threads=args.threads
        )
        downloaded = downloader.download_fonts(font_urls, source_url=args.url)

        # Report results
        if downloaded:
            logger.info(
                f"successfully created font package: '{os.path.join(output_dir, downloaded[0])}'"
            )
        else:
            logger.error("failed to download any fonts. run with -vv for more details")

    except Exception as e:
        logger.error(f"error: {str(e)}", exc_info=args.verbose >= 2)
        sys.exit(1)


if __name__ == "__main__":
    main()
