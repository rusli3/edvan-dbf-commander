#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF Data Tab

Data tab component for viewing and editing DBF files.
Extends BaseDataTab with DBF-specific functionality.
"""

import os
from tkinter import messagebox
import customtkinter as ctk
import pandas as pd
from dbfpy3 import dbf
import logging

from .base_data_tab import BaseDataTab

logger = logging.getLogger(__name__)


class DBFDataTab(BaseDataTab):
    """Data tab for DBF files"""
    
    def __init__(self, parent, file_path: str, read_only: bool = False):
        super().__init__(parent, file_path, read_only)
    
    def setup_toolbar_buttons(self, toolbar):
        """Setup DBF-specific toolbar buttons"""
        if not self.read_only:
            ctk.CTkButton(toolbar, text="Add Record", width=100,
                         command=self.add_record).pack(side="right", padx=5)
            ctk.CTkButton(toolbar, text="Delete Selected", width=120,
                         command=self.delete_selected).pack(side="right", padx=5)
            ctk.CTkButton(toolbar, text="Save Changes", width=100,
                         command=self.save_changes).pack(side="right", padx=5)
    
    def load_data(self):
        """Load DBF data"""
        try:
            with dbf.Dbf(self.file_path) as db:
                records = []
                field_names = [field.name for field in db.header.fields]
                
                for record in db:
                    row_data = []
                    for field in field_names:
                        value = record[field]
                        row_data.append(value)
                    records.append(row_data)
                
                # Create DataFrame
                self.df = pd.DataFrame(records, columns=field_names)
                self.total_records = len(self.df)
                
            # Update display
            self.update_data_display()
            
            logger.info(f"Loaded DBF file: {self.file_path} ({self.total_records} records)")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load DBF file: {str(e)}")
            logger.error(f"Failed to load DBF file {self.file_path}: {str(e)}")
    
    def on_double_click(self, event):
        """Handle double-click for editing"""
        if self.read_only:
            return
        
        # Get selected item
        item = self.data_tree.identify_row(event.y)
        column = self.data_tree.identify_column(event.x)
        
        if item and column:
            col_index = int(column[1:]) - 1
            if col_index >= 0:
                self.edit_cell(item, col_index)
    
    def edit_cell(self, item, col_index):
        """Edit a cell value"""
        if self.read_only:
            return
        
        # Get current value
        values = self.data_tree.item(item, 'values')
        if col_index < len(values):
            current_value = values[col_index]
            col_name = self.df.columns[col_index]
            
            # Create edit dialog
            dialog = ctk.CTkInputDialog(
                text=f"Edit {col_name}:",
                title="Edit Cell"
            )
            new_value = dialog.get_input()
            
            if new_value is not None:
                # Update the dataframe
                row_index = self.data_tree.index(item) + (self.current_page * self.rows_per_page)
                self.df.at[row_index, col_name] = new_value
                self.modified = True
                
                # Refresh display
                self.update_data_display()
    
    def add_record(self):
        """Add a new record"""
        if self.read_only:
            messagebox.showinfo("Read-Only", "Cannot add records to read-only file")
            return
        
        # Create empty row with default values
        new_row = {col: '' for col in self.df.columns}
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.total_records = len(self.df)
        self.modified = True
        
        # Go to last page to show new record
        self.last_page()
    
    def delete_selected(self):
        """Delete selected records"""
        if self.read_only:
            messagebox.showinfo("Read-Only", "Cannot delete records from read-only file")
            return
        
        selected = self.data_tree.selection()
        if not selected:
            messagebox.showinfo("Delete", "Please select records to delete")
            return
        
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected)} selected record(s)?"):
            return
        
        # Get indices to delete
        indices_to_delete = []
        for item in selected:
            row_index = self.data_tree.index(item) + (self.current_page * self.rows_per_page)
            indices_to_delete.append(row_index)
        
        # Delete rows
        self.df = self.df.drop(indices_to_delete).reset_index(drop=True)
        self.total_records = len(self.df)
        self.modified = True
        
        # Refresh display
        self.update_data_display()
    
    def save_changes(self):
        """Save changes to the DBF file"""
        if self.read_only:
            messagebox.showinfo("Read-Only", "Cannot save read-only file")
            return
        
        if not self.modified:
            messagebox.showinfo("Save", "No changes to save")
            return
        
        try:
            # Create backup first
            self.backup_file()
            
            # Re-create DBF file with updated data
            import dbf as dbf_lib
            
            # Get field specs from original file
            with dbf.Dbf(self.file_path) as db:
                field_specs = []
                for field in db.header.fields:
                    if field.type == 'N':
                        field_specs.append(f"{field.name} N({field.length},{field.decimal_count})")
                    elif field.type == 'C':
                        field_specs.append(f"{field.name} C({field.length})")
                    elif field.type == 'D':
                        field_specs.append(f"{field.name} D")
                    elif field.type == 'L':
                        field_specs.append(f"{field.name} L")
                    elif field.type == 'M':
                        field_specs.append(f"{field.name} M")
            
            # Create new DBF file
            table = dbf_lib.Table(self.file_path, '; '.join(field_specs))
            table.open(mode=dbf_lib.READ_WRITE)
            
            # Add records
            for _, row in self.df.iterrows():
                record = table.new()
                for i, (col, value) in enumerate(row.items()):
                    field_name = list(table.field_names)[i]
                    if pd.isna(value) or value == '':
                        setattr(record, field_name, '')
                    else:
                        setattr(record, field_name, value)
                record.write_record()
            
            table.close()
            
            self.modified = False
            messagebox.showinfo("Save", "Changes saved successfully")
            logger.info(f"Changes saved to: {self.file_path}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save: {str(e)}")
            logger.error(f"Failed to save {self.file_path}: {str(e)}")
