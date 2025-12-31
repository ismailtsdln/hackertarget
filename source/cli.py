#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Modern CLI interface for HackerTarget using argparse.
Supports both interactive and command-line modes.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional, List

from .hackertarget_api import HackerTargetAPI
from .config import get_config
from .logger import setup_logger, set_log_level
from .formatters import get_formatter
from .utils import read_targets_from_file, sanitize_filename
from .exceptions import HackerTargetException


class HackerTargetCLI:
    """Modern CLI interface for HackerTarget."""
    
    # Tool mappings
    TOOLS = {
        'traceroute': 1,
        'ping': 2,
        'dns': 3,
        'rdns': 4,
        'hostsearch': 5,
        'shareddns': 6,
        'zonetransfer': 7,
        'whois': 8,
        'geoip': 9,
        'reverseip': 10,
        'portscan': 11,
        'subnet': 12,
        'headers': 13,
        'pagelinks': 14,
    }
    
    def __init__(self):
        """Initialize CLI."""
        self.config = get_config()
        self.logger = None
        self.api = None
    
    def _setup_logging(self, args):
        """Setup logging based on arguments and config."""
        log_level = args.log_level if hasattr(args, 'log_level') else self.config.get('logging', 'level', 'INFO')
        log_file = args.log_file if hasattr(args, 'log_file') else self.config.get('logging', 'file')
        colored = not args.no_color if hasattr(args, 'no_color') else self.config.get('logging', 'colored', True)
        
        self.logger = setup_logger(
            level=getattr(__import__('logging'), log_level.upper()),
            log_file=log_file,
            colored=colored
        )
    
    def _setup_api(self, args):
        """Setup API client based on arguments and config."""
        api_key = args.api_key if hasattr(args, 'api_key') and args.api_key else self.config.get('api', 'api_key')
        timeout = args.timeout if hasattr(args, 'timeout') else self.config.get('api', 'timeout', 30)
        max_retries = self.config.get('api', 'max_retries', 3)
        
        self.api = HackerTargetAPI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def run_tool(self, args) -> int:
        """
        Run a specific tool.
        
        Args:
            args: Parsed arguments
            
        Returns:
            Exit code (0 for success, 1 for error)
        """
        try:
            # Get tool choice
            tool_name = args.command
            if tool_name not in self.TOOLS:
                self.logger.error(f"Unknown tool: {tool_name}")
                return 1
            
            choice = self.TOOLS[tool_name]
            target = args.target
            
            # Setup components
            self._setup_logging(args)
            self._setup_api(args)
            
            # Query API
            self.logger.info(f"Running {self.api.get_tool_name(choice)} for: {target}")
            result = self.api.query(choice, target)
            
            # Format output
            output_format = args.output if hasattr(args, 'output') else 'console'
            formatter = get_formatter(output_format, use_color=not args.no_color)
            
            metadata = {
                'tool': self.api.get_tool_name(choice),
                'target': target,
            }
            
            formatted_output = formatter.format(result, metadata=metadata)
            
            # Print or save
            if hasattr(args, 'save') and args.save:
                self._save_output(formatted_output, args.save)
                self.logger.info(f"Output saved to: {args.save}")
            else:
                print(formatted_output)
            
            return 0
        
        except HackerTargetException as e:
            self.logger.error(f"Error: {e}")
            return 1
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            if args.verbose:
                import traceback
                traceback.print_exc()
            return 1
        finally:
            if self.api:
                self.api.close()
    
    def run_batch(self, args) -> int:
        """
        Run batch processing from file.
        
        Args:
            args: Parsed arguments
            
        Returns:
            Exit code
        """
        try:
            # Setup
            self._setup_logging(args)
            self._setup_api(args)
            
            # Read targets
            targets = read_targets_from_file(args.file)
            self.logger.info(f"Loaded {len(targets)} targets from {args.file}")
            
            # Get tool
            tool_name = args.tool
            if tool_name not in self.TOOLS:
                self.logger.error(f"Unknown tool: {tool_name}")
                return 1
            
            choice = self.TOOLS[tool_name]
            
            # Run batch
            delay = args.delay if hasattr(args, 'delay') else self.config.get('batch', 'delay', 1.0)
            results = self.api.batch_query(choice, targets, delay=delay)
            
            # Format and output
            output_format = args.output if hasattr(args, 'output') else 'json'
            formatter = get_formatter(output_format)
            
            formatted_output = formatter.format(results)
            
            if hasattr(args, 'save') and args.save:
                self._save_output(formatted_output, args.save)
                self.logger.info(f"Batch results saved to: {args.save}")
            else:
                print(formatted_output)
            
            return 0
        
        except Exception as e:
            self.logger.error(f"Batch processing error: {e}")
            return 1
        finally:
            if self.api:
                self.api.close()
    
    def run_config(self, args) -> int:
        """
        Handle configuration commands.
        
        Args:
            args: Parsed arguments
            
        Returns:
            Exit code
        """
        try:
            if args.config_command == 'init':
                # Create default config
                config_path = args.path or str(Path.home() / '.hackertarget.yaml')
                self.config.save(config_path)
                print(f"Configuration file created at: {config_path}")
            
            elif args.config_command == 'show':
                # Show current config
                import yaml
                print(yaml.dump(self.config.to_dict(), default_flow_style=False))
            
            elif args.config_command == 'set':
                # Set config value
                section, key = args.key.split('.')
                self.config.set(section, key, args.value)
                config_path = args.path or str(Path.home() / '.hackertarget.yaml')
                self.config.save(config_path)
                print(f"Set {args.key} = {args.value}")
            
            elif args.config_command == 'get':
                # Get config value
                section, key = args.key.split('.')
                value = self.config.get(section, key)
                print(f"{args.key}: {value}")
            
            return 0
        
        except Exception as e:
            print(f"Configuration error: {e}")
            return 1
    
    def run_cache(self, args) -> int:
        """
        Handle cache commands.
        
        Args:
            args: Parsed arguments
            
        Returns:
            Exit code
        """
        try:
            from .cache import get_cache
            cache = get_cache()
            
            if args.cache_command == 'clear':
                # Clear cache
                if cache.clear():
                    print("✅ Cache cleared successfully")
                else:
                    print("❌ Failed to clear cache")
            
            elif args.cache_command == 'stats':
                # Show cache statistics
                stats = cache.stats()
                if 'error' in stats:
                    print(f"❌ Error: {stats['error']}")
                else:
                    print("\n📊 Cache Statistics:")
                    print(f"  Status: {'Enabled' if stats['enabled'] else 'Disabled'}")
                    if stats['enabled']:
                        print(f"  Total Entries: {stats['total_entries']}")
                        print(f"  Active Entries: {stats['active_entries']}")
                        print(f"  Expired Entries: {stats['expired_entries']}")
                        print(f"  Total Hits: {stats['total_hits']}")
                        print(f"  Cache Size: {stats['cache_size_mb']} MB")
                        print(f"  TTL: {stats['ttl_seconds']} seconds")
                        print(f"  Location: {stats['cache_dir']}")
            
            elif args.cache_command == 'cleanup':
                # Cleanup expired entries
                count = cache.cleanup()
                print(f"✅ Removed {count} expired cache entries")
            
            elif args.cache_command == 'top':
                # Show top cached targets
                limit = args.limit if hasattr(args, 'limit') else 10
                top_targets = cache.get_top_targets(limit)
                
                if top_targets:
                    print(f"\n📈 Top {len(top_targets)} Most Cached Targets:")
                    print(f"{'Target':<30} {'Tool ID':<10} {'Hits':<10}")
                    print("-" * 50)
                    for target, tool_id, hits in top_targets:
                        print(f"{target:<30} {tool_id:<10} {hits:<10}")
                else:
                    print("No cached entries found")
            
            return 0
        
        except Exception as e:
            print(f"Cache error: {e}")
            return 1
    
    def _save_output(self, content: str, filepath: str):
        """Save output to file."""
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            prog='hackertarget',
            description='HackerTarget CLI - Network reconnaissance and security testing toolkit',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run DNS lookup
  hackertarget dns google.com
  
  # Run whois with JSON output
  hackertarget whois github.com -o json
  
  # Save results to file
  hackertarget portscan 192.168.1.1 -s scan_results.json -o json
  
  # Batch processing
  hackertarget batch -f domains.txt -t dns -o csv
  
  # Configuration
  hackertarget config set api.api_key YOUR_KEY
  
  # Cache management
  hackertarget cache stats
  hackertarget cache clear

For more information, visit: https://github.com/ismailtasdelen/hackertarget
            """
        )
        
        # Global options
        parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
        parser.add_argument('--no-color', action='store_true', help='Disable colored output')
        parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='INFO', help='Log level')
        parser.add_argument('--log-file', help='Log file path')
        parser.add_argument('--config', help='Configuration file path')
        parser.add_argument('--api-key', help='HackerTarget API key')
        parser.add_argument('--timeout', type=int, help='Request timeout in seconds')
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Individual tool commands
        for tool_name in HackerTargetCLI.TOOLS.keys():
            tool_parser = subparsers.add_parser(tool_name, help=f'Run {tool_name}')
            tool_parser.add_argument('target', help='Target domain or IP address')
            tool_parser.add_argument('-o', '--output', choices=['console', 'json', 'csv', 'xml', 'html'], default='console', help='Output format')
            tool_parser.add_argument('-s', '--save', help='Save output to file')
        
        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Batch processing from file')
        batch_parser.add_argument('-f', '--file', required=True, help='File with targets (one per line)')
        batch_parser.add_argument('-t', '--tool', required=True, choices=list(HackerTargetCLI.TOOLS.keys()), help='Tool to use')
        batch_parser.add_argument('-o', '--output', choices=['json', 'csv', 'xml'], default='json', help='Output format')
        batch_parser.add_argument('-s', '--save', help='Save output to file')
        batch_parser.add_argument('-d', '--delay', type=float, default=1.0, help='Delay between requests (seconds)')
        
        # Config command
        config_parser = subparsers.add_parser('config', help='Manage configuration')
        config_subparsers = config_parser.add_subparsers(dest='config_command', help='Config commands')
        
        config_subparsers.add_parser('init', help='Create default config file').add_argument('-p', '--path', help='Config file path')
        config_subparsers.add_parser('show', help='Show current configuration')
        
        set_parser = config_subparsers.add_parser('set', help='Set configuration value')
        set_parser.add_argument('key', help='Configuration key (e.g., api.api_key)')
        set_parser.add_argument('value', help='Value to set')
        set_parser.add_argument('-p', '--path', help='Config file path')
        
        get_parser = config_subparsers.add_parser('get', help='Get configuration value')
        get_parser.add_argument('key', help='Configuration key')
        
        # Cache command
        cache_parser = subparsers.add_parser('cache', help='Manage cache')
        cache_subparsers = cache_parser.add_subparsers(dest='cache_command', help='Cache commands')
        
        cache_subparsers.add_parser('clear', help='Clear all cache entries')
        cache_subparsers.add_parser('stats', help='Show cache statistics')
        cache_subparsers.add_parser('cleanup', help='Remove expired cache entries')
        
        top_parser = cache_subparsers.add_parser('top', help='Show most cached targets')
        top_parser.add_argument('-l', '--limit', type=int, default=10, help='Number of results to show')
        
        return parser
    
    def run(self, args: Optional[List[str]] = None) -> int:
        """
        Run the CLI.
        
        Args:
            args: Command-line arguments (defaults to sys.argv)
            
        Returns:
            Exit code
        """
        parser = self.create_parser()
        parsed_args = parser.parse_args(args)
        
        # Load config if specified
        if hasattr(parsed_args, 'config') and parsed_args.config:
            self.config = get_config(parsed_args.config)
        
        # Handle commands
        if not parsed_args.command:
            parser.print_help()
            return 0
        
        if parsed_args.command == 'batch':
            return self.run_batch(parsed_args)
        elif parsed_args.command == 'config':
            return self.run_config(parsed_args)
        elif parsed_args.command == 'cache':
            return self.run_cache(parsed_args)
        else:
            return self.run_tool(parsed_args)


def main():
    """Main entry point for CLI."""
    cli = HackerTargetCLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
