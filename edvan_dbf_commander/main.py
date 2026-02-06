#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EDVAN DBF Commander - Main Application

Modern Desktop Application for DBF File Management.
This is the main application class with menu system and tab management.
"""

import os
import sys
import logging
from tkinter import messagebox, filedialog
import tkinter as tk
import customtkinter as ctk
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import local modules
from .dialogs import (
    DBFStructureDialog,
    FindReplaceDialog,
    CSVConversionDialog,
    StataConversionDialog
)
from .tabs import DBFDataTab, DTADataTab
from .utils import (
    convert_ansi_to_oem,
    convert_oem_to_ansi,
    convert_ansi_to_utf8,
    convert_utf8_to_ansi,
    import_csv_to_dbf,
    import_xml_to_dbf,
    cleanup_temp_files
)

# Check for Stata support
STATA_SUPPORT = True
try:
    import pyreadstat
except ImportError:
    STATA_SUPPORT = False
    logger.info("pyreadstat not available - Stata .dta support disabled")

# Set CustomTkinter appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class EDVANDBFCommander(ctk.CTk):
    """Main application class for EDVAN DBF Commander"""
    
    def __init__(self):
        super().__init__()
        
        # Configure main window
        self.title("EDVAN DBF Commander v1.1")
        self.geometry("1200x800")
        self.minsize(800, 600)
        
        # Track open files
        self.open_files = {}
        
        # Cleanup old temp files on startup
        cleanup_temp_files(max_age_hours=24)
        
        # Setup UI
        self.setup_ui()
        self.create_menu()
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabbed interface for multiple files
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
        if len(self.notebook._tab_dict) == 0:
            welcome_tab = self.notebook.add("Welcome")
            welcome_frame = ctk.CTkFrame(welcome_tab)
            welcome_frame.pack(fill="both", expand=True)
            
            welcome_content = ctk.CTkFrame(welcome_frame)
            welcome_content.place(relx=0.5, rely=0.5, anchor="center")
            
            ctk.CTkLabel(welcome_content, 
                        text="Welcome to EDVAN DBF Commander",
                        font=ctk.CTkFont(size=32, weight="bold")).pack(pady=20)
            
            ctk.CTkLabel(welcome_content,
                        text="Modern DBF File Management Tool v1.1",
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
        edit_menu.add_command(label="Structure Editor...", command=self.open_structure_editor)
        
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
        encoding_menu.add_command(label="Windows (ANSI) → MS-DOS (OEM)", command=self.convert_ansi_to_oem)
        encoding_menu.add_command(label="MS-DOS (OEM) → Windows (ANSI)", command=self.convert_oem_to_ansi)
        encoding_menu.add_separator()
        encoding_menu.add_command(label="Windows (ANSI) → UTF-8", command=self.convert_ansi_to_utf8)
        encoding_menu.add_command(label="UTF-8 → Windows (ANSI)", command=self.convert_utf8_to_ansi)
        
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
        self.bind('<Control-q>', lambda e: self.quit())
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.configure(text=message)
    
    def get_current_tab(self):
        """Get the currently active data tab (DBFDataTab or DTADataTab)"""
        current_tab_name = self.notebook.get()
        if current_tab_name and current_tab_name != "Welcome":
            if current_tab_name in self.open_files:
                return self.open_files[current_tab_name].get('tab')
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
            if "Welcome" in self.notebook._tab_dict:
                self.notebook.delete("Welcome")
            
            # Create new tab
            file_name = os.path.basename(file_path)
            tab_name = f"{file_name} {'(RO)' if read_only else ''}"
            
            # Check if file is already open
            if tab_name in self.open_files:
                messagebox.showinfo("Already Open", f"File {file_name} is already open.")
                self.notebook.set(tab_name)
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
                'tab': data_tab,
                'type': 'dbf'
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
    
    def open_stata_file(self, file_path: str):
        """Open a Stata DTA file in a new tab"""
        try:
            # Remove welcome tab if present
            if "Welcome" in self.notebook._tab_dict:
                self.notebook.delete("Welcome")
            
            # Create new tab
            file_name = os.path.basename(file_path)
            tab_name = f"{file_name} (DTA)"
            
            # Check if file is already open
            if tab_name in self.open_files:
                messagebox.showinfo("Already Open", f"File {file_name} is already open.")
                self.notebook.set(tab_name)
                return
            
            # Create tab
            tab = self.notebook.add(tab_name)
            
            # Create DTA data tab widget
            data_tab = DTADataTab(tab, file_path, read_only=True)
            data_tab.pack(fill="both", expand=True)
            
            # Store reference
            self.open_files[tab_name] = {
                'path': file_path,
                'read_only': True,
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
    
    def close_current_tab(self):
        """Close the current tab"""
        current_tab = self.notebook.get()
        if current_tab and current_tab != "Welcome":
            # Cleanup resources
            if current_tab in self.open_files:
                tab_info = self.open_files[current_tab]
                if 'tab' in tab_info and hasattr(tab_info['tab'], 'cleanup'):
                    tab_info['tab'].cleanup()
                del self.open_files[current_tab]
            
            self.notebook.delete(current_tab)
            
            # Show welcome message if no tabs remain
            if len(self.notebook._tab_dict) == 0:
                self.show_welcome_message()
    
    def close_all_tabs(self):
        """Close all open tabs"""
        for tab_name in list(self.open_files.keys()):
            tab_info = self.open_files[tab_name]
            if 'tab' in tab_info and hasattr(tab_info['tab'], 'cleanup'):
                tab_info['tab'].cleanup()
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
            if import_csv_to_dbf(csv_path, current_tab.file_path):
                # Reload data
                current_tab.load_data()
                messagebox.showinfo("Import", f"Data imported from {os.path.basename(csv_path)}")
    
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
            if import_xml_to_dbf(xml_path, current_tab.file_path):
                # Reload data
                current_tab.load_data()
                messagebox.showinfo("Import", f"Data imported from {os.path.basename(xml_path)}")
    
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
                data_to_export = current_tab.filtered_df if current_tab.filtered_df is not None else current_tab.df
                
                root = ET.Element("data")
                for _, row in data_to_export.iterrows():
                    record = ET.SubElement(root, "record")
                    for col, value in row.items():
                        field = ET.SubElement(record, str(col).lower())
                        field.text = str(value) if value is not None else ""
                
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
                data_to_export = current_tab.filtered_df if current_tab.filtered_df is not None else current_tab.df
                
                html_content = f"""<!DOCTYPE html>
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
    
    def convert_ansi_to_oem(self):
        """Convert from Windows ANSI to MS-DOS OEM encoding"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot modify read-only file.")
            return
        
        if messagebox.askyesno("Confirm Conversion", 
                              "Convert encoding from Windows (ANSI) to MS-DOS (OEM)?\n\n" +
                              "A backup will be created before conversion."):
            if convert_ansi_to_oem(current_tab.file_path):
                current_tab.load_data()
                messagebox.showinfo("Success", "Encoding converted successfully!")
    
    def convert_oem_to_ansi(self):
        """Convert from MS-DOS OEM to Windows ANSI encoding"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot modify read-only file.")
            return
        
        if messagebox.askyesno("Confirm Conversion", 
                              "Convert encoding from MS-DOS (OEM) to Windows (ANSI)?\n\n" +
                              "A backup will be created before conversion."):
            if convert_oem_to_ansi(current_tab.file_path):
                current_tab.load_data()
                messagebox.showinfo("Success", "Encoding converted successfully!")
    
    def convert_ansi_to_utf8(self):
        """Convert from Windows ANSI to UTF-8 encoding"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot modify read-only file.")
            return
        
        if messagebox.askyesno("Confirm Conversion", 
                              "Convert encoding from Windows (ANSI) to UTF-8?\n\n" +
                              "A backup will be created before conversion."):
            if convert_ansi_to_utf8(current_tab.file_path):
                current_tab.load_data()
                messagebox.showinfo("Success", "Encoding converted successfully!")
    
    def convert_utf8_to_ansi(self):
        """Convert from UTF-8 to Windows ANSI encoding"""
        current_tab = self.get_current_tab()
        if not current_tab:
            messagebox.showinfo("No File", "No file is currently open.")
            return
        
        if current_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot modify read-only file.")
            return
        
        if messagebox.askyesno("Confirm Conversion", 
                              "Convert encoding from UTF-8 to Windows (ANSI)?\n\n" +
                              "A backup will be created before conversion."):
            if convert_utf8_to_ansi(current_tab.file_path):
                current_tab.load_data()
                messagebox.showinfo("Success", "Encoding converted successfully!")
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
EDVAN DBF Commander v1.1

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

© 2026 EDVAN DBF Commander
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
