#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DTA Data Tab

Data tab component for viewing Stata .dta files.
Extends BaseDataTab with DTA-specific functionality.
"""

import os
from tkinter import messagebox
import customtkinter as ctk
import pandas as pd
import logging

from .base_data_tab import BaseDataTab

logger = logging.getLogger(__name__)

# Check for Stata support
STATA_SUPPORT = True
try:
    import pyreadstat
except ImportError:
    STATA_SUPPORT = False


class DTADataTab(BaseDataTab):
    """Data tab for Stata DTA files (read-only)"""
    
    def __init__(self, parent, file_path: str, read_only: bool = True):
        self.meta = None
        # DTA files are always read-only in this application
        super().__init__(parent, file_path, read_only=True)
    
    def setup_toolbar_buttons(self, toolbar):
        """Setup DTA-specific toolbar buttons"""
        # Update status to show it's a Stata file
        file_name = os.path.basename(self.file_path)
        self.status_label.configure(text=f"{file_name} (Stata DTA - Read-Only)")
        
        # Add convert button
        ctk.CTkButton(toolbar, text="Convert to DBF", width=120,
                     command=self.convert_to_dbf).pack(side="right", padx=5)
    
    def load_data(self):
        """Load DTA data"""
        if not STATA_SUPPORT:
            messagebox.showerror("Error", 
                               "pyreadstat library not available.\n" +
                               "Please install it with: pip install pyreadstat")
            return
        
        try:
            # Read the Stata file with metadata
            self.df, self.meta = pyreadstat.read_dta(self.file_path)
            self.total_records = len(self.df)
            
            # Update display
            self.update_data_display()
            
            logger.info(f"Loaded DTA file: {self.file_path} ({self.total_records} records)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load DTA file: {str(e)}")
            logger.error(f"Failed to load DTA file {self.file_path}: {str(e)}")
    
    def convert_to_dbf(self):
        """Open conversion dialog"""
        from ..dialogs.stata_dialog import StataConversionDialog
        
        # Get parent window (main application)
        main_app = self.winfo_toplevel()
        StataConversionDialog(main_app, self.file_path)
    
    def on_double_click(self, event):
        """Handle double-click - DTA files are read-only"""
        # DTA files cannot be edited directly
        pass
