# EDVAN DBF Commander Package
"""
EDVAN DBF Commander - Modern Desktop Application for DBF File Management

This package contains the modular structure:
- dialogs/ - Dialog windows for various operations
- tabs/ - Data tab components for DBF and DTA files
- utils/ - Utility functions and helpers
- main.py - Main application class
"""

from .main import EDVANDBFCommander, main

__version__ = "1.1.0"
__author__ = "rusli3"

__all__ = ['EDVANDBFCommander', 'main']
