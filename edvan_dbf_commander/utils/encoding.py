#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Encoding Conversion Utilities

Functions for converting between different text encodings in DBF files.
Supports Windows (ANSI/CP1252), MS-DOS (OEM/CP437), and UTF-8.
"""

import os
import shutil
from datetime import datetime
from tkinter import messagebox
import logging

logger = logging.getLogger(__name__)

# Encoding mappings
ENCODINGS = {
    'ansi': 'cp1252',    # Windows ANSI
    'oem': 'cp437',      # MS-DOS OEM (IBM PC)
    'utf8': 'utf-8',     # UTF-8
    'latin1': 'iso-8859-1'  # ISO Latin-1
}


def convert_ansi_to_oem(file_path: str, create_backup: bool = True) -> bool:
    """
    Convert text encoding from Windows ANSI (CP1252) to MS-DOS OEM (CP437).
    
    Args:
        file_path: Path to the file to convert
        create_backup: Whether to create a backup before conversion
        
    Returns:
        True if conversion successful, False otherwise
    """
    return _convert_encoding(file_path, 'cp1252', 'cp437', create_backup)


def convert_oem_to_ansi(file_path: str, create_backup: bool = True) -> bool:
    """
    Convert text encoding from MS-DOS OEM (CP437) to Windows ANSI (CP1252).
    
    Args:
        file_path: Path to the file to convert
        create_backup: Whether to create a backup before conversion
        
    Returns:
        True if conversion successful, False otherwise
    """
    return _convert_encoding(file_path, 'cp437', 'cp1252', create_backup)


def convert_ansi_to_utf8(file_path: str, create_backup: bool = True) -> bool:
    """
    Convert text encoding from Windows ANSI (CP1252) to UTF-8.
    
    Args:
        file_path: Path to the file to convert
        create_backup: Whether to create a backup before conversion
        
    Returns:
        True if conversion successful, False otherwise
    """
    return _convert_encoding(file_path, 'cp1252', 'utf-8', create_backup)


def convert_utf8_to_ansi(file_path: str, create_backup: bool = True) -> bool:
    """
    Convert text encoding from UTF-8 to Windows ANSI (CP1252).
    
    Args:
        file_path: Path to the file to convert
        create_backup: Whether to create a backup before conversion
        
    Returns:
        True if conversion successful, False otherwise
    """
    return _convert_encoding(file_path, 'utf-8', 'cp1252', create_backup)


def _convert_encoding(file_path: str, from_encoding: str, to_encoding: str, 
                      create_backup: bool = True) -> bool:
    """
    Internal function to convert file encoding.
    
    For DBF files, this converts the character data within the records.
    """
    try:
        # Validate file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Create backup if requested
        if create_backup:
            backup_path = _create_backup(file_path)
            logger.info(f"Created backup: {backup_path}")
        
        # Read the file content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Check if this is a DBF file
        is_dbf = file_path.lower().endswith('.dbf')
        
        if is_dbf:
            # For DBF files, we need to handle the structure carefully
            # DBF header is fixed, only data portion needs encoding conversion
            converted_content = _convert_dbf_encoding(content, from_encoding, to_encoding)
        else:
            # For other files, convert the entire content
            try:
                decoded = content.decode(from_encoding)
                converted_content = decoded.encode(to_encoding)
            except UnicodeDecodeError as e:
                logger.warning(f"Decode error, trying with errors='replace': {e}")
                decoded = content.decode(from_encoding, errors='replace')
                converted_content = decoded.encode(to_encoding, errors='replace')
        
        # Write back
        with open(file_path, 'wb') as f:
            f.write(converted_content)
        
        logger.info(f"Successfully converted {file_path} from {from_encoding} to {to_encoding}")
        return True
        
    except Exception as e:
        logger.error(f"Encoding conversion failed: {str(e)}")
        messagebox.showerror("Conversion Error", f"Failed to convert encoding: {str(e)}")
        return False


def _convert_dbf_encoding(content: bytes, from_encoding: str, to_encoding: str) -> bytes:
    """
    Convert encoding for DBF file content.
    
    DBF files have a specific structure:
    - Header (32 bytes minimum + field descriptors)
    - Records (each starts with a deletion flag byte)
    """
    # DBF header length is at byte 8 (2 bytes, little-endian)
    if len(content) < 32:
        raise ValueError("Invalid DBF file: too short")
    
    header_length = int.from_bytes(content[8:10], 'little')
    
    # Get header and data portions
    header = content[:header_length]
    data = content[header_length:]
    
    # Convert data portion
    try:
        decoded_data = data.decode(from_encoding)
        converted_data = decoded_data.encode(to_encoding)
    except UnicodeDecodeError:
        # Try with error handling
        decoded_data = data.decode(from_encoding, errors='replace')
        converted_data = decoded_data.encode(to_encoding, errors='replace')
    
    # Combine header and converted data
    return header + converted_data


def _create_backup(file_path: str) -> str:
    """Create a backup of the file."""
    backup_dir = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{os.path.splitext(file_name)[0]}_backup_{timestamp}{os.path.splitext(file_name)[1]}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    shutil.copy2(file_path, backup_path)
    return backup_path


def detect_encoding(file_path: str) -> str:
    """
    Attempt to detect the encoding of a file.
    
    Returns the most likely encoding name.
    """
    try:
        # Try common encodings
        encodings_to_try = ['utf-8', 'cp1252', 'cp437', 'iso-8859-1']
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        for encoding in encodings_to_try:
            try:
                content.decode(encoding)
                logger.info(f"Detected encoding: {encoding}")
                return encoding
            except UnicodeDecodeError:
                continue
        
        # Default to Latin-1 (can decode any byte sequence)
        return 'iso-8859-1'
        
    except Exception as e:
        logger.error(f"Encoding detection failed: {str(e)}")
        return 'iso-8859-1'
