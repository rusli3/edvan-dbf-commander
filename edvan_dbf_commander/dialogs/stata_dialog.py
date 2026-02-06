#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stata Conversion Dialog

Dialog for converting Stata .dta files to DBF or other formats.
"""

import os
import tempfile
from tkinter import messagebox, filedialog
import customtkinter as ctk
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Check for Stata support
STATA_SUPPORT = True
try:
    import pyreadstat
except ImportError:
    STATA_SUPPORT = False


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
