# fontpls

A minimalist CLI tool for downloading fonts used on websites.

## Installation

### Using pip

```bash
pip install fontpls
```

### From source

```bash
git clone https://github.com/jon-becker/fontpls.git
cd fontpls
pip install -e .
```

## Usage

Basic usage:

```bash
fontpls <url>
```

This will download all fonts used on the specified URL, package them into a zip file, and save it to the current directory.

### Options

```
--tags <tags>     Only include fonts used in the specified tags (comma-separated)
--exclude <tags>  Exclude fonts used in the specified tags (comma-separated)
--output <dir>    Output font files to the specified directory
--no-zip          Don't create a zip file, save individual font files
--verbose, -v     Enable verbose output
--help            Display help message
```

### Examples

Download all fonts from a website as a zip file:

```bash
fontpls https://example.com
```

Download only fonts used in headings:

```bash
fontpls https://example.com --tags h1,h2,h3,h4,h5,h6
```

Download fonts, excluding those used in paragraphs:

```bash
fontpls https://example.com --exclude p,span
```

Save fonts to a specific directory:

```bash
fontpls https://example.com --output ./fonts
```

Download individual font files instead of a zip:

```bash
fontpls https://example.com --no-zip
```

## How It Works

fontpls works by:

1. Fetching the HTML content of the specified URL
2. Parsing the HTML to find:
   - External stylesheets
   - Internal stylesheets (in `<style>` tags)
   - Inline styles
   - Font service imports (like Google Fonts)
3. Analyzing CSS to find font URLs in:
   - `@font-face` rules
   - `url()` declarations that point to font files
4. Downloading the font files
5. Analyzing font metadata to extract font family names and styles
6. Creating descriptive filenames based on font family information
7. Generating a CSS stylesheet with @font-face declarations for easy usage
8. Packaging everything into a zip file named after the website domain

The generated zip file contains:
- Font files renamed to reflect their family names and styles
- A `fonts.css` stylesheet that you can include in your projects

## Development

### Setup

```bash
git clone https://github.com/jon-becker/fontpls.git
cd fontpls
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

## License

MIT License
