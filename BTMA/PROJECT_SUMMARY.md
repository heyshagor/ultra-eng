# PROJECT SUMMARY: BTMA PDF Data Extractor

## What Was Built

A complete Python data extraction and management **data pack** for converting BTMA fabric manufacturer PDF documents into structured Excel and CSV formats.

## Core Files

### Main Application
- **`main.py`** - Primary entry point with CLI and all features
- **`run.sh`** - Linux launcher script (auto-activates venv)
- **`test_extractor.py`** - Comprehensive test suite

### Core Package (`pdf_data_extractor/`)

- **`__init__.py`** - Package initialization
- **`extractor.py`** - PDF text/table extraction engine (pdfplumber)
- **`parser.py`** - Structured data parsing for companies, products, contacts
- **`cli.py`** - Command-line interface
- **`config.py`** - Configuration management

### Installation & Requirements

- **`setup.py`** - pip installable package configuration
- **`requirements.txt`** - Core dependencies only
- **`requirements-all.txt`** - Core + OCR dependencies

### Documentation

- **`README.md`** - Complete documentation
- **`QUICKSTART.md`** - Quick reference guide
- **`API.md`** - API reference with examples
- **`PROJECT_SUMMARY.md`** - This file

## Key Features

1. **PDF Extraction**
   - Text extraction from any PDF
   - Table detection and extraction
   - Optional OCR for scanned documents

2. **Data Export**
   - Excel (.xlsx) with multiple sheets
   - CSV with UTF-8-BOM encoding
   - Raw extraction + structured parsing

3. **Structured Parsing**
   - Company names, addresses, contacts
   - Product categories and items
   - Automatic pattern detection

4. **Easy to Use**
   - Command-line interface
   - Python API
   - Test mode with sample data

## Quick Start

### Option 1: Direct Python
```bash
cd "/home/heyshagor/Documents/Ultra Engineering/BTMA"
source venv/bin/activate
python main.py --test
```

### Option 2: Shell Script
```bash
cd "/home/heyshagor/Documents/Ultra Engineering/BTMA"
./run.sh --test
```

### Option 3: As Package
```bash
pip install -e .
btma-main --test
```

## Sample Commands

```bash
# Create sample dataset
main.py --test

# Extract your PDF
main.py --input yourfile.pdf

# Extract with parsing
main.py --input yourfile.pdf --parse --all-sheets

# Extract with OCR
main.py --input scanned.pdf --ocr

# Get help
main.py --help
```

## Output Files

| Mode | Excel | CSV |
|------|-------|-----|
| Basic | `btma_fabric_data.xlsx` | `btma_fabric_data.csv` |
| Parsed | `btma_fabric_data_parsed.xlsx` | `companies.csv`, `products.csv`, `contacts.csv` |
| Test | `btma_sample_parsed.xlsx` | `demo_sample.xlsx`, `demo_sample.csv` |

## Requirements

### Required (already installed)
- Python 3.8+
- pdfplumber
- pandas
- openpyxl

### Optional (for OCR)
- pytesseract
- pdf2image
- Pillow
- System: Tesseract OCR

## Test Status

All 5 tests passing:
- ✓ Imports
- ✓ Sample Data Creation
- ✓ Parser Functionality
- ✓ Excel I/O
- ✓ CLI Execution

Run tests: `python test_extractor.py`

## Project Structure

```
BTMA/
├── pdf_data_extractor/        # Main package
│   ├── __init__.py
│   ├── extractor.py          # PDF extraction
│   ├── parser.py             # Data parsing
│   ├── cli.py                # CLI
│   ├── config.py             # Settings
│   └── requirements.txt
├── main.py                   # Entry point
├── test_extractor.py         # Tests
├── setup.py                  # Installer
├── run.sh                    # Launcher
├── requirements-all.txt      # All dependencies
├── README.md                 # Full docs
├── QUICKSTART.md             # Quick guide
└── API.md                    # API reference
```

## What You Get

1. **Complete Python package** - Importable module
2. **Command-line tool** - Easy to run and automate
3. **Sample data generation** - Test without the PDF
4. **OCR support** - Handle scanned documents
5. **Multi-format export** - Excel and CSV
6. **Documentation** - README, quickstart, API docs
7. **Test suite** - Verify installation
8. **Virtual environment** - Pre-configured with dependencies

## Notes

- The current PDF (`B-Fabric-Manufacturer-of-BTMA_General.pdf`) appears to be scanned/image-based
- For scanned PDFs, use the `--ocr` flag
- Test mode (`--test`) generates realistic sample BTMA data with 10 manufacturers
- The parser is designed for typical BTMA directory format but is flexible

## Next Steps

1. Activate virtual environment: `source venv/bin/activate`
2. Run test mode: `python main.py --test`
3. Try with your PDF: `python main.py --input yourfile.pdf`
4. If PDF is scanned, add `--ocr` flag
5. Review output files (Excel and CSV)

---

**Created:** April 6, 2026
**Version:** 1.0.0
**Status:** Ready for use
