#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import/Export Utilities

Functions for importing CSV and XML data into DBF files,
and managing temporary files.
"""

import os
import glob
import tempfile
from datetime import datetime, timedelta
from tkinter import messagebox
import pandas as pd
from dbfpy3 import dbf
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)


def import_csv_to_dbf(csv_path: str, dbf_path: str, 
                      delimiter: str = ',', 
                      encoding: str = 'utf-8',
                      has_header: bool = True) -> bool:
    """
    Import CSV data into an existing or new DBF file.
    
    Args:
        csv_path: Path to the source CSV file
        dbf_path: Path to the target DBF file
        delimiter: CSV field delimiter
        encoding: CSV file encoding
        has_header: Whether CSV has header row
        
    Returns:
        True if import successful, False otherwise
    """
    try:
        # Read CSV file
        if has_header:
            df = pd.read_csv(csv_path, delimiter=delimiter, encoding=encoding)
        else:
            df = pd.read_csv(csv_path, delimiter=delimiter, encoding=encoding, header=None)
            # Generate column names
            df.columns = [f'FIELD{i+1}' for i in range(len(df.columns))]
        
        # Prepare data for DBF
        df = _prepare_dataframe_for_dbf(df)
        
        # Check if DBF file exists
        if os.path.exists(dbf_path):
            # Append to existing file
            _append_to_dbf(df, dbf_path)
        else:
            # Create new DBF file
            _create_dbf_from_dataframe(df, dbf_path)
        
        logger.info(f"Successfully imported {len(df)} records from {csv_path} to {dbf_path}")
        return True
        
    except Exception as e:
        logger.error(f"CSV import failed: {str(e)}")
        messagebox.showerror("Import Error", f"Failed to import CSV: {str(e)}")
        return False


def import_xml_to_dbf(xml_path: str, dbf_path: str, 
                      record_tag: str = 'record') -> bool:
    """
    Import XML data into an existing or new DBF file.
    
    Args:
        xml_path: Path to the source XML file
        dbf_path: Path to the target DBF file
        record_tag: XML tag name for each record
        
    Returns:
        True if import successful, False otherwise
    """
    try:
        # Parse XML file
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Extract records
        records = []
        columns = set()
        
        for record_elem in root.iter(record_tag):
            record = {}
            for child in record_elem:
                col_name = child.tag.upper()[:10]  # DBF column name limit
                col_name = col_name.replace('-', '_').replace(' ', '_')
                record[col_name] = child.text or ''
                columns.add(col_name)
            if record:
                records.append(record)
        
        if not records:
            # Try alternative: each child of root is a record
            for child in root:
                record = {}
                for field in child:
                    col_name = field.tag.upper()[:10]
                    col_name = col_name.replace('-', '_').replace(' ', '_')
                    record[col_name] = field.text or ''
                    columns.add(col_name)
                if record:
                    records.append(record)
        
        if not records:
            raise ValueError("No records found in XML file")
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Fill missing columns with empty strings
        for col in columns:
            if col not in df.columns:
                df[col] = ''
        
        # Prepare for DBF
        df = _prepare_dataframe_for_dbf(df)
        
        # Check if DBF file exists
        if os.path.exists(dbf_path):
            _append_to_dbf(df, dbf_path)
        else:
            _create_dbf_from_dataframe(df, dbf_path)
        
        logger.info(f"Successfully imported {len(df)} records from {xml_path} to {dbf_path}")
        return True
        
    except Exception as e:
        logger.error(f"XML import failed: {str(e)}")
        messagebox.showerror("Import Error", f"Failed to import XML: {str(e)}")
        return False


def _prepare_dataframe_for_dbf(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare DataFrame for DBF conversion."""
    result = df.copy()
    
    # Clean column names (max 10 chars, uppercase, no special chars)
    new_columns = []
    for col in result.columns:
        clean_name = str(col).upper().replace(' ', '_')[:10]
        # Remove invalid characters
        clean_name = ''.join(c for c in clean_name if c.isalnum() or c == '_')
        if not clean_name:
            clean_name = 'FIELD'
        new_columns.append(clean_name)
    result.columns = new_columns
    
    # Handle data types
    for col in result.columns:
        dtype = result[col].dtype
        
        # Convert to string and limit length
        if dtype == 'object':
            result[col] = result[col].fillna('').astype(str).str[:254]
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            result[col] = result[col].dt.strftime('%Y%m%d')
        elif dtype == 'bool':
            result[col] = result[col].map({True: 'T', False: 'F'})
        elif pd.api.types.is_numeric_dtype(dtype):
            result[col] = result[col].fillna(0)
    
    return result


def _create_dbf_from_dataframe(df: pd.DataFrame, dbf_path: str):
    """Create a new DBF file from DataFrame."""
    import dbf as dbf_lib
    
    # Determine field specifications
    field_specs = []
    for col in df.columns:
        dtype = df[col].dtype
        
        if pd.api.types.is_numeric_dtype(dtype):
            if pd.api.types.is_integer_dtype(dtype):
                field_specs.append(f"{col} N(12,0)")
            else:
                field_specs.append(f"{col} N(12,2)")
        else:
            max_len = min(df[col].astype(str).str.len().max() or 10, 254)
            max_len = max(max_len, 1)
            field_specs.append(f"{col} C({max_len})")
    
    # Create table
    table = dbf_lib.Table(dbf_path, '; '.join(field_specs))
    table.open(mode=dbf_lib.READ_WRITE)
    
    try:
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


def _append_to_dbf(df: pd.DataFrame, dbf_path: str):
    """Append DataFrame records to existing DBF file."""
    import dbf as dbf_lib
    
    table = dbf_lib.Table(dbf_path)
    table.open(mode=dbf_lib.READ_WRITE)
    
    try:
        for _, row in df.iterrows():
            record = table.new()
            for col, value in row.items():
                # Find matching field name (case-insensitive)
                matching_field = None
                for field in table.field_names:
                    if field.upper() == col.upper():
                        matching_field = field
                        break
                
                if matching_field:
                    if pd.isna(value) or value == '':
                        setattr(record, matching_field, '')
                    else:
                        setattr(record, matching_field, value)
            record.write_record()
    finally:
        table.close()


def cleanup_temp_files(max_age_hours: int = 24):
    """
    Clean up temporary DBF files created during Stata conversion.
    
    Args:
        max_age_hours: Maximum age of temp files to keep (in hours)
    """
    try:
        temp_dir = tempfile.gettempdir()
        pattern = os.path.join(temp_dir, "*.dbf")
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        for file_path in glob.glob(pattern):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff_time:
                    os.remove(file_path)
                    cleaned_count += 1
                    logger.info(f"Cleaned up temp file: {file_path}")
            except Exception as e:
                logger.warning(f"Could not clean up {file_path}: {e}")
        
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} temporary files")
        
        return cleaned_count
        
    except Exception as e:
        logger.error(f"Temp file cleanup failed: {str(e)}")
        return 0
