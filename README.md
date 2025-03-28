# fontpls

[![Unit Tests (on PR)](https://github.com/Jon-Becker/fontpls/actions/workflows/tests.yaml/badge.svg)](https://github.com/Jon-Becker/fontpls/actions/workflows/tests.yaml) ![PyPI version](https://badge.fury.io/py/fontpls.svg) ![Installations](https://img.shields.io/pypi/dd/fontpls?color=g)

## Overview

`fontpls` is a minimal cli tool for extracting font files from websites.

This tool helps web developers, designers, and typographers easily extract and reuse fonts from websites with minimal effort.

**Please respect all font licenses when using this tool.**

## Installation

```bash
pip install fontpls
```

Or install from source:

```bash
git clone https://github.com/jon-becker/fontpls
cd fontpls
pip install -e .
```

## Usage

Basic usage:

```bash
fontpls https://example.com
```

With options:

```bash
fontpls https://example.com --output fonts --threads 8 --tags h1,p,div
```

### Options

| Option | Description |
|--------|-------------|
| `--tags` | Only include fonts used in the specified HTML tags (comma-separated) |
| `--exclude`, `-x` | Exclude fonts used in the specified tags (comma-separated) |
| `--output`, `-o` | Output font files to the specified directory |
| `--threads`, `-t` | Number of download threads to use |
| `--verbose`, `-v` | Increase verbosity level (use multiple times for more detail) |

## Output

fontpls creates a directory structure like this:

```
example-com/
├── Font1-Regular.woff2
├── Font2-Bold.woff2
├── Font3-Italic.woff2
├── fonts.css
└── index.html
```

- `fonts.css`: CSS stylesheet with @font-face declarations
- `index.html`: HTML file showcasing all downloaded fonts

## Contributing

If you'd like to contribute to fontpls, please open a pull-request with your changes, as well as detailed information on what is changed, added, or improved.

For more detailed information, see the [contributing guide](CONTRIBUTING.md)

## Issues

If you've found an issue or have a question, please open an issue [here](https://github.com/Jon-Becker/fontpls/issues). All issues must follow their respective templates.
