#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Find and Replace Dialog

Provides actual find and replace functionality for DBF data.
"""

import customtkinter as ctk
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)


class FindReplaceDialog(ctk.CTkToplevel):
    """Find and Replace dialog with actual implementation"""
    
    def __init__(self, parent, data_tab):
        super().__init__(parent)
        self.parent = parent
        self.data_tab = data_tab
        self.current_match_index = -1
        self.matches = []  # List of (row_idx, col_name, cell_value) tuples
        
        self.title("Find & Replace")
        self.geometry("450x350")
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
        self.find_entry.bind('<Return>', lambda e: self.find_next())
        
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
        self.partial_match.select()  # Default to partial match
        
        # Status label
        self.status_label = ctk.CTkLabel(main_frame, text="", text_color="gray")
        self.status_label.pack(pady=5)
        
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
    
    def _search_data(self, find_text: str) -> list:
        """Search the data for matching cells"""
        matches = []
        
        if not find_text:
            return matches
        
        df = self.data_tab.filtered_df if self.data_tab.filtered_df is not None else self.data_tab.df
        if df is None:
            return matches
        
        case_sensitive = self.case_sensitive.get()
        partial_match = self.partial_match.get()
        
        search_text = find_text if case_sensitive else find_text.lower()
        
        for row_idx, row in df.iterrows():
            for col_name in df.columns:
                cell_value = str(row[col_name]) if row[col_name] is not None else ""
                compare_value = cell_value if case_sensitive else cell_value.lower()
                
                if partial_match:
                    if search_text in compare_value:
                        matches.append((row_idx, col_name, cell_value))
                else:
                    if search_text == compare_value:
                        matches.append((row_idx, col_name, cell_value))
        
        return matches
    
    def find_next(self):
        """Find next occurrence"""
        find_text = self.find_entry.get()
        if not find_text:
            self.status_label.configure(text="Please enter search text")
            return
        
        try:
            # Search if matches list is empty or search text changed
            if not self.matches or not hasattr(self, '_last_search') or self._last_search != find_text:
                self.matches = self._search_data(find_text)
                self.current_match_index = -1
                self._last_search = find_text
            
            if not self.matches:
                self.status_label.configure(text="No matches found")
                return
            
            # Move to next match
            self.current_match_index = (self.current_match_index + 1) % len(self.matches)
            row_idx, col_name, cell_value = self.matches[self.current_match_index]
            
            # Update status
            self.status_label.configure(
                text=f"Match {self.current_match_index + 1} of {len(self.matches)}: "
                     f"Row {row_idx}, Column '{col_name}'"
            )
            
            # Highlight the match in the treeview
            self._highlight_match(row_idx, col_name)
            
            logger.info(f"Found match at row {row_idx}, column {col_name}")
            
        except Exception as e:
            logger.error(f"Find failed: {str(e)}")
            self.status_label.configure(text=f"Error: {str(e)}")
    
    def _highlight_match(self, row_idx: int, col_name: str):
        """Highlight the matching cell in the data view"""
        try:
            # Navigate to the page containing this row
            rows_per_page = self.data_tab.rows_per_page
            target_page = row_idx // rows_per_page
            
            if self.data_tab.current_page != target_page:
                self.data_tab.current_page = target_page
                self.data_tab.update_data_display()
            
            # Try to select the item in treeview
            tree = self.data_tab.data_tree
            if tree and hasattr(tree, 'selection_set'):
                # Clear current selection
                for item in tree.selection():
                    tree.selection_remove(item)
                
                # Find and select the matching row
                page_row = row_idx % rows_per_page
                items = tree.get_children()
                if page_row < len(items):
                    tree.selection_set(items[page_row])
                    tree.see(items[page_row])
                    
        except Exception as e:
            logger.warning(f"Could not highlight match: {str(e)}")
    
    def replace_current(self):
        """Replace current selection"""
        if not self.matches or self.current_match_index < 0:
            messagebox.showinfo("Replace", "Please find a match first")
            return
        
        if self.data_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot replace in read-only mode")
            return
        
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        try:
            row_idx, col_name, cell_value = self.matches[self.current_match_index]
            
            # Get the dataframe
            df = self.data_tab.df
            
            # Perform replacement
            case_sensitive = self.case_sensitive.get()
            if case_sensitive:
                new_value = cell_value.replace(find_text, replace_text)
            else:
                import re
                new_value = re.sub(re.escape(find_text), replace_text, cell_value, flags=re.IGNORECASE)
            
            # Update the dataframe
            df.at[row_idx, col_name] = new_value
            
            # Mark as modified
            self.data_tab.modified = True
            
            # Refresh display
            self.data_tab.update_data_display()
            
            # Remove the current match and find next
            self.matches.pop(self.current_match_index)
            if self.matches:
                self.current_match_index = self.current_match_index % len(self.matches)
                self.status_label.configure(text=f"Replaced. {len(self.matches)} matches remaining")
            else:
                self.current_match_index = -1
                self.status_label.configure(text="All matches replaced")
            
            logger.info(f"Replaced '{find_text}' with '{replace_text}' at row {row_idx}, column {col_name}")
            
        except Exception as e:
            logger.error(f"Replace failed: {str(e)}")
            messagebox.showerror("Error", f"Replace failed: {str(e)}")
    
    def replace_all(self):
        """Replace all occurrences"""
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        
        if not find_text:
            self.status_label.configure(text="Please enter search text")
            return
        
        if self.data_tab.read_only:
            messagebox.showinfo("Read-Only", "Cannot replace in read-only mode")
            return
        
        try:
            # Get fresh matches
            self.matches = self._search_data(find_text)
            
            if not self.matches:
                self.status_label.configure(text="No matches found")
                return
            
            count = len(self.matches)
            
            # Confirm replacement
            if not messagebox.askyesno("Confirm Replace All", 
                                       f"Replace {count} occurrences of '{find_text}' with '{replace_text}'?"):
                return
            
            # Get the dataframe
            df = self.data_tab.df
            case_sensitive = self.case_sensitive.get()
            
            # Perform all replacements
            import re
            for row_idx, col_name, cell_value in self.matches:
                if case_sensitive:
                    new_value = cell_value.replace(find_text, replace_text)
                else:
                    new_value = re.sub(re.escape(find_text), replace_text, cell_value, flags=re.IGNORECASE)
                df.at[row_idx, col_name] = new_value
            
            # Mark as modified
            self.data_tab.modified = True
            
            # Clear matches
            self.matches = []
            self.current_match_index = -1
            
            # Refresh display
            self.data_tab.update_data_display()
            
            self.status_label.configure(text=f"Replaced {count} occurrences")
            messagebox.showinfo("Replace All", f"Successfully replaced {count} occurrences")
            
            logger.info(f"Replaced all {count} occurrences of '{find_text}' with '{replace_text}'")
            
        except Exception as e:
            logger.error(f"Replace all failed: {str(e)}")
            messagebox.showerror("Error", f"Replace all failed: {str(e)}")
