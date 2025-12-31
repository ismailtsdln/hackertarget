#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HackerTarget CLI - Network reconnaissance and security testing toolkit.

This script provides both interactive menu-based and modern CLI interfaces
for accessing HackerTarget API tools.

For modern CLI usage:
    python -m source.cli <command> <target> [options]
    
For interactive menu:
    python hackertarget.py

Author: İsmail Taşdelen
GitHub: https://github.com/ismailtasdelen/hackertarget
"""

import sys
import time
from typing import Optional

# Try to import new CLI, fallback to legacy if needed
try:
    from source.cli import HackerTargetCLI
    from source.hackertarget_api import HackerTargetAPI
    from source.logger import get_logger, Colors
    from source.exceptions import HackerTargetException
    NEW_CLI_AVAILABLE = True
except ImportError:
    from source import hackertarget_api
    NEW_CLI_AVAILABLE = False


# ASCII Art Banner
HACKERTARGET_LOGO = f"""{Colors.BRIGHT_CYAN if NEW_CLI_AVAILABLE else ''}
  _               _              _                          _
 | |_   __ _  __ | |__ ___  _ _ | |_  __ _  _ _  __ _  ___ | |_
 | ' \\ / _` |/ _|| / // -_)| '_||  _|/ _` || '_|/ _` |/ -_)|  _|
 |_||_|\\__,_|\\__||_\\_\\___||_|   \\__|\\__,_||_|  \\__, |\\___| \\__|
                                                |___/
{Colors.BRIGHT_GREEN if NEW_CLI_AVAILABLE else ''}                  Ismail Tasdelen
 | github.com/ismailtasdelen | linkedin.com/in/ismailtasdelen |
{Colors.RESET if NEW_CLI_AVAILABLE else ''}"""

MENU = f"""{Colors.BRIGHT_YELLOW if NEW_CLI_AVAILABLE else ''}
[1]  Traceroute             [8]  Whois Lookup
[2]  Ping Test              [9]  IP Location Lookup
[3]  DNS Lookup             [10] Reverse IP Lookup
[4]  Reverse DNS            [11] TCP Port Scan
[5]  Find DNS Host          [12] Subnet Lookup
[6]  Find Shared DNS        [13] HTTP Header Check
[7]  Zone Transfer          [14] Extract Page Links

[15] Version                [16] Exit
{Colors.RESET if NEW_CLI_AVAILABLE else ''}

{Colors.BRIGHT_MAGENTA if NEW_CLI_AVAILABLE else ''}💡 Tip: Use modern CLI for more features!
   Example: python -m source.cli dns google.com --output json
{Colors.RESET if NEW_CLI_AVAILABLE else ''}
"""


class InteractiveCLI:
    """Legacy interactive menu-based CLI."""
    
    def __init__(self):
        """Initialize interactive CLI."""
        if NEW_CLI_AVAILABLE:
            self.api = HackerTargetAPI()
            self.logger = get_logger()
        else:
            self.api = None
    
    def display_banner(self):
        """Display banner and menu."""
        print(HACKERTARGET_LOGO)
        print(MENU)
    
    def get_tool_choice(self) -> Optional[int]:
        """Get tool choice from user."""
        try:
            choice = input(f"{Colors.BRIGHT_CYAN if NEW_CLI_AVAILABLE else ''}Which option number: {Colors.RESET if NEW_CLI_AVAILABLE else ''}")
            return int(choice)
        except (ValueError, KeyboardInterrupt):
            return None
    
    def get_target(self) -> str:
        """Get target from user."""
        return input(f"{Colors.BRIGHT_CYAN if NEW_CLI_AVAILABLE else ''}[+] Target: {Colors.RESET if NEW_CLI_AVAILABLE else ''}")
    
    def run_tool(self, choice: int, target: str) -> str:
        """Run selected tool."""
        tool_names = {
            1: "Traceroute", 2: "Ping Test", 3: "DNS Lookup",
            4: "Reverse DNS", 5: "Find DNS Host", 6: "Find Shared DNS",
            7: "Zone Transfer", 8: "Whois Lookup", 9: "IP Location Lookup",
            10: "Reverse IP Lookup", 11: "TCP Port Scan", 12: "Subnet Lookup",
            13: "HTTP Header Check", 14: "Extract Page Links"
        }
        
        tool_name = tool_names.get(choice, f"Tool {choice}")
        
        print(f"\n{Colors.BRIGHT_GREEN if NEW_CLI_AVAILABLE else ''}[+] {tool_name} script running..{Colors.RESET if NEW_CLI_AVAILABLE else ''}")
        
        if NEW_CLI_AVAILABLE:
            try:
                result = self.api.query(choice, target)
                return result
            except HackerTargetException as e:
                self.logger.error(f"Error: {e}")
                return f"Error: {e}"
        else:
            return hackertarget_api.hackertarget_api(choice, target)
    
    def show_version(self):
        """Show version information."""
        print(f"\n{Colors.BRIGHT_GREEN if NEW_CLI_AVAILABLE else ''}[+] Version Checking..{Colors.RESET if NEW_CLI_AVAILABLE else ''}")
        time.sleep(1)
        version = "3.0.0" if NEW_CLI_AVAILABLE else "2.0"
        features = " (Enhanced)" if NEW_CLI_AVAILABLE else ""
        time.sleep(1)
        print(f"{Colors.BRIGHT_CYAN if NEW_CLI_AVAILABLE else ''}[+] Version: {version}{features}{Colors.RESET if NEW_CLI_AVAILABLE else ''}")
        
        if NEW_CLI_AVAILABLE:
            print(f"\n{Colors.BRIGHT_MAGENTA}New features:{Colors.RESET}")
            print("  • Modern CLI with argparse")
            print("  • Multiple output formats (JSON, CSV, XML, HTML)")
            print("  • Batch processing support")
            print("  • Configuration file support")
            print("  • Enhanced error handling and retry logic")
            print("  • API key support for premium features")
            print("  • Colored output and logging")
            print(f"\n{Colors.BRIGHT_YELLOW}Try: python -m source.cli --help{Colors.RESET}")
    
    def run(self):
        """Run interactive CLI."""
        self.display_banner()
        
        while True:
            try:
                choice = self.get_tool_choice()
                
                if choice is None:
                    continue
                
                if choice == 16:
                    print(f"{Colors.BRIGHT_GREEN if NEW_CLI_AVAILABLE else ''}Goodbye!{Colors.RESET if NEW_CLI_AVAILABLE else ''}")
                    break
                
                elif choice == 15:
                    self.show_version()
                
                elif 1 <= choice <= 14:
                    print()
                    target = self.get_target()
                    print()
                    result = self.run_tool(choice, target)
                    print(result)
                    print()
                
                else:
                    print(f"{Colors.BRIGHT_RED if NEW_CLI_AVAILABLE else ''}Invalid option! Please choose 1-16.{Colors.RESET if NEW_CLI_AVAILABLE else ''}\n")
            
            except KeyboardInterrupt:
                print(f"\n{Colors.BRIGHT_YELLOW if NEW_CLI_AVAILABLE else ''}Aborted!{Colors.RESET if NEW_CLI_AVAILABLE else ''}")
                break
            
            except Exception as e:
                print(f"{Colors.BRIGHT_RED if NEW_CLI_AVAILABLE else ''}Error: {e}{Colors.RESET if NEW_CLI_AVAILABLE else ''}\n")


def main():
    """Main entry point."""
    # Check if command-line arguments are provided
    if len(sys.argv) > 1 and NEW_CLI_AVAILABLE:
        # Use modern CLI
        cli = HackerTargetCLI()
        sys.exit(cli.run())
    else:
        # Use interactive menu
        interactive = InteractiveCLI()
        interactive.run()


if __name__ == '__main__':
    main()
