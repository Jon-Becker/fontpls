"""
Font-related utility functions.
"""


def get_font_format(extension):
    """
    Get the CSS font format based on file extension.

    Args:
        extension (str): Font file extension

    Returns:
        str: CSS @font-face format value
    """
    formats = {
        ".woff2": "woff2",
        ".woff": "woff",
        ".ttf": "truetype",
        ".otf": "opentype",
        ".eot": "embedded-opentype",
        ".svg": "svg",
    }
    return formats.get(extension.lower(), "truetype")
