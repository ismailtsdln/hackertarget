# HackerTarget CLI - Usage Examples

This directory contains practical examples of using the HackerTarget CLI v3.0.

## Directory Structure

```
examples/
├── basic_usage.py          # Basic API usage examples
├── batch_processing.py     # Batch processing examples
├── custom_formatters.py    # Custom output formatting
├── error_handling.py       # Error handling patterns
├── domains.txt            # Sample domain list for batch processing
└── README.md              # This file
```

## Basic Usage

### Example 1: Simple DNS Lookup

```python
from source import HackerTargetAPI

# Create API client
with HackerTargetAPI() as api:
    # Perform DNS lookup
    result = api.query(3, "google.com")
    print(result)
```

### Example 2: Multiple Queries

```python
from source import HackerTargetAPI

tools = {
    'dns': 3,
    'whois': 8,
    'geoip': 9
}

with HackerTargetAPI() as api:
    target = "github.com"
    
    for tool_name, tool_id in tools.items():
        print(f"\n--- {tool_name.upper()} Results ---")
        result = api.query(tool_id, target)
        print(result)
```

## Batch Processing

### Example 3: Process Multiple Domains

```python
from source import HackerTargetAPI

# List of domains
domains = ["google.com", "github.com", "stackoverflow.com"]

with HackerTargetAPI() as api:
    # Batch DNS lookup
    results = api.batch_query(
        choice=3,  # DNS lookup
        targets=domains,
        delay=1.0  # 1 second between requests
    )
    
    # Process results
    for domain, result in results.items():
        if result['success']:
            print(f"\n{domain}:\n{result['data']}")
        else:
            print(f"\n{domain}: ERROR - {result['error']}")
```

### Example 4: From File

```python
from source import HackerTargetAPI
from source.utils import read_targets_from_file

# Read targets from file
targets = read_targets_from_file('domains.txt')

with HackerTargetAPI() as api:
    results = api.batch_query(3, targets)
    
    # Count successes
    success_count = sum(1 for r in results.values() if r['success'])
    print(f"\nProcessed {len(targets)} targets")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(targets) - success_count}")
```

## Output Formatting

### Example 5: JSON Output

```python
from source import HackerTargetAPI
from source.formatters import get_formatter
import json

with HackerTargetAPI() as api:
    result = api.query(3, "google.com")
    
    # Format as JSON
    formatter = get_formatter('json')
    json_output = formatter.format(
        result,
        metadata={
            'tool': 'DNS Lookup',
            'target': 'google.com'
        }
    )
    
    # Save to file
    with open('dns_result.json', 'w') as f:
        f.write(json_output)
```

### Example 6: CSV Export

```python
from source import HackerTargetAPI
from source.formatters import get_formatter

with HackerTargetAPI() as api:
    # Get multiple results
    targets = ["google.com", "github.com"]
    results = api.batch_query(3, targets)
    
    # Format as CSV
    formatter = get_formatter('csv')
    
    for target, result in results.items():
        if result['success']:
            csv_output = formatter.format(result['data'])
            
            filename = f"{target.replace('.', '_')}_dns.csv"
            with open(filename, 'w') as f:
                f.write(csv_output)
```

### Example 7: HTML Report

```python
from source import HackerTargetAPI
from source.formatters import get_formatter

with HackerTargetAPI() as api:
    result = api.query(8, "github.com")  # Whois
    
    # Format as HTML
    formatter = get_formatter('html')
    html_output = formatter.format(
        result,
        metadata={
            'tool': 'Whois Lookup',
            'target': 'github.com',
            'date': '2025-12-31'
        }
    )
    
    with open('whois_report.html', 'w') as f:
        f.write(html_output)
```

## Error Handling

### Example 8: Robust Error Handling

```python
from source import HackerTargetAPI
from source.exceptions import (
    APIError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    ValidationError
)
import time

def safe_query(api, tool_id, target, max_retries=3):
    """Perform query with comprehensive error handling."""
    
    for attempt in range(max_retries):
        try:
            result = api.query(tool_id, target)
            return result
            
        except RateLimitError as e:
            print(f"Rate limit exceeded. Waiting {e.retry_after} seconds...")
            time.sleep(e.retry_after)
            
        except TimeoutError as e:
            print(f"Request timed out: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying... (attempt {attempt + 2}/{max_retries})")
                
        except NetworkError as e:
            print(f"Network error: {e}")
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                
        except ValidationError as e:
            print(f"Validation error: {e}")
            return None  # Don't retry validation errors
            
        except APIError as e:
            print(f"API error: {e}")
            return None
    
    print(f"Failed after {max_retries} attempts")
    return None

# Usage
with HackerTargetAPI() as api:
    result = safe_query(api, 3, "google.com")
    if result:
        print(result)
```

## Advanced Usage

### Example 9: Custom Configuration

```python
from source import HackerTargetAPI
from source.config import Config

# Load custom config
config = Config('custom_config.yaml')

# Create API with config
api = HackerTargetAPI(
    api_key=config.get('api', 'api_key'),
    timeout=config.get('api', 'timeout', 30),
    max_retries=config.get('api', 'max_retries', 3)
)

# Use API
result = api.query(3, "google.com")
print(result)
```

### Example 10: Logging

```python
from source import HackerTargetAPI
from source.logger import setup_logger
import logging

# Setup custom logger
logger = setup_logger(
    name='my_scanner',
    level=logging.DEBUG,
    log_file='scanner.log',
    colored=True
)

# Use API
with HackerTargetAPI() as api:
    logger.info("Starting scan...")
    
    targets = ["google.com", "github.com"]
    for target in targets:
        logger.debug(f"Scanning {target}")
        result = api.query(3, target)
        logger.info(f"Completed {target}")
```

## CLI Usage Examples

### Basic Commands

```bash
# DNS lookup
hackertarget dns google.com

# Whois lookup
hackertarget whois github.com

# Port scan
hackertarget portscan 192.168.1.1

# Geolocation
hackertarget geoip 8.8.8.8
```

### With Options

```bash
# JSON output
hackertarget dns google.com -o json

# Save to file
hackertarget whois github.com -o json -s whois.json

# Verbose logging
hackertarget dns google.com -v --log-level DEBUG

# Custom timeout
hackertarget portscan 192.168.1.1 --timeout 60
```

### Batch Processing

```bash
# From file
hackertarget batch -f domains.txt -t dns -o csv

# With delay
hackertarget batch -f domains.txt -t whois -d 2.0

# Save results
hackertarget batch -f ips.txt -t geoip -o json -s results.json
```

### Configuration

```bash
# Initialize config
hackertarget config init

# Set API key
hackertarget config set api.api_key YOUR_KEY

# View config
hackertarget config show

# Get specific value
hackertarget config get api.timeout
```

## Sample Files

### domains.txt

```
google.com
github.com
stackoverflow.com
reddit.com
python.org
```

### ips.txt

```
8.8.8.8
1.1.1.1
208.67.222.222
```

## Tips & Best Practices

1. **Rate Limiting**: Always use appropriate delays in batch processing
2. **Error Handling**: Implement retry logic for network errors
3. **Logging**: Use logging instead of print statements
4. **Configuration**: Use config files for API keys and settings
5. **Validation**: Validate inputs before making API calls
6. **Context Managers**: Use `with` statement for automatic cleanup
7. **Batch Size**: Don't process too many targets at once
8. **Save Results**: Always save important scan results

## More Examples

For more examples and advanced usage, check out:

- [API Documentation](https://hackertarget.com/api/)
- [GitHub Repository](https://github.com/ismailtasdelen/hackertarget)
- [CHANGELOG](../CHANGELOG.md)
