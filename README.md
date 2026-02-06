# EDVAN DBF Commander 🗃️

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()
[![Version](https://img.shields.io/badge/Version-1.1.0-green.svg)]()

A modern desktop application for managing and viewing DBF files with a sleek, professional interface.

![EDVAN DBF Commander Interface](https://via.placeholder.com/800x400/2B2D31/FFFFFF?text=EDVAN+DBF+Commander)

## ✨ Features

### 🎯 Core Features
- **Modern GUI**: Built with CustomTkinter for a sleek, dark-themed interface
- **Tabbed Interface**: Manage multiple DBF files simultaneously
- **DBF File Management**: Open, view, edit, and create DBF files
- **Structure Editor**: Modify DBF table structure and field definitions
- **SQL Query Support**: Execute SQL queries on DBF files with syntax highlighting
- **Multi-format Support**: Export to CSV, Excel, XML, HTML; Import from CSV, XML, Stata (.dta)

### 📊 Data Management
- **Table View**: Modern data grid with sorting and filtering
- **Record Operations**: Add, edit, delete records with validation
- **Bulk Operations**: Import/export large datasets efficiently
- **Data Types**: Support for all DBF field types (Character, Numeric, Date, Logical, Memo)
- **Find & Replace**: Advanced search and replace with case-sensitive and partial match options
- **Pagination**: Handle large files up to 500MB with efficient pagination

### 🔧 Advanced Features
- **Stata Support**: Optional support for Stata .dta files (requires pyreadstat)
- **Encoding Conversion**: Convert between Windows (ANSI), MS-DOS (OEM), and UTF-8
- **One-Click Backup**: Create instant backups of your DBF files
- **Read-Only Mode**: Open files safely without risk of accidental modifications
- **Memory Management**: Automatic cleanup when tabs are closed
- **Temp File Cleanup**: Automatic cleanup of temporary files on startup

## 📋 Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: 512 MB RAM minimum (4GB recommended for large files)
- **Storage**: 50 MB free space

### Required Python Packages:
```
customtkinter>=5.2.0
dbfpy3>=1.1.0
pandas>=2.0.0
numpy>=1.24.0
openpyxl>=3.1.0
```

### Optional Packages:
```
pyreadstat>=1.2.0  # For Stata .dta support
```

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/rusli3/edvan-dbf-commander.git
cd edvan-dbf-commander
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Install Stata Support
```bash
pip install pyreadstat
```

### 4. Create Sample Files
```bash
python create_sample_dbf.py
```

### 5. Run the Application
```bash
python edvan_dbf_commander.py
```

Or use the batch file (Windows):
```batch
run_edvan_dbf_commander.bat
```

## 📁 Project Structure

```
edvan-dbf-commander/
├── edvan_dbf_commander.py          # Application launcher
├── edvan_dbf_commander/            # Main package (v1.1.0)
│   ├── __init__.py                 # Package initialization
│   ├── main.py                     # Main application class
│   ├── dialogs/                    # Dialog components
│   │   ├── __init__.py
│   │   ├── structure_dialog.py     # DBF structure editor
│   │   ├── find_replace_dialog.py  # Find & Replace dialog
│   │   ├── csv_dialog.py           # CSV conversion dialog
│   │   └── stata_dialog.py         # Stata conversion dialog
│   ├── tabs/                       # Data tab components
│   │   ├── __init__.py
│   │   ├── base_data_tab.py        # Shared tab functionality
│   │   ├── dbf_data_tab.py         # DBF file tab
│   │   └── dta_data_tab.py         # Stata DTA file tab
│   └── utils/                      # Utility modules
│       ├── __init__.py
│       ├── encoding.py             # Encoding conversion
│       └── import_export.py        # Import/export utilities
├── create_sample_dbf.py            # Sample file generator
├── install_stata_support.py        # Stata support installer
├── run_edvan_dbf_commander.bat     # Windows batch launcher
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── LICENSE                         # MIT license
├── README.md                       # This file
├── CHANGELOG.md                    # Version history
└── sample_*.dbf                    # Sample DBF files
```

## 🎮 Usage Guide

### Opening Files
| Action | Menu | Shortcut |
|--------|------|----------|
| New DBF | File → New DBF... | Ctrl+N |
| Open DBF | File → Open... | Ctrl+O |
| Open Read-Only | File → Open Read-Only... | - |
| Open Stata | File → Open Stata File (.dta)... | - |

### Editing Data
1. Double-click any cell to edit
2. Use **"Add Record"** to insert new rows
3. Select rows and click **"Delete Selected"** to remove
4. Use SQL queries for advanced filtering

### Find & Replace
1. Open via: Edit → Find & Replace (Ctrl+F)
2. Enter search text and replacement
3. Options: Case Sensitive, Partial Match
4. Use "Find Next", "Replace", or "Replace All"

### Importing/Exporting
| Action | Menu Path |
|--------|-----------|
| Import CSV | Data → Import → From CSV... |
| Import XML | Data → Import → From XML... |
| Export CSV | Data → Export → To CSV... |
| Export Excel | Data → Export → To Excel... |
| Export XML | Data → Export → To XML... |
| Export HTML | Data → Export → To HTML... |

### SQL Queries
```sql
SELECT * FROM data WHERE salary > 50000
SELECT department, AVG(salary) FROM data GROUP BY department
SELECT COUNT(*) FROM data WHERE active = True
SELECT * FROM data ORDER BY name
```

### Encoding Conversion
| Conversion | Menu Path |
|------------|-----------|
| ANSI → OEM | Data → Convert Encoding → Windows (ANSI) → MS-DOS (OEM) |
| OEM → ANSI | Data → Convert Encoding → MS-DOS (OEM) → Windows (ANSI) |
| ANSI → UTF-8 | Data → Convert Encoding → Windows (ANSI) → UTF-8 |
| UTF-8 → ANSI | Data → Convert Encoding → UTF-8 → Windows (ANSI) |

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Close Tab | Ctrl+W |
| Backup File | Ctrl+B |
| Find & Replace | Ctrl+F |
| Exit Application | Ctrl+Q |

## 📊 Sample Data

The application includes sample DBF files:

| File | Records | Description |
|------|---------|-------------|
| `sample_employees.dbf` | 15 | Employee information with salaries |
| `sample_products.dbf` | 15 | Product catalog with inventory |
| `sample_sales.dbf` | 20 | Sales transaction records |

Create sample files:
```bash
python create_sample_dbf.py
```

## 🛠️ Development

### Setting Up Development Environment
```bash
# Clone the repository
git clone https://github.com/rusli3/edvan-dbf-commander.git
cd edvan-dbf-commander

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python edvan_dbf_commander.py
```

### Architecture (v1.1.0)

The application uses a modular architecture:

- **Main Application**: `EDVANDBFCommander` class in `main.py`
- **Base Tab**: `BaseDataTab` abstract class with shared functionality
  - Pagination, SQL queries, sorting, filtering
  - Memory cleanup, backup functionality
- **Data Tabs**: `DBFDataTab` and `DTADataTab` extend `BaseDataTab`
- **Dialogs**: Separate classes for Structure Editor, Find/Replace, CSV/Stata Conversion
- **Utils**: Encoding conversion, import/export utilities

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
```bash
python --version  # Check Python version (3.8+)
pip install -r requirements.txt  # Install dependencies
```

**Stata support not working:**
```bash
pip install pyreadstat
```

**Encoding issues:**
- Use: Data → Convert Encoding
- Try ANSI ↔ OEM or ANSI ↔ UTF-8 conversion

**Large file performance:**
- Application uses pagination (100 rows per page)
- Consider increasing available RAM

## 📈 Changelog

### v1.1.0 (2026-02-06)
- **Restructured** project to modular package architecture
- **Added** `BaseDataTab` for code deduplication
- **Implemented** Find & Replace with full functionality
- **Implemented** CSV/XML import utilities
- **Added** encoding conversion (ANSI/OEM/UTF-8)
- **Added** automatic memory cleanup on tab close
- **Added** temporary file cleanup on startup
- **Cleaned up** redundant dependencies

### v1.0.0
- Initial release with core DBF management features

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CustomTkinter** - Modern GUI framework
- **dbfpy3** - DBF file handling
- **Pandas** - Data manipulation
- **Python Community** - Excellent ecosystem

---

**Made with ❤️ by rusli3**
**© 2026 EDVAN DBF Commander v1.1.0**

*Professional DBF management made simple.*
