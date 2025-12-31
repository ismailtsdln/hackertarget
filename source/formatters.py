#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Output formatters for HackerTarget CLI.
Supports multiple output formats: JSON, CSV, XML, HTML, and colored console.
"""

import json
import csv
import io
from typing import Any, Dict, List
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom

from .logger import Colors


class OutputFormatter:
    """Base class for output formatters."""
    
    def format(self, data: Any, metadata: Dict = None) -> str:
        """
        Format data for output.
        
        Args:
            data: Data to format
            metadata: Optional metadata about the query
            
        Returns:
            Formatted string
        """
        raise NotImplementedError


class JSONFormatter(OutputFormatter):
    """Format output as JSON."""
    
    def format(self, data: Any, metadata: Dict = None) -> str:
        """Format data as JSON."""
        output = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        
        if metadata:
            output["metadata"] = metadata
        
        return json.dumps(output, indent=2, ensure_ascii=False)


class CSVFormatter(OutputFormatter):
    """Format output as CSV."""
    
    def format(self, data: Any, metadata: Dict = None) -> str:
        """Format data as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Add metadata as comments if provided
        if metadata:
            for key, value in metadata.items():
                output.write(f"# {key}: {value}\n")
        
        # Handle different data types
        if isinstance(data, str):
            # Split by lines and treat as rows
            lines = data.strip().split('\n')
            for line in lines:
                # Try to split by common delimiters
                if ',' in line:
                    writer.writerow(line.split(','))
                elif '\t' in line:
                    writer.writerow(line.split('\t'))
                elif ':' in line:
                    parts = line.split(':', 1)
                    writer.writerow([p.strip() for p in parts])
                else:
                    writer.writerow([line.strip()])
        
        elif isinstance(data, (list, tuple)):
            for item in data:
                if isinstance(item, (list, tuple)):
                    writer.writerow(item)
                elif isinstance(item, dict):
                    writer.writerow(item.values())
                else:
                    writer.writerow([item])
        
        elif isinstance(data, dict):
            writer.writerow(data.keys())
            writer.writerow(data.values())
        
        return output.getvalue()


class XMLFormatter(OutputFormatter):
    """Format output as XML."""
    
    def format(self, data: Any, metadata: Dict = None) -> str:
        """Format data as XML."""
        root = ET.Element("hackertarget")
        
        # Add metadata
        if metadata:
            meta_elem = ET.SubElement(root, "metadata")
            for key, value in metadata.items():
                elem = ET.SubElement(meta_elem, key)
                elem.text = str(value)
        
        # Add data
        data_elem = ET.SubElement(root, "data")
        
        if isinstance(data, str):
            data_elem.text = data
        elif isinstance(data, dict):
            for key, value in data.items():
                elem = ET.SubElement(data_elem, key)
                elem.text = str(value)
        elif isinstance(data, (list, tuple)):
            for i, item in enumerate(data):
                elem = ET.SubElement(data_elem, f"item_{i}")
                elem.text = str(item)
        
        # Pretty print
        rough_string = ET.tostring(root, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")


class HTMLFormatter(OutputFormatter):
    """Format output as HTML."""
    
    def format(self, data: Any, metadata: Dict = None) -> str:
        """Format data as HTML."""
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            "  <meta charset='utf-8'>",
            "  <title>HackerTarget Results</title>",
            "  <style>",
            "    body { font-family: 'Courier New', monospace; margin: 20px; background: #1e1e1e; color: #d4d4d4; }",
            "    .container { max-width: 1200px; margin: 0 auto; }",
            "    .header { background: #2d2d2d; padding: 20px; border-radius: 5px; margin-bottom: 20px; }",
            "    .metadata { background: #252526; padding: 15px; border-radius: 5px; margin-bottom: 20px; }",
            "    .data { background: #1e1e1e; padding: 20px; border: 1px solid #3e3e3e; border-radius: 5px; white-space: pre-wrap; }",
            "    h1 { color: #4ec9b0; margin: 0; }",
            "    .meta-item { margin: 5px 0; }",
            "    .meta-key { color: #9cdcfe; font-weight: bold; }",
            "    .meta-value { color: #ce9178; }",
            "  </style>",
            "</head>",
            "<body>",
            "  <div class='container'>",
            "    <div class='header'>",
            "      <h1>🎯 HackerTarget Results</h1>",
            "    </div>",
        ]
        
        # Add metadata section
        if metadata:
            html_parts.append("    <div class='metadata'>")
            html_parts.append("      <h2>Metadata</h2>")
            for key, value in metadata.items():
                html_parts.append(f"      <div class='meta-item'>")
                html_parts.append(f"        <span class='meta-key'>{key}:</span>")
                html_parts.append(f"        <span class='meta-value'>{value}</span>")
                html_parts.append(f"      </div>")
            html_parts.append("    </div>")
        
        # Add data section
        html_parts.append("    <div class='data'>")
        
        if isinstance(data, str):
            html_parts.append(f"      {self._escape_html(data)}")
        elif isinstance(data, dict):
            html_parts.append("<table>")
            for key, value in data.items():
                html_parts.append(f"<tr><td><strong>{key}</strong></td><td>{value}</td></tr>")
            html_parts.append("</table>")
        else:
            html_parts.append(f"      {self._escape_html(str(data))}")
        
        html_parts.extend([
            "    </div>",
            "  </div>",
            "</body>",
            "</html>"
        ])
        
        return '\n'.join(html_parts)
    
    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))


class ColoredConsoleFormatter(OutputFormatter):
    """Format output with colored console output."""
    
    def __init__(self, use_color: bool = True):
        """
        Initialize formatter.
        
        Args:
            use_color: Whether to use color in output
        """
        self.use_color = use_color
    
    def format(self, data: Any, metadata: Dict = None) -> str:
        """Format data with colors for console."""
        parts = []
        
        # Add metadata header
        if metadata:
            parts.append(self._colorize("=" * 60, Colors.BRIGHT_CYAN))
            parts.append(self._colorize("QUERY INFORMATION", Colors.BRIGHT_GREEN, bold=True))
            parts.append(self._colorize("=" * 60, Colors.BRIGHT_CYAN))
            
            for key, value in metadata.items():
                key_colored = self._colorize(f"{key}:", Colors.BRIGHT_YELLOW)
                value_colored = self._colorize(str(value), Colors.BRIGHT_WHITE)
                parts.append(f"{key_colored} {value_colored}")
            
            parts.append("")
        
        # Add data header
        parts.append(self._colorize("=" * 60, Colors.BRIGHT_CYAN))
        parts.append(self._colorize("RESULTS", Colors.BRIGHT_GREEN, bold=True))
        parts.append(self._colorize("=" * 60, Colors.BRIGHT_CYAN))
        parts.append("")
        
        # Add data
        if isinstance(data, str):
            # Highlight important patterns
            formatted_data = self._highlight_patterns(data)
            parts.append(formatted_data)
        else:
            parts.append(str(data))
        
        parts.append("")
        parts.append(self._colorize("=" * 60, Colors.BRIGHT_CYAN))
        
        return '\n'.join(parts)
    
    def _colorize(self, text: str, color: str, bold: bool = False) -> str:
        """Apply color to text if color is enabled."""
        if not self.use_color:
            return text
        
        prefix = Colors.BOLD + color if bold else color
        return f"{prefix}{text}{Colors.RESET}"
    
    def _highlight_patterns(self, text: str) -> str:
        """Highlight important patterns in text."""
        if not self.use_color:
            return text
        
        lines = text.split('\n')
        highlighted = []
        
        for line in lines:
            # Highlight IP addresses
            if any(char.isdigit() for char in line) and '.' in line:
                line = self._colorize(line, Colors.BRIGHT_BLUE)
            # Highlight domains
            elif '.com' in line or '.net' in line or '.org' in line:
                line = self._colorize(line, Colors.BRIGHT_MAGENTA)
            # Highlight headers (lines with colon)
            elif ':' in line and not line.startswith(' '):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = self._colorize(parts[0] + ':', Colors.BRIGHT_YELLOW)
                    value = self._colorize(parts[1], Colors.BRIGHT_WHITE)
                    line = f"{key}{value}"
            
            highlighted.append(line)
        
        return '\n'.join(highlighted)


def get_formatter(format_type: str, **kwargs) -> OutputFormatter:
    """
    Get formatter instance by type.
    
    Args:
        format_type: Type of formatter (json, csv, xml, html, console)
        **kwargs: Additional arguments for formatter
        
    Returns:
        Formatter instance
        
    Raises:
        ValueError: If format type is unknown
    """
    formatters = {
        'json': JSONFormatter,
        'csv': CSVFormatter,
        'xml': XMLFormatter,
        'html': HTMLFormatter,
        'console': ColoredConsoleFormatter,
    }
    
    format_type = format_type.lower()
    
    if format_type not in formatters:
        raise ValueError(
            f"Unknown format type: {format_type}. "
            f"Available formats: {', '.join(formatters.keys())}"
        )
    
    return formatters[format_type](**kwargs)
