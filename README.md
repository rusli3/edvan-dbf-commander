# EDVAN DBF Commander 🗃️

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

A modern desktop application for managing and viewing DBF files with a sleek, professional interface.

![EDVAN DBF Commander Interface](https://via.placeholder.com/800x400/2B2D31/FFFFFF?text=EDVAN+DBF+Commander)

## ✨ Features

### 🎯 Core Features
- **Modern GUI**: Built with CustomTkinter for a sleek, dark-themed interface
- **Tabbed Interface**: Manage multiple DBF files simultaneously
- **DBF File Management**: Open, view, edit, and create DBF files
- **Structure Editor**: Modify DBF table structure and field definitions
- **SQL Query Support**: Execute SQL queries on DBF files with syntax highlighting
- **Multi-format Support**: Export to CSV, Excel, XML, HTML; Import from Stata (.dta)

### 📊 Data Management
- **Table View**: Modern data grid with sorting and filtering
- **Record Operations**: Add, edit, delete records with validation
- **Bulk Operations**: Import/export large datasets efficiently
- **Data Types**: Support for all DBF field types (Character, Numeric, Date, Logical, Memo)
- **Find & Replace**: Advanced search and replace functionality
- **Pagination**: Handle large files up to 500MB with efficient pagination

### 🔧 Advanced Features
- **Stata Support**: Optional support for Stata .dta files (requires pyreadstat)
- **Encoding Conversion**: Convert between Windows (ANSI), MS-DOS (OEM), and UTF-8
- **One-Click Backup**: Create instant backups of your DBF files
- **Read-Only Mode**: Open files safely without risk of accidental modifications
- **Logging System**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error handling with user-friendly messages

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
pyreadstat>=1.0.0  # For Stata .dta support
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
python install_stata_support.py
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
├── edvan_dbf_commander.py      # Main application
├── create_sample_dbf.py        # Sample file generator
├── install_stata_support.py    # Stata support installer
├── run_edvan_dbf_commander.bat # Windows batch launcher
├── requirements.txt            # Python dependencies
├── .gitignore                 # Git ignore rules
├── LICENSE                    # MIT license
├── README.md                  # This file
├── CHANGELOG.md               # Version history
├── QUICK_START.md             # Quick start guide
├── PROJECT_READY.md           # Project status and roadmap
├── GITHUB_UPLOAD_GUIDE.md     # GitHub upload instructions
└── sample_*.dbf               # Sample DBF files
```

## 🎮 Usage Guide

### Opening Files
1. **New DBF**: File → New DBF... (Ctrl+N)
2. **Open DBF**: File → Open... (Ctrl+O)
3. **Read-Only**: File → Open Read-Only...
4. **Stata Files**: File → Open Stata File (.dta)...

### Editing Data
1. Double-click any cell to edit
2. Use **"Add Record"** to insert new rows
3. Select rows and click **"Delete Selected"** to remove
4. Use SQL queries for advanced filtering

### Importing/Exporting
- **Import CSV**: Data → Import → From CSV...
- **Export CSV**: Data → Export → To CSV...
- **Export Excel**: Data → Export → To Excel...
- **Export XML**: Data → Export → To XML...
- **Export HTML**: Data → Export → To HTML...
- **Convert DBF to CSV**: File → Convert DBF to CSV...
- **Convert Stata to CSV**: File → Convert Stata to CSV...

### SQL Queries
1. Use the SQL Query box to filter your data
2. Example queries:
```sql
SELECT * FROM data WHERE salary > 50000
SELECT department, AVG(salary) FROM data GROUP BY department
SELECT COUNT(*) FROM data WHERE active = True
SELECT * FROM data ORDER BY name
```

### Structure Editor
1. Open via: Edit → Structure Editor... (Ctrl+S)
2. **Add Field**: Click "Add Field" button
3. **Edit Field**: Modify name, type, length, decimals
4. **Reorder Fields**: Use ↑ ↓ buttons
5. **Delete Field**: Use × button
6. **Save Changes**: Click "Save Structure"

### Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| New File | Ctrl+N |
| Open File | Ctrl+O |
| Close Tab | Ctrl+W |
| Backup File | Ctrl+B |
| Find & Replace | Ctrl+F |
| Structure Editor | Ctrl+S |
| Exit Application | Ctrl+Q |

## 📊 Sample Data

The application includes three sample DBF files:

| File | Records | Description |
|------|---------|-------------|
| `sample_employees.dbf` | 15 | Employee information with salaries |
| `sample_products.dbf` | 15 | Product catalog with inventory |
| `sample_sales.dbf` | 20 | Sales transaction records |

Create additional sample files by running:
```bash
python create_sample_dbf.py
```

## 🛠️ Development

### Setting Up Development Environment
```bash
# Clone the repository
git clone https://github.com/your-username/edvan-dbf-commander.git
cd edvan-dbf-commander

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python edvan_dbf_commander.py
```

### Code Structure
- **Main Application**: `edvan_dbf_commander.py`
- **GUI Framework**: CustomTkinter widgets
- **Data Handling**: DBF and Pandas integration
- **Error Handling**: Comprehensive try-catch blocks
- **Logging**: Python logging module

### Architecture
- **Main Application**: `EDVANDBFCommander` class
- **Data Tabs**: `DBFDataTab` class for DBF files, `DTADataTab` for Stata files
- **Dialogs**: Separate classes for Structure Editor, Find/Replace, CSV Conversion
- **Performance**: Pagination system for large files (100 rows per page)

## 🐛 Troubleshooting

### Common Issues

**Application won't start:**
```bash
# Check Python version
python --version

# Install missing dependencies
pip install -r requirements.txt

# Run with verbose logging
python edvan_dbf_commander.py --verbose
```

**Stata support not working:**
```bash
# Install pyreadstat
pip install pyreadstat

# Or use the installer
python install_stata_support.py
```

**File format errors:**
- Ensure DBF files are not corrupted
- Check file permissions
- Try opening with Read-Only mode first

**Large file performance:**
- Application automatically uses pagination for files >100MB
- Consider increasing available RAM
- Close unnecessary applications

**Encoding issues:**
- Use: Data → Convert Encoding
- Try ANSI ↔ OEM conversion
- Try ANSI ↔ UTF-8 conversion

### Getting Help
1. Check the [CHANGELOG.md](CHANGELOG.md) for recent updates
2. Review [QUICK_START.md](QUICK_START.md) for basic usage
3. Open an issue on GitHub with error details

## 📈 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and updates.

## 🤝 Contributing

Contributions are welcome! Here's how to contribute:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Include type hints where appropriate

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **CustomTkinter** - Modern GUI framework
- **DBF Library** - DBF file handling
- **Pandas** - Data manipulation
- **Python Community** - Excellent ecosystem

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Made with ❤️ by rusli3**
**© 2026 EDVAN DBF Commander**

*Professional DBF management made simple.*


