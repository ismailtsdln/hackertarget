# HackerTarget CLI v3.0 🎯

<p align="center">
  <img src="/image/hackertarget.png">
  <br>
  <img src="https://img.shields.io/badge/version-3.0.0-blue.svg">
  <img src="https://img.shields.io/badge/python-3.7+-green.svg">
  <img src="https://img.shields.io/github/license/pyhackertarget/hackertarget">
  <img src="https://img.shields.io/github/stars/pyhackertarget/hackertarget?style=social">
  <img src="https://img.shields.io/github/forks/pyhackertarget/hackertarget?style=social">
</p>

Modern command-line interface for **HackerTarget** network reconnaissance and security testing toolkit.

Use open source tools and network intelligence to help organizations with attack surface discovery and identification of security vulnerabilities.

## 🚀 What's New in v3.0

✨ **Complete rewrite** with modern Python best practices!

- 🎨 **Modern CLI** with argparse and subcommands
- 📊 **Multiple Formats**: JSON, CSV, XML, HTML output
- ⚡ **Batch Processing**: Scan multiple targets from file
- 🔑 **API Key Support**: Premium features integration
- 🎯 **Smart Retry**: Automatic retry with exponential backoff
- 🌈 **Colored Output**: Beautiful terminal output
- ⚙️ **Configuration**: YAML config files support
- 📝 **Better Logging**: File and console with rotation
- 🛡️ **Robust Errors**: Enhanced error handling
- 🔄 **Backward Compatible**: Old interface still works!

## 📦 Installation

### Quick Install

```bash
git clone https://github.com/ismailtasdelen/hackertarget.git
cd hackertarget/
pip install -e .
```

### From PyPI (coming soon)

```bash
pip install hackertarget
```

### Requirements

- Python 3.7+
- requests >= 2.31.0
- pyyaml >= 6.0

## 🎯 Quick Start

### Modern CLI Mode (New!)

```bash
# DNS Lookup
hackertarget dns google.com

# Whois with JSON output
hackertarget whois github.com -o json

# Port scan and save to file
hackertarget portscan 192.168.1.1 -s results.json -o json

# Batch processing
hackertarget batch -f domains.txt -t dns -o csv

# Get help
hackertarget --help
```

### Interactive Mode (Classic)

```bash
python hackertarget.py
```

Interactive menu with 14 tools will appear. Choose an option and enter your target.

## 🛠️ Available Tools

| #  | Tool | Command | Description |
|----|------|---------|-------------|
| 1  | **Traceroute** | `traceroute` | Network path analysis |
| 2  | **Ping Test** | `ping` | ICMP echo test |
| 3  | **DNS Lookup** | `dns` | DNS record query |
| 4  | **Reverse DNS** | `rdns` | PTR record lookup |
| 5  | **Find DNS Host** | `hostsearch` | Find DNS A records |
| 6  | **Find Shared DNS** | `shareddns` | Find shared DNS servers |
| 7  | **Zone Transfer** | `zonetransfer` | AXFR zone transfer |
| 8  | **Whois Lookup** | `whois` | Domain registration info |
| 9  | **IP Geolocation** | `geoip` | Geographic IP location |
| 10 | **Reverse IP** | `reverseip` | Domains on same IP |
| 11 | **Port Scan** | `portscan` | TCP port scanning |
| 12 | **Subnet Calc** | `subnet` | Subnet calculator |
| 13 | **HTTP Headers** | `headers` | HTTP header analysis |
| 14 | **Page Links** | `pagelinks` | Extract hyperlinks |

## 📖 Usage Examples

### Basic Usage

```bash
# DNS lookup
hackertarget dns example.com

# Whois information
hackertarget whois github.com

# Port scan
hackertarget portscan 8.8.8.8
```

### Advanced Usage

#### Output Formats

```bash
# JSON output
hackertarget dns google.com -o json

# CSV output
hackertarget whois github.com -o csv

# HTML report
hackertarget headers example.com -o html

# XML output
hackertarget geoip 8.8.8.8 -o xml
```

#### Save to File

```bash
# Save JSON results
hackertarget dns google.com -o json -s dns_results.json

# Save CSV results
hackertarget portscan 192.168.1.1 -o csv -s scan.csv

# Save HTML report
hackertarget whois example.com -o html -s report.html
```

#### Batch Processing

Create a file with targets (one per line):

```
google.com
github.com
stackoverflow.com
```

Process them:

```bash
# DNS lookup for all domains
hackertarget batch -f domains.txt -t dns -o json -s results.json

# Whois for multiple domains with custom delay
hackertarget batch -f domains.txt -t whois -d 2.0 -o csv
```

#### Configuration

```bash
# Initialize configuration file
hackertarget config init

# Set API key
hackertarget config set api.api_key YOUR_API_KEY_HERE

# View current configuration
hackertarget config show

# Get specific value
hackertarget config get api.timeout
```

#### Logging

```bash
# Verbose mode with debug logging
hackertarget dns google.com --log-level DEBUG -v

# Save logs to file
hackertarget dns google.com --log-file scan.log

# Disable colored output
hackertarget dns google.com --no-color
```

## ⚙️ Configuration File

Create `~/.hackertarget.yaml`:

```yaml
api:
  api_key: YOUR_API_KEY  # Optional, for premium features
  timeout: 30
  max_retries: 3
  backoff_factor: 0.5

logging:
  level: INFO
  file: null  # or "/path/to/logfile.log"
  colored: true

output:
  format: console  # console, json, csv, xml, html
  colored: true
  verbose: false

batch:
  delay: 1.0  # Seconds between requests
  continue_on_error: true
```

Or use environment variables:

```bash
export HACKERTARGET_API_KEY="your-key-here"
export HACKERTARGET_TIMEOUT=60
export HACKERTARGET_LOG_LEVEL=DEBUG
```

## 🐍 Python API

### Basic Usage

```python
from source import HackerTargetAPI

# Create API client
api = HackerTargetAPI()

# DNS lookup
result = api.query(3, "google.com")
print(result)

# With context manager (recommended)
with HackerTargetAPI(timeout=60) as api:
    result = api.query(3, "google.com")
    print(result)
```

### Advanced Usage

```python
from source import HackerTargetAPI
from source.exceptions import APIError, RateLimitError

# API client with custom settings
api = HackerTargetAPI(
    api_key="your-key-here",
    timeout=60,
    max_retries=5,
    backoff_factor=1.0
)

# Batch query
targets = ["google.com", "github.com", "stackoverflow.com"]
results = api.batch_query(
    choice=3,  # DNS lookup
    targets=targets,
    delay=1.0
)

for target, result in results.items():
    if result["success"]:
        print(f"{target}: {result['data']}")
    else:
        print(f"{target}: ERROR - {result['error']}")

# Error handling
try:
    result = api.query(3, "example.com")
except RateLimitError as e:
    print(f"Rate limit exceeded. Retry after: {e.retry_after}s")
except APIError as e:
    print(f"API Error: {e}")
```

### Output Formatting

```python
from source.formatters import get_formatter

# Get formatter
formatter = get_formatter('json')

# Format data
result = api.query(3, "google.com")
formatted = formatter.format(
    result,
    metadata={'tool': 'DNS Lookup', 'target': 'google.com'}
)

print(formatted)

# Save to file
with open('output.json', 'w') as f:
    f.write(formatted)
```

## 🔒 Security & Privacy

- All data is queried from HackerTarget's public API
- No data is stored locally (except optional caching)
- HTTPS used for all API communications
- Rate limiting respected automatically
- API keys supported for authenticated access

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**İsmail Taşdelen**

- GitHub: [@ismailtasdelen](https://github.com/ismailtasdelen)
- LinkedIn: [ismailtasdelen](https://linkedin.com/in/ismailtasdelen)

## 🙏 Acknowledgments

- [HackerTarget](https://hackertarget.com/) for providing the excellent API
- All contributors to this project

## 💰 Support

If you find this tool useful, please consider:

**PayPal**: <https://paypal.me/ismailtsdln>

**LiberaPay**: <a href="https://liberapay.com/ismailtasdelen/donate"><img alt="Donate using Liberapay" src="https://liberapay.com/assets/widgets/donate.svg"></a>

## 📚 Additional Resources

- [HackerTarget API Documentation](https://hackertarget.com/api/)
- [Changelog](CHANGELOG.md)
- [Security Policy](SECURITY.md)

---

**Note**: This tool is not affiliated with HackerTarget. It's an independent CLI wrapper built for educational and authorized security testing purposes only.
