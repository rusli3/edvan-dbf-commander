# EDVAN DBF Commander - Quick Start Guide

## 🚀 Quick Installation & Launch

### For Windows Users (Easiest Method)
1. **Double-click** `run_edvan_dbf_commander.bat`
   - This will automatically check Python, install dependencies, create sample files, and launch the app!

### Manual Installation
1. **Install Python 3.8+** from [python.org](https://python.org)
2. **Open Command Prompt/Terminal** in the application folder
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create sample files** (optional but recommended):
   ```bash
   python create_sample_dbf.py
   ```
5. **Run the application:**
   ```bash
   python edvan_dbf_commander.py
   ```

## 🎯 First Steps

### 1. Open Your First File
#### DBF Files
- **File → Open...** (Ctrl+O) to open an existing DBF file
- **File → Open Read-Only...** to safely view files without editing risk
- Try the included sample files: `sample_employees.dbf`, `sample_products.dbf`, `sample_sales.dbf`

#### Stata DTA Files 🆕🅴🆆
- **File → Open Stata File (.dta)...** to open Stata files directly
- **File → Convert Stata to DBF...** to convert .dta files to .dbf format
- DTA files open in **read-only mode** with a "Convert to DBF" button

### 2. Explore the Interface
- **Tabbed Interface**: Each DBF file opens in its own tab
- **Pagination Controls**: Navigate large files with ◀◀ ◀ ▶ ▶▶ buttons
- **SQL Query Box**: Filter data with SQL commands like `SELECT * FROM data WHERE salary > 70000`

### 3. Key Features to Try

#### 🔍 **SQL Queries** (Most Popular Feature)
```sql
SELECT * FROM data WHERE department = 'Engineering'
SELECT name, salary FROM data WHERE salary > 75000
SELECT * FROM data ORDER BY hire_date
```

#### 📊 **Sort Data**
- Click any column header to sort
- Click again to reverse order

#### 🛠️ **Edit Structure**
- **Edit → Structure Editor...** (Ctrl+S)
- Add, edit, delete, or reorder fields

#### 💾 **Export Data**
- **Data → Export → To Excel...** (most popular)
- Also available: CSV, XML, HTML

#### 🔍 **Find & Replace**
- **Edit → Find & Replace...** (Ctrl+F)
- Search and replace text across your data

### 4. Essential Keyboard Shortcuts
| Action | Shortcut |
|--------|----------|
| Open File | **Ctrl+O** |
| Find & Replace | **Ctrl+F** |
| Structure Editor | **Ctrl+S** |
| Backup File | **Ctrl+B** |
| Close Tab | **Ctrl+W** |

## 🎯 Common Use Cases

### Scenario 1: View Large DBF Files
1. Open file in **Read-Only mode** (File → Open Read-Only...)
2. Use **pagination** to navigate (100 records per page)
3. Use **SQL queries** to filter specific data

### Scenario 2: Convert Files to Other Formats

#### Convert to Excel
1. Open your DBF file
2. Optional: Filter with SQL query
3. **Data → Export → To Excel...**
4. Choose save location

#### 🆕 Direct CSV Conversion
1. **File → Convert DBF to CSV...** (for DBF files)
2. **File → Convert Stata to CSV...** (for DTA files)  
3. Configure options:
   - Delimiter: comma, semicolon, tab, or pipe
   - Encoding: UTF-8, UTF-8-BOM, Windows-1252, or ISO-8859-1
   - Headers: include/exclude column names
   - Quoting: quote text fields or minimal quoting
4. Preview data and convert

### Scenario 3: Edit Field Structure
1. **Edit → Structure Editor...** (Ctrl+S)
2. Click **Add Field** or edit existing fields
3. Use ↑ ↓ to reorder fields
4. **Save Structure**

### Scenario 4: Search and Replace Data
1. **Edit → Find & Replace...** (Ctrl+F)
2. Enter search and replacement text
3. Choose options (case sensitive, partial match)
4. Click **Replace All**

## 🔧 Troubleshooting

### "Missing Library" Error
**Solution:** Run `pip install -r requirements.txt`

### File Won't Open
**Try:** File → Open Read-Only... (safer mode)

### Performance Issues with Large Files
- Application uses **automatic pagination** (100 records/page)
- Use **SQL queries** to filter data
- Consider **Read-Only mode** for viewing only

### Special Characters Look Wrong
**Solution:** Data → Convert Encoding → try ANSI ↔ OEM or ANSI ↔ UTF-8

## 📁 File Structure Overview

```
📁 EDVAN-DBF-Commander/
├── 🐍 edvan_dbf_commander.py      # Main application
├── 📄 requirements.txt            # Dependencies
├── 🎯 run_edvan_dbf_commander.bat # Windows launcher
├── 🔧 create_sample_dbf.py       # Creates test files
├── 📖 README.md                   # Full documentation
├── ⚡ QUICK_START.md              # This file
└── 📊 sample_*.dbf               # Test DBF files
```

## 🏁 Ready to Start!

You're now ready to use EDVAN DBF Commander! Start by:
1. **Double-clicking** `run_edvan_dbf_commander.bat` (Windows)
2. **Opening** one of the sample files to explore features
3. **Trying** SQL queries in the query box

For detailed features and advanced usage, see `README.md`.

**Enjoy managing your DBF files! 🎉**
