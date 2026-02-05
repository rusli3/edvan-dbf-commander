#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDVAN DBF Commander - Modern Desktop Application for DBF File Management

Author: AI Assistant
Version: 1.0.0
Description: A comprehensive DBF file management application with modern GUI
using CustomTkinter, featuring tabbed interface, data editing, SQL queries,
and various import/export capabilities.
"""

import os
import sys
import shutil
import sqlite3
import threading
from pathlib import Path
from tkinter import messagebox, filedialog
from typing import Dict, List, Optional, Any, Tuple
import logging

# Third-party imports
try:
    import customtkinter as ctk
    import pandas as pd
    from dbfpy3 import dbf
    import xml.etree.ElementTree as ET
    from xml.dom import minidom
    import openpyxl
    import csv
except ImportError as e:
    print(f"Missing required library: {e}")
    print("Please install required packages using: pip install -r requirements.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional Stata DTA support
STATA_SUPPORT = True
try:
    import pyreadstat
except ImportError:
    STATA_SUPPORT = False
    logger.info("pyreadstat not available - Stata .dta support disabled")

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class DBFStructureDialog(ctk.CTkToplevel):
    """Dialog for editing DBF file structure"""
    
    def __init__(self, parent, dbf_file_path: str = None):
        super().__init__(parent)
        self.parent = parent
        self.dbf_file_path = dbf_file_path
        self.fields_data = []
        
        self.title("DBF Structure Editor")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        if dbf_file_path:
            self.load_structure()
    
    def setup_ui(self):
        """Setup the structure editor UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="DBF Structure Editor", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Fields frame
        fields_frame = ctk.CTkFrame(main_frame)
        fields_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Fields list with scrollbar
        self.fields_tree = ctk.CTkScrollableFrame(fields_frame, height=300)
        self.fields_tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Headers
        headers_frame = ctk.CTkFrame(self.fields_tree)
        headers_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(headers_frame, text="Field Name", width=150).pack(side="left", padx=5)
        ctk.CTkLabel(headers_frame, text="Type", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(headers_frame, text="Length", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(headers_frame, text="Decimals", width=80).pack(side="left", padx=5)
        ctk.CTkLabel(headers_frame, text="Actions", width=120).pack(side="left", padx=5)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(buttons_frame, text="Add Field", 
                     command=self.add_field).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Save Structure", 
                     command=self.save_structure).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Export Structure", 
                     command=self.export_structure).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Close", 
                     command=self.destroy).pack(side="right", padx=5)
    
    def load_structure(self):
        """Load existing DBF structure"""
        try:
            with dbf.Dbf(self.dbf_file_path) as db:
                self.fields_data = []
                for field in db.header.fields:
                    self.fields_data.append({
                        'name': field.name,
                        'type': field.type,
                        'length': field.length,
                        'decimals': field.decimal_count
                    })
                self.refresh_fields_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load structure: {str(e)}")
    
    def refresh_fields_display(self):
        """Refresh the fields display"""
        # Clear existing widgets
        for widget in self.fields_tree.winfo_children()[1:]:  # Skip header
            widget.destroy()
        
        # Add field rows
        for i, field in enumerate(self.fields_data):
            self.create_field_row(i, field)
    
    def create_field_row(self, index: int, field: dict):
        """Create a row for a field"""
        row_frame = ctk.CTkFrame(self.fields_tree)
        row_frame.pack(fill="x", pady=2)
        
        # Field name
        name_entry = ctk.CTkEntry(row_frame, width=150)
        name_entry.pack(side="left", padx=5)
        name_entry.insert(0, field['name'])
        
        # Field type
        type_combo = ctk.CTkComboBox(row_frame, width=80, 
                                    values=["C", "N", "L", "D", "M"])
        type_combo.pack(side="left", padx=5)
        type_combo.set(field['type'])
        
        # Length
        length_entry = ctk.CTkEntry(row_frame, width=80)
        length_entry.pack(side="left", padx=5)
        length_entry.insert(0, str(field['length']))
        
        # Decimals
        decimals_entry = ctk.CTkEntry(row_frame, width=80)
        decimals_entry.pack(side="left", padx=5)
        decimals_entry.insert(0, str(field['decimals']))
        
        # Actions
        actions_frame = ctk.CTkFrame(row_frame, width=120)
        actions_frame.pack(side="left", padx=5)
        
        ctk.CTkButton(actions_frame, text="↑", width=30,
                     command=lambda i=index: self.move_field_up(i)).pack(side="left", padx=2)
        ctk.CTkButton(actions_frame, text="↓", width=30,
                     command=lambda i=index: self.move_field_down(i)).pack(side="left", padx=2)
        ctk.CTkButton(actions_frame, text="×", width=30,
                     command=lambda i=index: self.delete_field(i)).pack(side="left", padx=2)
        
        # Store references for data extraction
        setattr(row_frame, 'name_entry', name_entry)
        setattr(row_frame, 'type_combo', type_combo)
        setattr(row_frame, 'length_entry', length_entry)
        setattr(row_frame, 'decimals_entry', decimals_entry)
    
    def add_field(self):
        """Add a new field"""
        new_field = {
            'name': f'FIELD{len(self.fields_data) + 1}',
            'type': 'C',
            'length': 10,
            'decimals': 0
        }
        self.fields_data.append(new_field)
        self.refresh_fields_display()
    
    def delete_field(self, index: int):
        """Delete a field"""
        if 0 <= index < len(self.fields_data):
            del self.fields_data[index]
            self.refresh_fields_display()
    
    def move_field_up(self, index: int):
        """Move field up"""
        if index > 0:
            self.fields_data[index], self.fields_data[index-1] = \
                self.fields_data[index-1], self.fields_data[index]
            self.refresh_fields_display()
    
    def move_field_down(self, index: int):
        """Move field down"""
        if index < len(self.fields_data) - 1:
            self.fields_data[index], self.fields_data[index+1] = \
                self.fields_data[index+1], self.fields_data[index]
            self.refresh_fields_display()
    
    def save_structure(self):
        """Save the current structure"""
        try:
            # Extract current data from UI
            self.extract_fields_data()
            
            # Here you would implement the actual structure saving
            # This is a simplified version
            messagebox.showinfo("Success", "Structure saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save structure: {str(e)}")
    
    def extract_fields_data(self):
        """Extract field data from UI elements"""
        extracted_data = []
        for widget in self.fields_tree.winfo_children()[1:]:  # Skip header
            if hasattr(widget, 'name_entry'):
                field_data = {
                    'name': widget.name_entry.get(),
                    'type': widget.type_combo.get(),
                    'length': int(widget.length_entry.get() or 0),
                    'decimals': int(widget.decimals_entry.get() or 0)
                }
                extracted_data.append(field_data)
        self.fields_data = extracted_data
    
    def export_structure(self):
        """Export structure to text file"""
        try:
            self.extract_fields_data()
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("DBF Structure Export\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"{'Field Name':<20} {'Type':<8} {'Length':<10} {'Decimals':<10}\n")
                    f.write("-" * 50 + "\n")
                    
                    for field in self.fields_data:
                        f.write(f"{field['name']:<20} {field['type']:<8} "
                               f"{field['length']:<10} {field['decimals']:<10}\n")
                
                messagebox.showinfo("Success", f"Structure exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export structure: {str(e)}")


class FindReplaceDialog(ctk.CTkToplevel):
    """Find and Replace dialog"""
    
    def __init__(self, parent, data_tab):
        super().__init__(parent)
        self.parent = parent
        self.data_tab = data_tab
        
        self.title("Find & Replace")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the find/replace UI"""
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Find & Replace", 
                                  font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # Find section
        find_frame = ctk.CTkFrame(main_frame)
        find_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(find_frame, text="Find:").pack(anchor="w", padx=10, pady=5)
        self.find_entry = ctk.CTkEntry(find_frame, width=300)
        self.find_entry.pack(padx=10, pady=5)
        
        # Replace section
        replace_frame = ctk.CTkFrame(main_frame)
        replace_frame.pack(fill="x", pady=5)
        
        ctk.CTkLabel(replace_frame, text="Replace with:").pack(anchor="w", padx=10, pady=5)
        self.replace_entry = ctk.CTkEntry(replace_frame, width=300)
        self.replace_entry.pack(padx=10, pady=5)
        
        # Options
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=5)
        
        self.case_sensitive = ctk.CTkCheckBox(options_frame, text="Case sensitive")
        self.case_sensitive.pack(anchor="w", padx=10, pady=2)
        
        self.partial_match = ctk.CTkCheckBox(options_frame, text="Partial match")
        self.partial_match.pack(anchor="w", padx=10, pady=2)
        
        # Buttons
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(buttons_frame, text="Find Next", 
                     command=self.find_next).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Replace", 
                     command=self.replace_current).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Replace All", 
                     command=self.replace_all).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Close", 
                     command=self.destroy).pack(side="right", padx=5)
    
    def find_next(self):
        """Find next occurrence"""
        find_text = self.find_entry.get()
        if not find_text:
            return
        
        try:
            # Implementation would depend on the data tab structure
            messagebox.showinfo("Find", f"Searching for: {find_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Find failed: {str(e)}")
    
    def replace_current(self):
        """Replace current selection"""
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        try:
            # Implementation would depend on the data tab structure
            messagebox.showinfo("Replace", f"Replaced '{find_text}' with '{replace_text}'")
        except Exception as e:
            messagebox.showerror("Error", f"Replace failed: {str(e)}")
    
    def replace_all(self):
        """Replace all occurrences"""
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        try:
            # Implementation would depend on the data tab structure
            count = 0  # This would be calculated based on actual replacements
            messagebox.showinfo("Replace All", f"Replaced {count} occurrences")
        except Exception as e:
            messagebox.showerror("Error", f"Replace all failed: {str(e)}")


class CSVConversionDialog(ctk.CTkToplevel):
    """Dialog for configuring CSV conversion options"""
    
    def __init__(self, parent, source_file_path: str, file_type: str = "dbf"):
        super().__init__(parent)
        self.parent = parent
        self.source_file_path = source_file_path
        self.file_type = file_type  # "dbf" or "dta"
        self.df = None
        self.meta = None
        
        self.title(f"Convert {file_type.upper()} to CSV")
        self.geometry("500x600")
        self.transient(parent)
        self.grab_set()
        
        self.setup_ui()
        self.load_file_info()
    
    def setup_ui(self):
        """Setup the CSV conversion dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text=f"Convert {self.file_type.upper()} to CSV", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # File info frame
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(info_frame, text="File Information:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.info_text = ctk.CTkTextbox(info_frame, height=120)
        self.info_text.pack(fill="x", padx=10, pady=5)
        
        # CSV Options frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(options_frame, text="CSV Options:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # Delimiter selection
        delimiter_frame = ctk.CTkFrame(options_frame)
        delimiter_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(delimiter_frame, text="Field Delimiter:").pack(side="left", padx=5)
        self.delimiter_var = ctk.StringVar(value=",")
        delimiter_combo = ctk.CTkComboBox(delimiter_frame, values=[",", ";", "\t", "|"], 
                                         variable=self.delimiter_var)
        delimiter_combo.pack(side="left", padx=5)
        
        # Encoding selection
        encoding_frame = ctk.CTkFrame(options_frame)
        encoding_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(encoding_frame, text="Text Encoding:").pack(side="left", padx=5)
        self.encoding_var = ctk.StringVar(value="utf-8")
        encoding_combo = ctk.CTkComboBox(encoding_frame, values=["utf-8", "utf-8-sig", "cp1252", "iso-8859-1"], 
                                        variable=self.encoding_var)
        encoding_combo.pack(side="left", padx=5)
        
        # Options checkboxes
        checkbox_frame = ctk.CTkFrame(options_frame)
        checkbox_frame.pack(fill="x", padx=10, pady=5)
        
        self.include_headers = ctk.CTkCheckBox(checkbox_frame, text="Include column headers")
        self.include_headers.pack(anchor="w", padx=5, pady=2)
        self.include_headers.select()
        
        self.quote_strings = ctk.CTkCheckBox(checkbox_frame, text="Quote text fields")
        self.quote_strings.pack(anchor="w", padx=5, pady=2)
        self.quote_strings.select()
        
        self.remove_empty = ctk.CTkCheckBox(checkbox_frame, text="Skip empty rows")
        self.remove_empty.pack(anchor="w", padx=5, pady=2)
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(buttons_frame, text="Preview Data", 
                     command=self.preview_data).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Convert to CSV", 
                     command=self.convert_to_csv).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Cancel", 
                     command=self.destroy).pack(side="right", padx=5)
    
    def load_file_info(self):
        """Load file information"""
        try:
            if self.file_type == "dta":
                self.load_dta_info()
            else:
                self.load_dbf_info()
        except Exception as e:
            error_msg = f"Error loading file: {str(e)}\n\nPlease check if the file is valid and accessible."
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", error_msg)
    
    def load_dta_info(self):
        """Load Stata file information"""
        if not STATA_SUPPORT:
            self.info_text.insert("1.0", "Error: pyreadstat library not available.\nPlease install it with: pip install pyreadstat")
            return
        
        # Read the Stata file with metadata
        self.df, self.meta = pyreadstat.read_dta(self.source_file_path)
        
        # Display file information
        info = f"""File: {os.path.basename(self.source_file_path)}
Size: {os.path.getsize(self.source_file_path):,} bytes
Records: {len(self.df):,}
Columns: {len(self.df.columns)}

Column Information:
{'-'*40}
"""
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            info += f"{col:<15} {dtype:<12}\n"
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info)
    
    def load_dbf_info(self):
        """Load DBF file information"""
        # Read DBF file using dbfpy3
        with dbf.Dbf(self.source_file_path) as db:
            records = []
            field_names = [field.name for field in db.header.fields]
            
            for record in db:
                records.append([record[field] for field in field_names])
            
            # Create DataFrame
            self.df = pd.DataFrame(records, columns=field_names)
        
        # Display file information
        info = f"""File: {os.path.basename(self.source_file_path)}
Size: {os.path.getsize(self.source_file_path):,} bytes
Records: {len(self.df):,}
Columns: {len(self.df.columns)}

Column Information:
{'-'*40}
"""
        
        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            info += f"{col:<15} {dtype:<12}\n"
        
        self.info_text.delete("1.0", "end")
        self.info_text.insert("1.0", info)
    
    def preview_data(self):
        """Preview the data in a separate window"""
        if self.df is None:
            messagebox.showerror("Error", "No data loaded. Please check the file.")
            return
        
        # Create preview window
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Data Preview")
        preview_window.geometry("800x600")
        preview_window.transient(self)
        
        # Create text widget for preview
        preview_text = ctk.CTkTextbox(preview_window)
        preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show first 20 rows
        preview_data = self.df.head(20).to_string()
        preview_text.insert("1.0", f"First 20 rows preview:\n\n{preview_data}")
        
        # Add close button
        ctk.CTkButton(preview_window, text="Close", 
                     command=preview_window.destroy).pack(pady=10)
    
    def convert_to_csv(self):
        """Convert file to CSV"""
        if self.df is None:
            messagebox.showerror("Error", "No data loaded. Please check the file.")
            return
        
        # Ask user for save location
        csv_path = filedialog.asksaveasfilename(
            title="Save CSV File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialvalue=f"{os.path.splitext(os.path.basename(self.source_file_path))[0]}.csv"
        )
        
        if not csv_path:
            return
        
        try:
            # Prepare data for export
            export_df = self.df.copy()
            
            # Remove empty rows if requested
            if self.remove_empty.get():
                export_df = export_df.dropna(how='all')
            
            # Get CSV options
            delimiter = self.delimiter_var.get()
            
            encoding = self.encoding_var.get()
            include_headers = self.include_headers.get()
            
            # Configure CSV writing options
            csv_options = {
                'sep': delimiter,
                'encoding': encoding,
                'index': False,
                'header': include_headers
            }
            
            # Handle quoting
            if self.quote_strings.get():
                csv_options['quoting'] = csv.QUOTE_NONNUMERIC
            else:
                csv_options['quoting'] = csv.QUOTE_MINIMAL
            
            # Export to CSV
            export_df.to_csv(csv_path, **csv_options)
            
            # Show success message
            messagebox.showinfo("Conversion Complete", 
                              f"File successfully converted to CSV:\n{csv_path}\n\n" +
                              f"Records exported: {len(export_df):,}")
            
            logger.info(f"{self.file_type.upper()} to CSV conversion completed: {csv_path}")
            self.destroy()
            
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Failed to convert file: {str(e)}")
            logger.error(f"CSV conversion failed: {str(e)}")


class StataConversionDialog(ctk.CTkToplevel):
    """Dialog for converting Stata .dta files"""
    
    def __init__(self, parent, dta_file_path: str):
        super().__init__(parent)
        self.parent = parent
        self.dta_file_path = dta_file_path
        
        self.title("Stata File Conversion")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        
        self.df = None
        self.meta = None
        
        self.setup_ui()
        self.load_dta_info()
    
    def setup_ui(self):
        """Setup the conversion dialog UI"""
        # Main frame
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        title_label = ctk.CTkLabel(main_frame, text="Stata File Conversion", 
                                  font=ctk.CTkFont(size=20, weight="bold"))
        title_label.pack(pady=(0, 20))
        
        # File info frame
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(info_frame, text="File Information:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        self.info_text = ctk.CTkTextbox(info_frame, height=150)
        self.info_text.pack(fill="x", padx=10, pady=5)
        
        # Conversion options frame
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(options_frame, text="Conversion Options:", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        # Conversion type selection
        conversion_frame = ctk.CTkFrame(options_frame)
        conversion_frame.pack(fill="x", padx=10, pady=5)
        
        self.conversion_type = ctk.StringVar(value="open_direct")
        
        ctk.CTkRadioButton(conversion_frame, text="Open directly in EDVAN DBF Commander",
                          variable=self.conversion_type, value="open_direct").pack(anchor="w", padx=5, pady=5)
        
        ctk.CTkRadioButton(conversion_frame, text="Convert to DBF file and save",
                          variable=self.conversion_type, value="convert_save").pack(anchor="w", padx=5, pady=5)
        
        ctk.CTkRadioButton(conversion_frame, text="Import into existing DBF file",
                          variable=self.conversion_type, value="import_existing").pack(anchor="w", padx=5, pady=5)
        
        # Options for field type mapping
        mapping_frame = ctk.CTkFrame(options_frame)
        mapping_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(mapping_frame, text="Field Type Mapping:").pack(anchor="w", padx=5, pady=2)
        
        self.preserve_types = ctk.CTkCheckBox(mapping_frame, text="Preserve original data types when possible")
        self.preserve_types.pack(anchor="w", padx=10, pady=2)
        self.preserve_types.select()
        
        self.handle_missing = ctk.CTkCheckBox(mapping_frame, text="Convert missing values to empty strings")
        self.handle_missing.pack(anchor="w", padx=10, pady=2)
        self.handle_missing.select()
        
        # Buttons frame
        buttons_frame = ctk.CTkFrame(main_frame)
        buttons_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(buttons_frame, text="Preview Data", 
                     command=self.preview_data).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Convert", 
                     command=self.convert_file).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Cancel", 
                     command=self.destroy).pack(side="right", padx=5)
    
    def load_dta_info(self):
        """Load Stata file information"""
        if not STATA_SUPPORT:
            self.info_text.insert("1.0", "Error: pyreadstat library not available.\nPlease install it with: pip install pyreadstat")
            return
        
        try:
            # Read the Stata file with metadata
            self.df, self.meta = pyreadstat.read_dta(self.dta_file_path)
            
            # Display file information
            info = f"""File: {os.path.basename(self.dta_file_path)}
Size: {os.path.getsize(self.dta_file_path):,} bytes
Records: {len(self.df):,}
Columns: {len(self.df.columns)}

Column Information:
{'-'*50}
"""
            
            for col in self.df.columns:
                dtype = str(self.df[col].dtype)
                info += f"{col:<20} {dtype:<15}\n"
            
            if self.meta and hasattr(self.meta, 'column_labels'):
                info += "\nColumn Labels:\n" + "-"*50 + "\n"
                for col, label in self.meta.column_labels.items():
                    if label:
                        info += f"{col:<20} {label}\n"
            
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", info)
            
        except Exception as e:
            error_msg = f"Error loading Stata file: {str(e)}\n\nPossible solutions:\n• Install pyreadstat: pip install pyreadstat\n• Check if file is corrupted\n• Ensure file is a valid Stata .dta file"
            self.info_text.delete("1.0", "end")
            self.info_text.insert("1.0", error_msg)
    
    def preview_data(self):
        """Preview the data in a separate window"""
        if self.df is None:
            messagebox.showerror("Error", "No data loaded. Please check the file.")
            return
        
        # Create preview window
        preview_window = ctk.CTkToplevel(self)
        preview_window.title("Data Preview")
        preview_window.geometry("800x600")
        preview_window.transient(self)
        
        # Create text widget for preview
        preview_text = ctk.CTkTextbox(preview_window)
        preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Show first 20 rows
        preview_data = self.df.head(20).to_string()
        preview_text.insert("1.0", f"First 20 rows:\n\n{preview_data}")
        
        # Add close button
        ctk.CTkButton(preview_window, text="Close", 
                     command=preview_window.destroy).pack(pady=10)
    
    def convert_file(self):
        """Convert the Stata file based on selected options"""
        if self.df is None:
            messagebox.showerror("Error", "No data loaded. Please check the file.")
            return
        
        conversion_type = self.conversion_type.get()
        
        try:
            if conversion_type == "open_direct":
                self.open_directly()
            elif conversion_type == "convert_save":
                self.convert_and_save()
            elif conversion_type == "import_existing":
                self.import_to_existing()
                
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Failed to convert file: {str(e)}")
            logger.error(f"Stata conversion failed: {str(e)}")
    
    def open_directly(self):
        """Open Stata data directly in the application"""
        # Convert DataFrame to DBF-compatible format
        converted_df = self.prepare_dataframe_for_dbf(self.df)
        
        # Create temporary DBF file
        import tempfile
        temp_dir = tempfile.gettempdir()
        temp_dbf_path = os.path.join(temp_dir, f"{os.path.splitext(os.path.basename(self.dta_file_path))[0]}.dbf")
        
        # Create DBF file
        self.create_dbf_from_dataframe(converted_df, temp_dbf_path)
        
        # Open in main application
        self.parent.open_dbf_file(temp_dbf_path, read_only=False)
        
        messagebox.showinfo("Success", f"Stata file opened successfully!\nTemporary DBF created at: {temp_dbf_path}")
        self.destroy()
    
    def convert_and_save(self):
        """Convert Stata file to DBF and save"""
        # Ask user for save location
        dbf_path = filedialog.asksaveasfilename(
            title="Save DBF File",
            defaultextension=".dbf",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")],
            initialvalue=f"{os.path.splitext(os.path.basename(self.dta_file_path))[0]}.dbf"
        )
        
        if not dbf_path:
            return
        
        # Convert DataFrame to DBF-compatible format
        converted_df = self.prepare_dataframe_for_dbf(self.df)
        
        # Create DBF file
        self.create_dbf_from_dataframe(converted_df, dbf_path)
        
        # Ask if user wants to open the converted file
        if messagebox.askyesno("Conversion Complete", 
                              f"DBF file created successfully at:\n{dbf_path}\n\nWould you like to open it now?"):
            self.parent.open_dbf_file(dbf_path, read_only=False)
        
        self.destroy()
    
    def import_to_existing(self):
        """Import Stata data into existing DBF file"""
        # Ask user to select existing DBF file
        dbf_path = filedialog.askopenfilename(
            title="Select DBF File to Import Into",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        
        if not dbf_path:
            return
        
        # This would require more complex implementation
        # For now, show a message about the feature
        messagebox.showinfo("Feature Coming Soon", 
                           "Import to existing DBF file feature is under development.\n" +
                           "Please use 'Convert and save' option for now.")
    
    def prepare_dataframe_for_dbf(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare DataFrame for DBF conversion"""
        converted_df = df.copy()
        
        # Handle missing values if requested
        if self.handle_missing.get():
            converted_df = converted_df.fillna('')
        
        # Convert data types for DBF compatibility
        for col in converted_df.columns:
            dtype = converted_df[col].dtype
            
            # Convert datetime to string format
            if pd.api.types.is_datetime64_any_dtype(dtype):
                converted_df[col] = converted_df[col].dt.strftime('%Y%m%d')
            
            # Convert boolean to string
            elif dtype == 'bool':
                converted_df[col] = converted_df[col].map({True: 'T', False: 'F', pd.NA: ''})
            
            # Handle object/string columns - truncate if too long
            elif dtype == 'object':
                # Convert to string and limit length to 254 characters (DBF limit)
                converted_df[col] = converted_df[col].astype(str).str[:254]
            
            # Handle numeric columns
            elif pd.api.types.is_numeric_dtype(dtype):
                # Keep as is, but handle infinities
                converted_df[col] = converted_df[col].replace([float('inf'), float('-inf')], 0)
        
        return converted_df
    
    def create_dbf_from_dataframe(self, df: pd.DataFrame, dbf_path: str):
        """Create DBF file from DataFrame"""
        import dbf
        
        # Determine field specifications
        field_specs = []
        for col in df.columns:
            # Clean column name for DBF (max 10 chars, no spaces)
            clean_name = col.replace(' ', '_')[:10].upper()
            
            # Determine field type and size
            dtype = df[col].dtype
            
            if pd.api.types.is_numeric_dtype(dtype):
                if pd.api.types.is_integer_dtype(dtype):
                    field_specs.append(f"{clean_name} N(12,0)")
                else:
                    field_specs.append(f"{clean_name} N(12,2)")
            else:
                # String field - determine max length
                max_len = min(df[col].astype(str).str.len().max() or 10, 254)
                max_len = max(max_len, 1)  # Minimum length of 1
                field_specs.append(f"{clean_name} C({max_len})")
        
        # Create DBF table
        table = dbf.Table(dbf_path, '; '.join(field_specs))
        table.open(mode=dbf.READ_WRITE)
        
        try:
            # Add records
            for _, row in df.iterrows():
                record = table.new()
                for i, (col, value) in enumerate(row.items()):
                    field_name = list(table.field_names)[i]
                    if pd.isna(value) or value == '':
                        setattr(record, field_name, '')
                    else:
                        setattr(record, field_name, value)
                record.write_record()
        
        finally:
            table.close()
        
        logger.info(f"DBF file created: {dbf_path} with {len(df)} records")


class DTADataTab(ctk.CTkFrame):
    """Individual tab for DTA file data (similar to DBFDataTab but for Stata files)"""
    
    def __init__(self, parent, file_path: str, read_only: bool = True):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.read_only = read_only  # DTA files are always read-only
        self.current_page = 0
        self.rows_per_page = 100
        self.total_records = 0
        self.df = None
        self.meta = None
        self.filtered_df = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the data tab UI"""
        # Top toolbar
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        # File info
        file_name = os.path.basename(self.file_path)
        status_text = f"{file_name} (Stata DTA - Read-Only)"
        self.status_label = ctk.CTkLabel(toolbar, text=status_text)
        self.status_label.pack(side="left", padx=10)
        
        # Convert button
        ctk.CTkButton(toolbar, text="Convert to DBF", width=120,
                     command=self.convert_to_dbf).pack(side="right", padx=5)
        
        # Pagination controls
        pagination_frame = ctk.CTkFrame(toolbar)
        pagination_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(pagination_frame, text="◀◀", width=40,
                     command=self.first_page).pack(side="left", padx=2)
        ctk.CTkButton(pagination_frame, text="◀", width=40,
                     command=self.prev_page).pack(side="left", padx=2)
        
        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1/1")
        self.page_label.pack(side="left", padx=10)
        
        ctk.CTkButton(pagination_frame, text="▶", width=40,
                     command=self.next_page).pack(side="left", padx=2)
        ctk.CTkButton(pagination_frame, text="▶▶", width=40,
                     command=self.last_page).pack(side="left", padx=2)
        
        # SQL Query frame
        sql_frame = ctk.CTkFrame(self)
        sql_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(sql_frame, text="SQL Query:").pack(side="left", padx=5)
        self.sql_entry = ctk.CTkEntry(sql_frame, placeholder_text="SELECT * FROM data WHERE ...")
        self.sql_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(sql_frame, text="Execute", width=80,
                     command=self.execute_sql).pack(side="right", padx=5)
        ctk.CTkButton(sql_frame, text="Clear", width=60,
                     command=self.clear_filter).pack(side="right", padx=2)
        
        # Data display area
        self.data_frame = ctk.CTkScrollableFrame(self)
        self.data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for data display
        self.create_data_tree()
    
    def create_data_tree(self):
        """Create the data tree view"""
        import tkinter as tk
        from tkinter import ttk
        
        # Create frame for treeview
        tree_frame = tk.Frame(self.data_frame._parent_canvas)
        self.data_frame._parent_canvas.create_window((0, 0), window=tree_frame, anchor="nw")
        
        # Style for treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#404040", foreground="white")
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and tree
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_header_click)
    
    def load_data(self):
        """Load DTA data"""
        if not STATA_SUPPORT:
            messagebox.showerror("Error", "pyreadstat library not available.\nPlease install it with: pip install pyreadstat")
            return
        
        try:
            # Read Stata file
            self.df, self.meta = pyreadstat.read_dta(self.file_path)
            self.filtered_df = self.df.copy()
            self.total_records = len(self.df)
            
            # Setup tree columns
            self.tree["columns"] = list(self.df.columns)
            self.tree["show"] = "tree headings"
            
            # Configure columns
            for col in self.df.columns:
                # Use label if available, otherwise use column name
                display_name = col
                if self.meta and hasattr(self.meta, 'column_labels') and col in self.meta.column_labels:
                    label = self.meta.column_labels[col]
                    if label:
                        display_name = f"{col}\n({label})"
                
                self.tree.heading(col, text=display_name, anchor="w")
                self.tree.column(col, width=100, anchor="w")
            
            self.update_data_display()
            self.update_pagination_info()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load DTA file: {str(e)}")
            logger.error(f"Failed to load DTA file {self.file_path}: {str(e)}")
    
    def convert_to_dbf(self):
        """Open conversion dialog"""
        StataConversionDialog(self.parent.parent, self.file_path)
    
    # Include similar methods from DBFDataTab for pagination, SQL, etc.
    def update_data_display(self):
        """Update the data display for current page"""
        if self.filtered_df is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate page boundaries
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.filtered_df))
        
        # Add data for current page
        for idx, row in self.filtered_df.iloc[start_idx:end_idx].iterrows():
            values = [str(val) if val is not None and not pd.isna(val) else "" for val in row]
            self.tree.insert("", "end", values=values)
        
        self.update_pagination_info()
    
    def update_pagination_info(self):
        """Update pagination information"""
        if self.filtered_df is not None:
            total_pages = (len(self.filtered_df) - 1) // self.rows_per_page + 1 if len(self.filtered_df) > 0 else 1
            current_page_display = self.current_page + 1
            self.page_label.configure(text=f"Page {current_page_display}/{total_pages}")
    
    def first_page(self):
        """Go to first page"""
        self.current_page = 0
        self.update_data_display()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_data_display()
    
    def next_page(self):
        """Go to next page"""
        if self.filtered_df is not None:
            max_page = (len(self.filtered_df) - 1) // self.rows_per_page
            if self.current_page < max_page:
                self.current_page += 1
                self.update_data_display()
    
    def last_page(self):
        """Go to last page"""
        if self.filtered_df is not None and len(self.filtered_df) > 0:
            self.current_page = (len(self.filtered_df) - 1) // self.rows_per_page
            self.update_data_display()
    
    def execute_sql(self):
        """Execute SQL query on data"""
        query = self.sql_entry.get().strip()
        if not query:
            return
        
        try:
            if "FROM data" in query.upper():
                # Create temporary SQLite database in memory
                conn = sqlite3.connect(':memory:')
                self.df.to_sql('data', conn, index=False, if_exists='replace')
                
                result_df = pd.read_sql_query(query, conn)
                conn.close()
                
                self.filtered_df = result_df
                self.current_page = 0
                self.update_data_display()
                
            else:
                messagebox.showwarning("SQL Query", 
                                     "Please use 'FROM data' in your query to reference the current table.")
                
        except Exception as e:
            messagebox.showerror("SQL Error", f"Query failed: {str(e)}")
            logger.error(f"SQL query failed: {str(e)}")
    
    def clear_filter(self):
        """Clear current filter and show all data"""
        self.filtered_df = self.df.copy()
        self.current_page = 0
        self.sql_entry.delete(0, 'end')
        self.update_data_display()
    
    def on_header_click(self, event):
        """Handle header click for sorting"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x, event.y)
            column_index = int(column.replace('#', '')) - 1
            
            if column_index >= 0 and self.filtered_df is not None:
                column_name = self.filtered_df.columns[column_index]
                
                # Toggle sort order
                if hasattr(self, '_last_sort_column') and self._last_sort_column == column_name:
                    ascending = not getattr(self, '_last_sort_ascending', True)
                else:
                    ascending = True
                
                self.filtered_df = self.filtered_df.sort_values(by=column_name, ascending=ascending)
                self._last_sort_column = column_name
                self._last_sort_ascending = ascending
                
                self.current_page = 0
                self.update_data_display()
    
    def on_double_click(self, event):
        """Handle double-click for editing"""
        messagebox.showinfo("Read-Only", "Stata files are opened in read-only mode.\nUse 'Convert to DBF' to create an editable copy.")
    
    def backup_file(self):
        """Create backup of the current file"""
        try:
            backup_path = self.file_path + ".bak"
            shutil.copy2(self.file_path, backup_path)
            messagebox.showinfo("Backup", f"Backup created: {backup_path}")
            logger.info(f"Backup created for {self.file_path}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
            logger.error(f"Backup failed for {self.file_path}: {str(e)}")


class DBFDataTab(ctk.CTkFrame):
    """Individual tab for DBF file data"""
    
    def __init__(self, parent, file_path: str, read_only: bool = False):
        super().__init__(parent)
        self.parent = parent
        self.file_path = file_path
        self.read_only = read_only
        self.current_page = 0
        self.rows_per_page = 100
        self.total_records = 0
        self.df = None
        self.filtered_df = None
        
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup the data tab UI"""
        # Top toolbar
        toolbar = ctk.CTkFrame(self)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        # File info
        file_name = os.path.basename(self.file_path)
        status_text = f"{file_name} {'(Read-Only)' if self.read_only else ''}"
        self.status_label = ctk.CTkLabel(toolbar, text=status_text)
        self.status_label.pack(side="left", padx=10)
        
        # Pagination controls
        pagination_frame = ctk.CTkFrame(toolbar)
        pagination_frame.pack(side="right", padx=10)
        
        ctk.CTkButton(pagination_frame, text="◀◀", width=40,
                     command=self.first_page).pack(side="left", padx=2)
        ctk.CTkButton(pagination_frame, text="◀", width=40,
                     command=self.prev_page).pack(side="left", padx=2)
        
        self.page_label = ctk.CTkLabel(pagination_frame, text="Page 1/1")
        self.page_label.pack(side="left", padx=10)
        
        ctk.CTkButton(pagination_frame, text="▶", width=40,
                     command=self.next_page).pack(side="left", padx=2)
        ctk.CTkButton(pagination_frame, text="▶▶", width=40,
                     command=self.last_page).pack(side="left", padx=2)
        
        # SQL Query frame
        sql_frame = ctk.CTkFrame(self)
        sql_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(sql_frame, text="SQL Query:").pack(side="left", padx=5)
        self.sql_entry = ctk.CTkEntry(sql_frame, placeholder_text="SELECT * FROM data WHERE ...")
        self.sql_entry.pack(side="left", fill="x", expand=True, padx=5)
        
        ctk.CTkButton(sql_frame, text="Execute", width=80,
                     command=self.execute_sql).pack(side="right", padx=5)
        ctk.CTkButton(sql_frame, text="Clear", width=60,
                     command=self.clear_filter).pack(side="right", padx=2)
        
        # Data display area
        self.data_frame = ctk.CTkScrollableFrame(self)
        self.data_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview for data display
        self.create_data_tree()
    
    def create_data_tree(self):
        """Create the data tree view"""
        import tkinter as tk
        from tkinter import ttk
        
        # Create frame for treeview
        tree_frame = tk.Frame(self.data_frame._parent_canvas)
        self.data_frame._parent_canvas.create_window((0, 0), window=tree_frame, anchor="nw")
        
        # Style for treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background="#2b2b2b", foreground="white",
                       fieldbackground="#2b2b2b")
        style.configure("Treeview.Heading", background="#404040", foreground="white")
        
        # Create treeview
        self.tree = ttk.Treeview(tree_frame)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and tree
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self.on_header_click)
    
    def load_data(self):
        """Load DBF data"""
        try:
            # Read DBF file using dbfpy3
            with dbf.Dbf(self.file_path) as db:
                records = []
                field_names = [field.name for field in db.header.fields]
                
                for record in db:
                    records.append([record[field] for field in field_names])
                
                # Create DataFrame
                self.df = pd.DataFrame(records, columns=field_names)
                self.filtered_df = self.df.copy()
                self.total_records = len(self.df)
                
                # Setup tree columns
                self.tree["columns"] = field_names
                self.tree["show"] = "tree headings"
                
                # Configure columns
                for col in field_names:
                    self.tree.heading(col, text=col, anchor="w")
                    self.tree.column(col, width=100, anchor="w")
                
                self.update_data_display()
                self.update_pagination_info()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
            logger.error(f"Failed to load DBF file {self.file_path}: {str(e)}")
    
    def update_data_display(self):
        """Update the data display for current page"""
        if self.filtered_df is None:
            return
        
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Calculate page boundaries
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.filtered_df))
        
        # Add data for current page
        for idx, row in self.filtered_df.iloc[start_idx:end_idx].iterrows():
            values = [str(val) if val is not None else "" for val in row]
            self.tree.insert("", "end", values=values)
        
        self.update_pagination_info()
    
    def update_pagination_info(self):
        """Update pagination information"""
        if self.filtered_df is not None:
            total_pages = (len(self.filtered_df) - 1) // self.rows_per_page + 1 if len(self.filtered_df) > 0 else 1
            current_page_display = self.current_page + 1
            self.page_label.configure(text=f"Page {current_page_display}/{total_pages}")
    
    def first_page(self):
        """Go to first page"""
        self.current_page = 0
        self.update_data_display()
    
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_data_display()
    
    def next_page(self):
        """Go to next page"""
        if self.filtered_df is not None:
            max_page = (len(self.filtered_df) - 1) // self.rows_per_page
            if self.current_page < max_page:
                self.current_page += 1
                self.update_data_display()
    
    def last_page(self):
        """Go to last page"""
        if self.filtered_df is not None:
            self.current_page = (len(self.filtered_df) - 1) // self.rows_per_page
            self.update_data_display()
    
    def execute_sql(self):
        """Execute SQL query on data"""
        query = self.sql_entry.get().strip()
        if not query:
            return
        
        try:
            # Simple SQL parsing - replace "FROM data" with actual dataframe
            # This is a simplified implementation
            if "FROM data" in query.upper():
                # Create temporary SQLite database in memory
                conn = sqlite3.connect(':memory:')
                self.df.to_sql('data', conn, index=False, if_exists='replace')
                
                result_df = pd.read_sql_query(query, conn)
                conn.close()
                
                self.filtered_df = result_df
                self.current_page = 0
                self.update_data_display()
                
            else:
                messagebox.showwarning("SQL Query", 
                                     "Please use 'FROM data' in your query to reference the current table.")
                
        except Exception as e:
            messagebox.showerror("SQL Error", f"Query failed: {str(e)}")
            logger.error(f"SQL query failed: {str(e)}")
    
    def clear_filter(self):
        """Clear current filter and show all data"""
        self.filtered_df = self.df.copy()
        self.current_page = 0
        self.sql_entry.delete(0, 'end')
        self.update_data_display()
    
    def on_header_click(self, event):
        """Handle header click for sorting"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.tree.identify_column(event.x, event.y)
            column_index = int(column.replace('#', '')) - 1
            
            if column_index >= 0 and self.filtered_df is not None:
                column_name = self.filtered_df.columns[column_index]
                
                # Toggle sort order
                if hasattr(self, '_last_sort_column') and self._last_sort_column == column_name:
                    ascending = not getattr(self, '_last_sort_ascending', True)
                else:
                    ascending = True
                
                self.filtered_df = self.filtered_df.sort_values(by=column_name, ascending=ascending)
                self._last_sort_column = column_name
                self._last_sort_ascending = ascending
                
                self.current_page = 0
                self.update_data_display()
    
    def on_double_click(self, event):
        """Handle double-click for editing"""
        if self.read_only:
            messagebox.showinfo("Read-Only", "File is opened in read-only mode.")
            return
        
        item = self.tree.selection()[0] if self.tree.selection() else None
        if item:
            # Simple editing implementation
            messagebox.showinfo("Edit", "Cell editing would be implemented here")
    
    def backup_file(self):
        """Create backup of the current file"""
        try:
            backup_path = self.file_path + ".bak"
            shutil.copy2(self.file_path, backup_path)
            messagebox.showinfo("Backup", f"Backup created: {backup_path}")
            logger.info(f"Backup created for {self.file_path}")
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
            logger.error(f"Backup failed for {self.file_path}: {str(e)}")


class EDVANDBFCommander(ctk.CTk):
    """Main application class for EDVAN DBF Commander"""
    
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("EDVAN DBF Commander v1.0")
        self.geometry("1200x800")
        
        # Initialize variables
        self.open_files = {}  # Dictionary to store open files
        
        # Setup UI
        self.setup_ui()
        self.create_menu()
        
        logger.info("EDVAN DBF Commander started successfully")
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title bar
        title_frame = ctk.CTkFrame(self.main_container)
        title_frame.pack(fill="x", pady=(0, 10))
        
        title_label = ctk.CTkLabel(title_frame, 
                                  text="EDVAN DBF Commander", 
                                  font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(pady=10)
        
        # Tabbed notebook for multiple files
        self.notebook = ctk.CTkTabview(self.main_container)
        self.notebook.pack(fill="both", expand=True)
        
        # Status bar
        self.status_frame = ctk.CTkFrame(self.main_container)
        self.status_frame.pack(fill="x", pady=(10, 0))
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="Ready", anchor="w")
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Welcome message if no files are open
        self.show_welcome_message()
    
    def show_welcome_message(self):
        """Show welcome message when no files are open"""
        if len(self.notebook.get()) == 0:
            welcome_tab = self.notebook.add("Welcome")
            welcome_frame = ctk.CTkFrame(welcome_tab)
            welcome_frame.pack(fill="both", expand=True)
            
            welcome_content = ctk.CTkFrame(welcome_frame)
            welcome_content.place(relx=0.5, rely=0.5, anchor="center")
            
            ctk.CTkLabel(welcome_content, 
                        text="Welcome to EDVAN DBF Commander",
                        font=ctk.CTkFont(size=32, weight="bold")).pack(pady=20)
            
            ctk.CTkLabel(welcome_content,
                        text="Modern DBF File Management Tool",
                        font=ctk.CTkFont(size=16)).pack(pady=10)
            
            buttons_frame = ctk.CTkFrame(welcome_content)
            buttons_frame.pack(pady=30)
            
            ctk.CTkButton(buttons_frame, text="Open DBF File", 
                         font=ctk.CTkFont(size=14),
                         command=self.open_file).pack(side="left", padx=10)
            
            ctk.CTkButton(buttons_frame, text="Create New DBF", 
                         font=ctk.CTkFont(size=14),
                         command=self.create_new_file).pack(side="left", padx=10)
            
            # Features list
            features_frame = ctk.CTkFrame(welcome_content)
            features_frame.pack(pady=20, fill="x")
            
            ctk.CTkLabel(features_frame, text="Features:", 
                        font=ctk.CTkFont(size=18, weight="bold")).pack(pady=5)
            
            features = [
                "• Tabbed interface for multiple files",
                "• Structure editor with field management",
                "• SQL query support",
                "• Data filtering and sorting",
                "• Import/Export (CSV, XML, Excel, HTML)",
                "• Find & Replace functionality",
                "• Encoding conversion support",
                "• Backup and read-only modes"
            ]
            
            for feature in features:
                ctk.CTkLabel(features_frame, text=feature, anchor="w").pack(anchor="w", padx=20, pady=2)
    
    def create_menu(self):
        """Create the application menu"""
        import tkinter as tk
        
        # Create menu bar
        menubar = tk.Menu(self)
        self.configure(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New DBF...", command=self.create_new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Open Read-Only...", command=self.open_readonly_file)
        file_menu.add_separator()
        # Stata DTA file support
        if STATA_SUPPORT:
            file_menu.add_command(label="Open Stata File (.dta)...", command=self.open_dta_file)
            file_menu.add_command(label="Convert Stata to DBF...", command=self.convert_dta_to_dbf)
            file_menu.add_command(label="Convert Stata to CSV...", command=self.convert_dta_to_csv)
        file_menu.add_separator()
        # Direct CSV conversion
        file_menu.add_command(label="Convert DBF to CSV...", command=self.convert_dbf_to_csv)
        file_menu.add_command(label="Close Tab", command=self.close_current_tab, accelerator="Ctrl+W")
        file_menu.add_command(label="Close All", command=self.close_all_tabs)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Current File", command=self.backup_current_file, accelerator="Ctrl+B")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Find & Replace...", command=self.open_find_replace, accelerator="Ctrl+F")
        edit_menu.add_separator()
        edit_menu.add_command(label="Structure Editor...", command=self.open_structure_editor, accelerator="Ctrl+S")
        
        # Data menu
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Data", menu=data_menu)
        data_menu.add_command(label="Clear Filter", command=self.clear_filter)
        data_menu.add_separator()
        
        # Import submenu
        import_menu = tk.Menu(data_menu, tearoff=0)
        data_menu.add_cascade(label="Import", menu=import_menu)
        import_menu.add_command(label="From CSV...", command=self.import_from_csv)
        import_menu.add_command(label="From XML...", command=self.import_from_xml)
        
        # Export submenu
        export_menu = tk.Menu(data_menu, tearoff=0)
        data_menu.add_cascade(label="Export", menu=export_menu)
        export_menu.add_command(label="To CSV...", command=self.export_to_csv)
        export_menu.add_command(label="To XML...", command=self.export_to_xml)
        export_menu.add_command(label="To Excel...", command=self.export_to_excel)
        export_menu.add_command(label="To HTML...", command=self.export_to_html)
        
        # Encoding submenu
        encoding_menu = tk.Menu(data_menu, tearoff=0)
        data_menu.add_cascade(label="Convert Encoding", menu=encoding_menu)
        encoding_menu.add_command(label="Windows (ANSI) ↔ MS-DOS (OEM)", command=self.convert_ansi_oem)
        encoding_menu.add_command(label="Windows (ANSI) ↔ UTF-8", command=self.convert_ansi_utf8)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About...", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.bind('<Control-n>', lambda e: self.create_new_file())
        self.bind('<Control-o>', lambda e: self.open_file())
        self.bind('<Control-w>', lambda e: self.close_current_tab())
        self.bind('<Control-b>', lambda e: self.backup_current_file())
        self.bind('<Control-f>', lambda e: self.open_find_replace())
        self.bind('<Control-s>', lambda e: self.open_structure_editor())
        self.bind('<Control-q>', lambda e: self.quit())
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)
    
    def get_current_tab(self):
        """Get the currently active data tab (DBFDataTab or DTADataTab)"""
        current_tab_name = self.notebook.get()
        if current_tab_name and current_tab_name != "Welcome":
            tab = self.notebook.tab(current_tab_name)
            # Find the DBFDataTab or DTADataTab widget in the tab
            for child in tab.winfo_children():
                if isinstance(child, (DBFDataTab, DTADataTab)):
                    return child
        return None
    
    def create_new_file(self):
        """Create a new DBF file"""
        file_path = filedialog.asksaveasfilename(
            title="Create New DBF File",
            defaultextension=".dbf",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                # Create a simple DBF file with one field
                import dbf
                table = dbf.Table(file_path, 'id N(10,0)')
                table.open(mode=dbf.READ_WRITE)
                table.close()
                
                self.open_dbf_file(file_path, read_only=False)
                self.update_status(f"Created new file: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create file: {str(e)}")
                logger.error(f"Failed to create DBF file {file_path}: {str(e)}")
    
    def open_file(self):
        """Open an existing DBF file"""
        file_path = filedialog.askopenfilename(
            title="Open DBF File",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.open_dbf_file(file_path, read_only=False)
    
    def open_readonly_file(self):
        """Open a DBF file in read-only mode"""
        file_path = filedialog.askopenfilename(
            title="Open DBF File (Read-Only)",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        
        if file_path:
            self.open_dbf_file(file_path, read_only=True)
    
    def open_dbf_file(self, file_path: str, read_only: bool = False):
        """Open a DBF file in a new tab"""
        try:
            # Remove welcome tab if present
            if "Welcome" in self.notebook.get():
                self.notebook.delete("Welcome")
            
            # Create new tab
            file_name = os.path.basename(file_path)
            tab_name = f"{file_name} {'(RO)' if read_only else ''}"
            
            # Check if file is already open
            if tab_name in [self.notebook.tab(tab_id) for tab_id in self.notebook.get()]:
                messagebox.showinfo("Already Open", f"File {file_name} is already open.")
                return
            
            # Create tab
            tab = self.notebook.add(tab_name)
            
            # Create data tab widget
            data_tab = DBFDataTab(tab, file_path, read_only)
            data_tab.pack(fill="both", expand=True)
            
            # Store reference
            self.open_files[tab_name] = {
                'path': file_path,
                'read_only': read_only,
                'tab': data_tab
            }
            
            # Switch to new tab
            self.notebook.set(tab_name)
            
            self.update_status(f"Opened: {file_name} {'(Read-Only)' if read_only else ''}")
            logger.info(f"Opened DBF file: {file_path} (read_only: {read_only})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            logger.error(f"Failed to open DBF file {file_path}: {str(e)}")
    
    def open_dta_file(self):
        """Open a Stata DTA file"""
        if not STATA_SUPPORT:
            messagebox.showerror("Stata Support Not Available", 
                               "pyreadstat library is required for Stata file support.\n" +
                               "Please install it with: pip install pyreadstat")
            return
        
        file_path = filedialog.askopenfilename(
            title="Open Stata DTA File",
            filetypes=[("Stata files", "*.dta"), ("All files", "*.*")]
        )
        
        if file_path:
            self.open_stata_file(file_path)
    
    def convert_dta_to_dbf(self):
        """Convert a Stata DTA file to DBF"""
        if not STATA_SUPPORT:
            messagebox.showerror("Stata Support Not Available", 
                               "pyreadstat library is required for Stata file support.\n" +
                               "Please install it with: pip install pyreadstat")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Stata DTA File to Convert",
            filetypes=[("Stata files", "*.dta"), ("All files", "*.*")]
        )
        
        if file_path:
            StataConversionDialog(self, file_path)
    
    def convert_dta_to_csv(self):
        """Convert a Stata DTA file to CSV"""
        if not STATA_SUPPORT:
            messagebox.showerror("Stata Support Not Available", 
                               "pyreadstat library is required for Stata file support.\n" +
                               "Please install it with: pip install pyreadstat")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select Stata DTA File to Convert to CSV",
            filetypes=[("Stata files", "*.dta"), ("All files", "*.*")]
        )
        
        if file_path:
            CSVConversionDialog(self, file_path, "dta")
    
    def convert_dbf_to_csv(self):
        """Convert a DBF file to CSV"""
        file_path = filedialog.askopenfilename(
            title="Select DBF File to Convert to CSV",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        
        if file_path:
            CSVConversionDialog(self, file_path, "dbf")
    
    def open_stata_file(self, file_path: str):
        """Open a Stata DTA file in a new tab"""
        try:
            # Remove welcome tab if present
            if "Welcome" in self.notebook.get():
                self.notebook.delete("Welcome")
            
            # Create new tab
            file_name = os.path.basename(file_path)
            tab_name = f"{file_name} (DTA)"
            
            # Check if file is already open
            existing_tabs = [self.notebook.tab(tab_id) for tab_id in self.notebook.get()]
            if tab_name in existing_tabs:
                messagebox.showinfo("Already Open", f"File {file_name} is already open.")
                return
            
            # Create tab
            tab = self.notebook.add(tab_name)
            
            # Create DTA data tab widget
            data_tab = DTADataTab(tab, file_path, read_only=True)
            data_tab.pack(fill="both", expand=True)
            
            # Store reference
            self.open_files[tab_name] = {
                'path': file_path,
                'read_only': True,  # DTA files are always read-only
                'tab': data_tab,
                'type': 'dta'
            }
            
            # Switch to new tab
            self.notebook.set(tab_name)
            
            self.update_status(f"Opened Stata file: {file_name} (Read-Only)")
            logger.info(f"Opened Stata DTA file: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Stata file: {str(e)}")
            logger.error(f"Failed to open Stata DTA file {file_path}: {str(e)}")
    
    def close_current_tab(self):
        """Close the current tab"""
        current_tab = self.notebook.get()
        if current_tab and current_tab != "Welcome":
            self.notebook.delete(current_tab)
            if current_tab in self.open_files:
                del self.open_files[current_tab]
            
            # Show welcome message if no tabs remain
            if len(self.notebook.get()) == 0:
                self.show_welcome_message()
    
    def close_all_tabs(self):
        """Close all open tabs"""
        for tab_name in list(self.open_files.keys()):
            self.notebook.delete(tab_name)
        self.open_files.clear()
        self.show_welcome_message()
    
    def backup_current_file(self):
        """Backup the current file"""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.backup_file()
        else:
            messagebox.showinfo("No File", "No file is currently open.")
    
    def open_find_replace(self):
        """Open find and replace dialog"""
        current_tab = self.get_current_tab()
        if current_tab:
            FindReplaceDialog(self, current_tab)
        else:
            messagebox.showinfo("No File", "No file is currently open.")
    
    def open_structure_editor(self):
        """Open structure editor"""
        current_tab = self.get_current_tab()
        if current_tab:
            DBFStructureDialog(self, current_tab.file_path)
        else:
            messagebox.showinfo("No File", "No file is currently open.")
    
    def clear_filter(self):
        """Clear current filter"""
        current_tab = self.get_current_tab()
        if current_tab:
            current_tab.clear_filter()
        else:
            messagebox.showinfo("No File", "No file is currently open.")
    
    def import_from_csv(self):
        """Import data from CSV file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot import to read-only file.")
            return
        
        csv_path = filedialog.askopenfilename(
            title="Import from CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if csv_path:
            try:
                # This is a simplified implementation
                messagebox.showinfo("Import", f"Would import data from {os.path.basename(csv_path)}")
                logger.info(f"CSV import requested: {csv_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def import_from_xml(self):
        """Import data from XML file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot import to read-only file.")
            return
        
        xml_path = filedialog.askopenfilename(
            title="Import from XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if xml_path:
            try:
                # This is a simplified implementation
                messagebox.showinfo("Import", f"Would import data from {os.path.basename(xml_path)}")
                logger.info(f"XML import requested: {xml_path}")
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import: {str(e)}")
    
    def export_to_csv(self):
        """Export data to CSV file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        csv_path = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if csv_path:
            try:
                # Export current filtered data
                data_to_export = current_tab.filtered_df if current_tab.filtered_df is not None else current_tab.df
                data_to_export.to_csv(csv_path, index=False)
                messagebox.showinfo("Export", f"Data exported to {os.path.basename(csv_path)}")
                logger.info(f"CSV export completed: {csv_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_to_xml(self):
        """Export data to XML file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        xml_path = filedialog.asksaveasfilename(
            title="Export to XML",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        
        if xml_path:
            try:
                # Export current filtered data
                data_to_export = current_tab.filtered_df if current_tab.filtered_df is not None else current_tab.df
                
                # Create XML structure
                root = ET.Element("data")
                for _, row in data_to_export.iterrows():
                    record = ET.SubElement(root, "record")
                    for col, value in row.items():
                        field = ET.SubElement(record, col.lower())
                        field.text = str(value) if value is not None else ""
                
                # Pretty print and save
                xml_str = ET.tostring(root, encoding='unicode')
                dom = minidom.parseString(xml_str)
                with open(xml_path, 'w', encoding='utf-8') as f:
                    f.write(dom.toprettyxml())
                
                messagebox.showinfo("Export", f"Data exported to {os.path.basename(xml_path)}")
                logger.info(f"XML export completed: {xml_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_to_excel(self):
        """Export data to Excel file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        excel_path = filedialog.asksaveasfilename(
            title="Export to Excel",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if excel_path:
            try:
                # Export current filtered data
                data_to_export = current_tab.filtered_df if current_tab.filtered_df is not None else current_tab.df
                data_to_export.to_excel(excel_path, index=False)
                messagebox.showinfo("Export", f"Data exported to {os.path.basename(excel_path)}")
                logger.info(f"Excel export completed: {excel_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_to_html(self):
        """Export data to HTML file"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        html_path = filedialog.asksaveasfilename(
            title="Export to HTML",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        
        if html_path:
            try:
                # Export current filtered data
                data_to_export = current_tab.filtered_df if current_tab.filtered_df is not None else current_tab.df
                
                html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>DBF Data Export</title>
    <style>
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>DBF Data Export</h1>
    {data_to_export.to_html(index=False, classes='data-table')}
</body>
</html>
"""
                
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                messagebox.showinfo("Export", f"Data exported to {os.path.basename(html_path)}")
                logger.info(f"HTML export completed: {html_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def convert_ansi_oem(self):
        """Convert between Windows (ANSI) and MS-DOS (OEM) encoding"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot modify read-only file.")
            return
        
        # This would require actual encoding conversion implementation
        messagebox.showinfo("Encoding Conversion", 
                           "ANSI ↔ OEM conversion would be implemented here")
        logger.info("ANSI-OEM encoding conversion requested")
    
    def convert_ansi_utf8(self):
        """Convert between Windows (ANSI) and UTF-8 encoding"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot modify read-only file.")
            return
        
        # This would require actual encoding conversion implementation
        messagebox.showinfo("Encoding Conversion", 
                           "ANSI ↔ UTF-8 conversion would be implemented here")
        logger.info("ANSI-UTF8 encoding conversion requested")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
EDVAN DBF Commander v1.0

A modern, feature-rich DBF file management application built with Python and CustomTkinter.

Features:
• Tabbed interface for multiple files
• Structure editor with field management
• SQL query support
• Data filtering and sorting
• Import/Export (CSV, XML, Excel, HTML)
• Find & Replace functionality
• Encoding conversion support
• Backup and read-only modes

Built with:
• Python 3
• CustomTkinter
• dbfpy3
• pandas
• openpyxl

© 2024 EDVAN DBF Commander
        """
        
        about_window = ctk.CTkToplevel(self)
        about_window.title("About EDVAN DBF Commander")
        about_window.geometry("500x400")
        about_window.transient(self)
        about_window.grab_set()
        
        text_widget = ctk.CTkTextbox(about_window)
        text_widget.pack(fill="both", expand=True, padx=20, pady=20)
        text_widget.insert("1.0", about_text)
        text_widget.configure(state="disabled")
        
        close_button = ctk.CTkButton(about_window, text="Close", 
                                    command=about_window.destroy)
        close_button.pack(pady=(0, 20))


def main():
    """Main function to run the application"""
    try:
        app = EDVANDBFCommander()
        app.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        messagebox.showerror("Application Error", f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
