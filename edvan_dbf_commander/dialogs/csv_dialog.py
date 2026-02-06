#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV Conversion Dialog

Dialog for configuring and executing CSV conversion from DBF or DTA files.
"""

import os
import csv
from tkinter import messagebox, filedialog
import customtkinter as ctk
import pandas as pd
from dbfpy3 import dbf
import logging

logger = logging.getLogger(__name__)

# Check for Stata support
STATA_SUPPORT = True
try:
    import pyreadstat
except ImportError:
    STATA_SUPPORT = False


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
