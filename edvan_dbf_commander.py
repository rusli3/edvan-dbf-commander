#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDVAN DBF Commander - Modern Desktop Application for DBF File Management

Author: rusli3
Version: 1.1.0
Description: A comprehensive DBF file management application with modern GUI
using CustomTkinter, featuring tabbed interface, data editing, SQL queries,
and various import/export capabilities.

This file serves as the entry point and imports the modular package.
For the main application code, see edvan_dbf_commander/main.py
"""

import sys
import os

# Add package to path if running directly
if __name__ == "__main__":
    # Ensure the package can be imported
    package_dir = os.path.dirname(os.path.abspath(__file__))
    if package_dir not in sys.path:
        sys.path.insert(0, package_dir)

# Import and run the main application
from edvan_dbf_commander import main

if __name__ == "__main__":
    main()
