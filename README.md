# fontpls

A utility for downloading and organizing fonts from websites.

## Installation

```bash
pip install fontpls
```

## Usage

```bash
fontpls https://example.com
```

### Options

- `--tags` - Only include fonts used in the specified tags (comma-separated)
- `--exclude`, `-x` - Exclude fonts used in the specified tags (comma-separated)
- `--output`, `-o` - Output font files to the specified directory
- `--threads`, `-t` - Number of download threads (default: CPU count)
- `--verbose`, `-v` - Increase verbosity level (use multiple times for more detail)

## Development

### Testing

To run the tests:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run specific test file
pytest tests/test_url_utils.py

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=fontpls tests/

# Generate HTML coverage report
pytest --cov=fontpls --cov-report=html tests/
```

The test suite includes:

- Unit tests for all utility functions
- Tests for HTML extraction with mock responses
- Tests for font downloading with mocked network requests
- Test coverage for error handling and edge cases

Current test coverage is over 88% of the codebase.

## License

See [LICENSE](LICENSE) file.
