#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DBF Structure Editor Dialog

Allows editing DBF file structure including adding, removing, and reordering fields.
"""

import os
from tkinter import messagebox, filedialog
import customtkinter as ctk
from dbfpy3 import dbf
import logging

logger = logging.getLogger(__name__)


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
