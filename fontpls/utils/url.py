"""
URL handling utilities for fontpls.
"""
import hashlib
import os
import re
from urllib.parse import unquote, urlparse


def normalize_url_to_filename(url):
    """
    Normalize a URL to a valid filename.

    Args:
        url (str): URL to normalize

    Returns:
        str: Normalized filename
    """
    if not url:
        return "fonts"

    # Parse the URL
    parsed = urlparse(url)
    hostname = parsed.netloc

    # Remove www. and any port number
    hostname = re.sub(r"^www\.", "", hostname)
    hostname = re.sub(r":\d+$", "", hostname)

    # Convert to lowercase and replace dots and other non-alphanumeric chars with hyphens
    normalized = re.sub(r"[^\w-]", "-", hostname.lower())

    # Remove consecutive hyphens and trim hyphens from ends
    normalized = re.sub(r"-+", "-", normalized)
    normalized = normalized.strip("-")

    # If empty (unusual case), use 'fonts'
    if not normalized:
        return "fonts"

    return normalized


def get_filename_from_url(url):
    """
    Extract a valid filename from a URL.

    Args:
        url (str): Font URL

    Returns:
        str: Filename for the font
    """
    # Parse URL path and extract filename
    path = urlparse(url).path
    filename = os.path.basename(unquote(path))

    # If no filename was found, use a hash of the URL
    if not filename or "." not in filename:
        # Create a hash from the URL and append a generic .font extension
        filename = hashlib.md5(url.encode()).hexdigest() + ".font"

    # Ensure filename is valid but keep spaces
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")

    return filename


def is_font_url(url):
    """
    Check if the URL points to a font file.

    Args:
        url (str): URL to check

    Returns:
        bool: True if the URL points to a font file
    """
    font_extensions = [".woff", ".woff2", ".ttf", ".otf", ".eot", ".svg"]
    return any(url.lower().endswith(ext) for ext in font_extensions)
