# Changelog

All notable changes to HackerTarget CLI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-12-31

### 🎉 Major Release - Complete Rewrite

This release brings a complete modernization of the HackerTarget CLI with extensive new features and improvements.

### Added

#### Core Features

- **Modern CLI Interface**: Complete argparse-based CLI with subcommands for each tool
- **Multiple Output Formats**: JSON, CSV, XML, HTML, and enhanced console output
- **Configuration System**: YAML-based configuration with environment variable support
- **Batch Processing**: Process multiple targets from a file
- **API Key Support**: Premium feature support with API key integration
- **Colored Output**: Beautiful colored terminal output with syntax highlighting

#### Developer Experience

- **Comprehensive Logging**: File and console logging with rotation and colored output
- **Error Handling**: Enhanced exception handling with retry logic and exponential backoff
- **Input Validation**: Robust validation for domains, IPs, URLs, and ports
- **Session Management**: Connection pooling and session reuse for better performance
- **Type Hints**: Full type annotations for better IDE support
- **Docstrings**: Comprehensive documentation for all functions and classes

#### New Modules

- `exceptions.py`: Custom exception classes (APIError, RateLimitError, NetworkError, etc.)
- `logger.py`: Advanced logging with colored console output
- `config.py`: Configuration management with YAML and environment variables
- `cli.py`: Modern CLI interface with argparse
- `formatters.py`: Multiple output format support
- `utils.py`: Utility functions for validation and file operations

### Changed

#### API Client (`hackertarget_api.py`)

- **OOP Refactor**: Converted to class-based design (`HackerTargetAPI`)
- **Retry Logic**: Automatic retries with exponential backoff
- **Session Management**: Connection pooling for better performance
- **Response Validation**: Enhanced error detection and handling
- **Rate Limit Detection**: Automatic rate limit detection and handling
- **Batch Query Support**: Query multiple targets with delay control

#### Main Script (`hackertarget.py`)

- **Dual Mode**: Supports both interactive menu and modern CLI
- **Version Bump**: Updated to v3.0.0
- **Colored Menu**: Enhanced visual presentation
- **Feature Discovery**: Tips for using modern CLI features
- **Backward Compatible**: Legacy functionality preserved

#### Package Structure

- **Entry Points**: Console script for easy `hackertarget` command
- **Dependencies**: Updated to modern versions (requests>=2.31.0, pyyaml>=6.0)
- **Python Requirement**: Updated to Python 3.7+
- **Package Metadata**: Enhanced classifiers and keywords

### Improved

- **Documentation**: Updated README with comprehensive usage examples
- **Error Messages**: More informative and actionable error messages
- **Performance**: Connection pooling and session reuse
- **User Experience**: Colored output, better formatting, progress indicators
- **Code Quality**: Type hints, docstrings, and better code organization

### Fixed

- **Error Handling**: Proper exception handling throughout the application
- **Network Errors**: Better handling of timeouts and connection failures
- **Input Validation**: Prevents invalid inputs from reaching the API

### Technical Details

#### New CLI Commands

```bash
# Individual tools
hackertarget dns google.com
hackertarget whois github.com -o json
hackertarget portscan 192.168.1.1 -s results.json

# Batch processing
hackertarget batch -f domains.txt -t dns -o csv

# Configuration
hackertarget config init
hackertarget config set api.api_key YOUR_KEY
```

#### Configuration File Support

```yaml
api:
  api_key: null
  timeout: 30
  max_retries: 3

logging:
  level: INFO
  colored: true

output:
  format: console
  colored: true
```

### Migration Guide

#### From v2.0 to v3.0

**Interactive Mode** - No changes required! The interactive menu still works exactly as before:

```bash
python hackertarget.py
```

**New CLI Mode** - Take advantage of new features:

```bash
# Old way (still works)
python hackertarget.py

# New way - Direct command
hackertarget dns google.com

# New features
hackertarget whois example.com -o json -s output.json
```

**API Usage** - Backward compatible:

```python
# Old way (still works)
from source import hackertarget_api
result = hackertarget_api.hackertarget_api(3, "google.com")

# New way (recommended)
from source import HackerTargetAPI
with HackerTargetAPI() as api:
    result = api.query(3, "google.com")
```

---

## [2.0] - Previous Release

### Features

- 14 network reconnaissance tools
- Interactive menu interface
- Basic API integration
- Unit tests with mocks

---

## Links

- **Repository**: <https://github.com/ismailtasdelen/hackertarget>
- **Issues**: <https://github.com/ismailtasdelen/hackertarget/issues>
- **HackerTarget API**: <https://hackertarget.com/>
