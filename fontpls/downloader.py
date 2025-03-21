"""
Font downloading functionality for fontpls.
"""
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from fontTools import ttLib

from .templates.css import create_stylesheet
from .templates.html import create_demo_html
from .utils.font import get_font_format
from .utils.logging import logger
from .utils.url import get_filename_from_url, normalize_url_to_filename


class FontDownloader:
    """
    Downloads font files from URLs and packages them into a folder with stylesheet and demo page.
    """

    def __init__(self, output_dir, verbose=0, threads=None):
        """
        Initialize the font downloader.

        Args:
            output_dir (str): Directory to save downloaded fonts
            verbose (int): Verbosity level (0-2)
            threads (int): Number of download threads to use, defaults to CPU count
        """
        self.output_dir = output_dir
        self.verbose = verbose
        self.threads = threads
        self.font_metadata = {}
        self.metadata_lock = threading.Lock()

    def download_fonts(self, font_urls, source_url=None):
        """
        Download font files from the specified URLs using multiple threads.

        Args:
            font_urls (set): Set of font URLs to download
            source_url (str): The original URL the fonts were extracted from

        Returns:
            list: List of downloaded font filenames
        """
        downloaded_fonts = []

        # Cap threads to font count
        if self.threads is None or self.threads > len(font_urls):
            self.threads = len(font_urls)

        # Save fonts and stylesheet to a folder
        folder_name = normalize_url_to_filename(source_url)
        folder_path = os.path.join(self.output_dir, folder_name)
        logger.info(f"creating font package folder: '{folder_path}'")

        # Create the output directory itself first if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Create the folder before downloading files
        os.makedirs(folder_path, exist_ok=True)

        # Download each font using threads
        total_fonts = len(font_urls)
        logger.info(f"downloading {total_fonts} fonts using {self.threads} threads...")

        # Create a progress tracking counter
        completed_count = 0
        progress_lock = threading.Lock()

        # Define the download worker function
        def download_font(url_index_tuple):
            i, url = url_index_tuple
            nonlocal completed_count

            try:
                # Get font filename from URL
                temp_filename = get_filename_from_url(url)
                filepath = os.path.join(folder_path, temp_filename)
                logger.debug(f"processing font {i}/{total_fonts}: '{url}'")
                logger.debug(f"temporary filename: {temp_filename}")

                # Download font file
                logger.debug(f"downloading from '{url}'")
                response = requests.get(url, headers={"User-Agent": "fontpls/0.1.0"})
                response.raise_for_status()

                # Save to file
                with open(filepath, "wb") as f:
                    f.write(response.content)

                # Extract font metadata for renaming
                final_filename = self._process_font_file(filepath, temp_filename, url)

                # Update progress counter
                with progress_lock:
                    completed_count += 1
                    logger.info(
                        f"downloaded [{completed_count}/{total_fonts}]: '{url}' as '{final_filename}'"
                    )

                return final_filename
            except Exception as e:
                logger.error(f"failed to download {url}: {str(e)}")
                # Update progress counter even for failures
                with progress_lock:
                    completed_count += 1
                return None

        # Create a ThreadPoolExecutor to download fonts in parallel
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            # Submit download tasks to the executor
            futures = [
                executor.submit(download_font, (i, url))
                for i, url in enumerate(font_urls, 1)
            ]

            # Collect results as they complete
            for future in as_completed(futures):
                result = future.result()
                if result:
                    downloaded_fonts.append(result)

        # Create stylesheet content
        logger.info("generating stylesheet...")
        stylesheet_content = create_stylesheet(self.font_metadata)

        # Save each font file
        logger.info("finalizing font files...")
        for font_info in self.font_metadata.values():
            font_path = os.path.join(folder_path, font_info["filename"])
            os.rename(font_info["path"], font_path)

            # Update path in metadata
            font_info["path"] = font_path

            # Add font to list of downloaded files
            downloaded_fonts.append(font_info["filename"])

        # Save the stylesheet
        stylesheet_path = os.path.join(folder_path, "fonts.css")
        with open(stylesheet_path, "w", encoding="utf-8") as f:
            f.write(stylesheet_content)

        # Generate and save demo HTML
        logger.info("generating demo html page...")
        demo_html = create_demo_html(self.font_metadata)
        html_path = os.path.join(folder_path, "index.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(demo_html)

        logger.info(f"demo html saved to '{html_path}'")

        return downloaded_fonts

    def _process_font_file(self, filepath, original_filename, url):
        """
        Process a font file to extract metadata and rename if possible.

        Args:
            filepath (str): Path to the downloaded font file
            original_filename (str): Original filename from URL
            url (str): Source URL of the font

        Returns:
            str: Final filename
        """
        # Default to original filename
        final_filename = original_filename
        file_extension = os.path.splitext(original_filename)[1].lower()

        logger.debug(f"processing font file: '{filepath}'")

        # Try to extract font metadata
        try:
            if file_extension in [".ttf", ".otf", ".woff", ".woff2"]:
                # Use fontTools to extract font metadata
                logger.debug(f"extracting metadata from {file_extension} font")
                font = ttLib.TTFont(filepath)

                # Get font family name
                name_record = None
                for record in font["name"].names:
                    # Look for font family name (nameID 1 or 16)
                    if record.nameID in (1, 16) and record.isUnicode():
                        name_record = record.toUnicode()
                        logger.debug(f"found font family name: {name_record}")
                        break

                # Get font style
                style_record = None
                for record in font["name"].names:
                    # Look for font style name (nameID 2)
                    if record.nameID == 2 and record.isUnicode():
                        style_record = record.toUnicode()
                        logger.debug(f"found font style: {style_record}")
                        break

                if name_record:
                    # Create a clean filename from font family and style
                    clean_name = re.sub(r"[^\w\s-]", "", name_record).strip()
                    clean_name = re.sub(r"[\s]+", "-", clean_name).lower()

                    # Add style if available
                    if style_record:
                        clean_style = re.sub(r"[^\w\s-]", "", style_record).strip()
                        clean_style = re.sub(r"[\s]+", "-", clean_style).lower()
                        clean_name = f"{clean_name}-{clean_style}"

                    # Set the final filename with proper extension
                    final_filename = f"{clean_name}{file_extension}"
                    logger.debug(f"generated clean filename: {final_filename}")

                    # If the file already exists, overwrite it
                    new_filepath = os.path.join(
                        os.path.dirname(filepath), final_filename
                    )
                    if os.path.exists(new_filepath) and new_filepath != filepath:
                        logger.debug(
                            f"file already exists, overwriting: {new_filepath}"
                        )
                        os.remove(new_filepath)

                    # Rename the file
                    logger.debug(f"renaming file to: '{new_filepath}'")
                    os.rename(filepath, new_filepath)
                    filepath = new_filepath

                # Store metadata for stylesheet generation (thread-safe)
                with self.metadata_lock:
                    self.font_metadata[url] = {
                        "family": name_record or "Unknown Font",
                        "style": style_record or "Regular",
                        "path": filepath,
                        "format": get_font_format(file_extension),
                        "filename": final_filename,
                    }
                    logger.debug(f"stored metadata for '{url}'")
            else:
                logger.debug(
                    f"unsupported font extension: {file_extension}, keeping original filename"
                )
        except Exception as e:
            logger.warning(
                f"could not extract metadata from {original_filename}: {str(e)}"
            )

        return final_filename
