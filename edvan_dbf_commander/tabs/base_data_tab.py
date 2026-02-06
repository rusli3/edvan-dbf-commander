#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Data Tab

Abstract base class for data tabs with shared functionality including
pagination, SQL queries, sorting, and filtering.
"""

import os
import shutil
import sqlite3
from abc import ABC, abstractmethod
from datetime import datetime
from tkinter import messagebox
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseDataTab(ctk.CTkFrame, ABC):
    """Abstract base class for data tabs with shared functionality"""
    
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
        self.modified = False
        self.sort_column = None
        self.sort_ascending = True
        
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
        
        # Additional toolbar buttons (to be overridden by subclasses)
        self.setup_toolbar_buttons(toolbar)
        
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
    
    def setup_toolbar_buttons(self, toolbar):
        """Setup additional toolbar buttons - to be overridden by subclasses"""
        pass
    
    def create_data_tree(self):
        """Create the data tree view"""
        # Create frame for treeview
        tree_frame = tk.Frame(self.data_frame._parent_canvas)
        tree_frame.pack(fill="both", expand=True)
        
        # Create treeview with scrollbars
        self.data_tree = ttk.Treeview(tree_frame, show="headings")
        
        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.data_tree.yview)
        vsb.pack(side="right", fill="y")
        
        # Horizontal scrollbar
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.data_tree.xview)
        hsb.pack(side="bottom", fill="x")
        
        self.data_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.data_tree.pack(fill="both", expand=True)
        
        # Bind events
        self.data_tree.bind('<Button-1>', self.on_header_click)
        self.data_tree.bind('<Double-1>', self.on_double_click)
    
    @abstractmethod
    def load_data(self):
        """Load data from file - must be implemented by subclasses"""
        pass
    
    def update_data_display(self):
        """Update the data display for current page"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Determine which data to display
        display_df = self.filtered_df if self.filtered_df is not None else self.df
        
        if display_df is None or len(display_df) == 0:
            return
        
        # Configure columns
        self.data_tree['columns'] = list(display_df.columns)
        for col in display_df.columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
        
        # Calculate page range
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(display_df))
        
        # Insert data rows
        for idx in range(start_idx, end_idx):
            values = [str(display_df.iloc[idx][col]) for col in display_df.columns]
            self.data_tree.insert('', 'end', values=values)
        
        self.update_pagination_info()
    
    def update_pagination_info(self):
        """Update pagination information"""
        display_df = self.filtered_df if self.filtered_df is not None else self.df
        total = len(display_df) if display_df is not None else 0
        total_pages = max(1, (total + self.rows_per_page - 1) // self.rows_per_page)
        self.page_label.configure(text=f"Page {self.current_page + 1}/{total_pages}")
    
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
        display_df = self.filtered_df if self.filtered_df is not None else self.df
        total = len(display_df) if display_df is not None else 0
        total_pages = max(1, (total + self.rows_per_page - 1) // self.rows_per_page)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_data_display()
    
    def last_page(self):
        """Go to last page"""
        display_df = self.filtered_df if self.filtered_df is not None else self.df
        total = len(display_df) if display_df is not None else 0
        total_pages = max(1, (total + self.rows_per_page - 1) // self.rows_per_page)
        self.current_page = total_pages - 1
        self.update_data_display()
    
    def execute_sql(self):
        """Execute SQL query on data"""
        query = self.sql_entry.get().strip()
        if not query:
            messagebox.showinfo("SQL Query", "Please enter a SQL query")
            return
        
        if self.df is None:
            messagebox.showerror("Error", "No data loaded")
            return
        
        try:
            # Create in-memory SQLite database
            conn = sqlite3.connect(':memory:')
            self.df.to_sql('data', conn, index=False, if_exists='replace')
            
            # Execute query
            result = pd.read_sql_query(query, conn)
            conn.close()
            
            # Store filtered result
            self.filtered_df = result
            self.current_page = 0
            self.update_data_display()
            
            logger.info(f"SQL query executed: {query}")
            
        except Exception as e:
            messagebox.showerror("SQL Error", f"Query failed: {str(e)}")
            logger.error(f"SQL query failed: {str(e)}")
    
    def clear_filter(self):
        """Clear current filter and show all data"""
        self.filtered_df = None
        self.sql_entry.delete(0, 'end')
        self.current_page = 0
        self.update_data_display()
    
    def on_header_click(self, event):
        """Handle header click for sorting"""
        region = self.data_tree.identify("region", event.x, event.y)
        if region == "heading":
            column = self.data_tree.identify_column(event.x)
            col_index = int(column[1:]) - 1  # Column index (0-based)
            
            display_df = self.filtered_df if self.filtered_df is not None else self.df
            if display_df is not None and col_index < len(display_df.columns):
                col_name = display_df.columns[col_index]
                
                # Toggle sort order if same column
                if self.sort_column == col_name:
                    self.sort_ascending = not self.sort_ascending
                else:
                    self.sort_column = col_name
                    self.sort_ascending = True
                
                # Sort the data
                if self.filtered_df is not None:
                    self.filtered_df = self.filtered_df.sort_values(
                        by=col_name, ascending=self.sort_ascending
                    ).reset_index(drop=True)
                else:
                    self.df = self.df.sort_values(
                        by=col_name, ascending=self.sort_ascending
                    ).reset_index(drop=True)
                
                self.update_data_display()
    
    def on_double_click(self, event):
        """Handle double-click for editing - to be overridden by subclasses"""
        pass
    
    def backup_file(self):
        """Create backup of the current file"""
        try:
            backup_dir = os.path.dirname(self.file_path)
            file_name = os.path.basename(self.file_path)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{os.path.splitext(file_name)[0]}_backup_{timestamp}{os.path.splitext(file_name)[1]}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            shutil.copy2(self.file_path, backup_path)
            messagebox.showinfo("Backup", f"Backup created: {backup_name}")
            logger.info(f"Backup created: {backup_path}")
            
        except Exception as e:
            messagebox.showerror("Backup Error", f"Failed to create backup: {str(e)}")
            logger.error(f"Backup failed: {str(e)}")
    
    def cleanup(self):
        """Cleanup resources when tab is closed"""
        # Clear dataframes to free memory
        if self.df is not None:
            del self.df
            self.df = None
        if self.filtered_df is not None:
            del self.filtered_df
            self.filtered_df = None
        
        logger.info(f"Resources cleaned up for: {self.file_path}")
