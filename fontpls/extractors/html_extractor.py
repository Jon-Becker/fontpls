"""
HTML font extraction functionality for fontpls.
"""
import logging
import re
from urllib.parse import urljoin

import cssutils
import requests
from bs4 import BeautifulSoup

from ..utils.logging import logger
from ..utils.url import is_font_url

# Suppress cssutils warnings but keep them in the cssutils logger
cssutils.log.setLevel(logging.CRITICAL)


class FontExtractor:
    """
    Extracts font URLs from a webpage.
    """

    def __init__(self, url, included_tags=None, excluded_tags=None):
        """
        Initialize the font extractor.

        Args:
            url (str): The URL to extract fonts from
            included_tags (list): Only include fonts used in these tags
            excluded_tags (list): Exclude fonts used in these tags
        """
        self.url = url
        self.included_tags = included_tags
        self.excluded_tags = excluded_tags
        self.font_urls = set()

    def extract(self):
        """
        Extract all font URLs from the specified webpage.

        Returns:
            set: Set of font URLs
        """
        logger.info(f"fetching '{self.url}'")

        # Fetch the page
        try:
            response = requests.get(self.url, headers={"User-Agent": "fontpls/0.1.0"})
            response.raise_for_status()
            logger.info(f"successfully fetched page ({response.status_code})")
        except requests.exceptions.RequestException as e:
            logger.error(f"failed to fetch page: {str(e)}")
            raise

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract fonts from stylesheets
        logger.info("extracting fonts from external and internal stylesheets")
        self._extract_from_stylesheets(soup)

        # Extract fonts from inline styles
        logger.info("extracting fonts from inline styles")
        self._extract_from_inline_styles(soup)

        # Extract fonts from Google Fonts or other font services
        logger.info("extracting fonts from font services")
        self._extract_from_font_services(soup)

        logger.info(f"found {len(self.font_urls)} unique fonts")
        return self.font_urls

    def _extract_from_stylesheets(self, soup):
        """Extract fonts from external and internal stylesheets."""
        # Find all external stylesheets
        stylesheet_count = 0
        for link in soup.find_all("link", rel="stylesheet"):
            href = link.get("href")
            if href:
                stylesheet_url = urljoin(self.url, href)
                logger.debug(f"found external stylesheet: '{stylesheet_url}'")
                try:
                    css_response = requests.get(
                        stylesheet_url, headers={"User-Agent": "fontpls/0.1.0"}
                    )
                    css_response.raise_for_status()
                    self._parse_css(css_response.text, stylesheet_url)
                    stylesheet_count += 1
                except Exception as e:
                    # If we can't fetch the stylesheet, log and move on
                    logger.debug(
                        f"failed to fetch stylesheet {stylesheet_url}: {str(e)}"
                    )
                    continue

        # Find all internal stylesheets
        internal_count = 0
        for style in soup.find_all("style"):
            logger.debug("found internal stylesheet")
            self._parse_css(style.string, self.url)
            internal_count += 1

        logger.debug(
            f"processed {stylesheet_count} external and {internal_count} internal stylesheets"
        )

    def _extract_from_inline_styles(self, soup):
        """Extract fonts from inline style attributes."""
        # Get elements with inline styles
        elements = soup.find_all(lambda tag: tag.has_attr("style"))

        # Filter elements if tags are specified
        if self.included_tags:
            elements = [el for el in elements if el.name in self.included_tags]
        if self.excluded_tags:
            elements = [el for el in elements if el.name not in self.excluded_tags]

        # Extract font URLs from inline styles
        for element in elements:
            style_text = element["style"]
            if "font" in style_text or "url(" in style_text:
                # Create a dummy rule to parse with cssutils
                try:
                    sheet = cssutils.parseString(f"dummy {{" + style_text + "}")
                    for rule in sheet:
                        if hasattr(rule, "style"):
                            self._extract_fonts_from_style(rule.style, self.url)
                except Exception:
                    # If cssutils fails, try a simple regex
                    self._extract_fonts_with_regex(style_text, self.url)

    def _extract_from_font_services(self, soup):
        """Extract fonts from font services like Google Fonts."""
        # Look for Google Fonts links
        for link in soup.find_all("link", href=re.compile(r"fonts\.googleapis\.com")):
            href = link.get("href")
            if href:
                # For Google Fonts, we need to follow the import to get the actual font files
                try:
                    css_url = (
                        href
                        if href.startswith("http")
                        else ("https:" + href if href.startswith("//") else href)
                    )
                    css_response = requests.get(
                        css_url, headers={"User-Agent": "fontpls/0.1.0"}
                    )
                    css_response.raise_for_status()
                    self._parse_css(css_response.text, css_url)
                except Exception as e:
                    logger.warning(
                        f"failed to process Google Font URL {css_url}: {str(e)}"
                    )
                    continue

    def _parse_css(self, css_text, base_url):
        """
        Parse CSS text to extract font URLs.

        Args:
            css_text (str): CSS text to parse
            base_url (str): Base URL for resolving relative URLs
        """
        if not css_text:
            return

        try:
            sheet = cssutils.parseString(css_text)

            # Extract @font-face rules
            for rule in sheet:
                # Check rule type using cssutils constants
                if (
                    hasattr(rule, "type")
                    and rule.type == cssutils.css.CSSFontFaceRule.FONT_FACE_RULE
                ):
                    self._extract_fonts_from_font_face(rule, base_url)
                elif (
                    hasattr(rule, "type")
                    and rule.type == cssutils.css.CSSStyleRule.STYLE_RULE
                ):
                    # Only process style rules if we're filtering by tags
                    if self.included_tags or self.excluded_tags:
                        selector_text = rule.selectorText.lower()

                        # Check if rule applies to included tags
                        if self.included_tags:
                            if not any(
                                tag.lower() in selector_text
                                for tag in self.included_tags
                            ):
                                continue

                        # Check if rule applies to excluded tags
                        if self.excluded_tags:
                            if any(
                                tag.lower() in selector_text
                                for tag in self.excluded_tags
                            ):
                                continue

                    self._extract_fonts_from_style(rule.style, base_url)
                elif (
                    hasattr(rule, "type")
                    and rule.type == cssutils.css.CSSImportRule.IMPORT_RULE
                ):
                    # Handle @import rules
                    import_url = urljoin(base_url, rule.href)
                    try:
                        import_response = requests.get(
                            import_url, headers={"User-Agent": "fontpls/0.1.0"}
                        )
                        import_response.raise_for_status()
                        self._parse_css(import_response.text, import_url)
                    except Exception as e:
                        logger.warning(
                            f"failed to process imported stylesheet {import_url}: {str(e)}"
                        )
                        continue
        except Exception as e:
            # If cssutils fails, fall back to regex
            logger.debug(f"css parsing failed, falling back to regex: {str(e)}")
            self._extract_fonts_with_regex(css_text, base_url)

    def _extract_fonts_from_font_face(self, rule, base_url):
        """Extract font URLs from @font-face rules."""
        for prop in rule.style:
            if prop.name == "src":
                self._extract_urls_from_property(prop.value, base_url)

    def _extract_fonts_from_style(self, style, base_url):
        """Extract font URLs from CSS style declarations."""
        for prop in style:
            if prop.name in ["font", "font-family"] or "src" in prop.name:
                self._extract_urls_from_property(prop.value, base_url)

    def _extract_urls_from_property(self, value, base_url):
        """Extract URLs from CSS property values."""
        # Use regex to find all url() expressions
        for match in re.finditer(r'url\([\'"]?([^\'")]+)[\'"]?\)', value):
            url = match.group(1)
            if is_font_url(url):
                absolute_url = urljoin(base_url, url)
                self.font_urls.add(absolute_url)

    def _extract_fonts_with_regex(self, text, base_url):
        """Fallback method to extract font URLs using regex."""
        for match in re.finditer(r'url\([\'"]?([^\'")]+)[\'"]?\)', text):
            url = match.group(1)
            if is_font_url(url):
                absolute_url = urljoin(base_url, url)
                self.font_urls.add(absolute_url)
