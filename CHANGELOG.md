# EDVAN DBF Commander - Changelog

## v1.0.1 (2024-12-25)

### 🐛 Bug Fixes
- **Fixed logger initialization bug**: Moved logger configuration before the pyreadstat import check to prevent `NameError: name 'logger' is not defined`

### 🆕 New Features  
- **Direct CSV Conversion**: Added ability to convert DBF and Stata DTA files directly to CSV
  - New menu items: "Convert DBF to CSV..." and "Convert Stata to CSV..."
  - Configurable CSV options: delimiter, encoding, headers, quoting
  - Data preview functionality before conversion
  - Support for comma, semicolon, tab, and pipe delimiters
  - Multiple encoding options: UTF-8, UTF-8-BOM, Windows-1252, ISO-8859-1

### 🛠️ Improvements
- **Enhanced Stata Support**: Better error handling when pyreadstat is not available
- **Installation Helper**: Added `install_stata_support.py` script for easy Stata support installation
- **Better User Feedback**: Enhanced batch file with Stata support status checking
- **Documentation Updates**: Updated README and QUICK_START with CSV conversion features

### 📋 Technical Changes
- Added `CSVConversionDialog` class for CSV conversion configuration
- Implemented `convert_dbf_to_csv()` and `convert_dta_to_csv()` functions
- Improved error handling and user messaging
- Enhanced logging configuration order

---

## v1.0.0 (2024-12-24)

### 🎉 Initial Release
- Modern DBF file management application with CustomTkinter GUI
- Tabbed interface for multiple files
- SQL query support
- Structure editor with field management
- Import/Export capabilities (CSV, XML, Excel, HTML)
- Find & Replace functionality
- Stata DTA file support (read-only)
- Backup and read-only modes
- Cross-platform compatibility

### 🔧 Core Features
- DBF file reading/writing with dbfpy3
- Data pagination for large files
- Advanced filtering and sorting
- Encoding conversion support
- Sample file generation
- Comprehensive documentation

### 📦 Dependencies
- Python 3.8+
- CustomTkinter
- pandas  
- dbfpy3
- openpyxl
- pyreadstat (optional, for Stata support)
