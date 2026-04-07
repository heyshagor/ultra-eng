# Quick Start Guide

## Installation & Setup

1. **Navigate to BTMA directory:**
   ```bash
   cd "/home/heyshagor/Documents/Ultra Engineering/BTMA"
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install packages:**
   ```bash
   pip install -r pdf_data_extractor/requirements.txt
   ```

## Quick Commands

### 1. Basic Extraction (from current directory)
```bash
python main.py
```
Extracts: `B-Fabric-Manufacturer-of-BTMA_General.pdf` → Excel + CSV

### 2. Extract Custom PDF
```bash
python main.py --input yourfile.pdf --excel output.xlsx --csv output.csv
```

### 3. Parse Structured Data
```bash
python main.py --parse --all-sheets
```
Creates multi-sheet Excel with:
- Companies (name, address, phone, email, website)
- Products (categories and items)
- Contacts (structured contact info)

### 4. OCR for Scanned PDFs
```bash
python main.py --input scanned.pdf --ocr
```
Note: Requires `pytesseract` and `pdf2image` packages.

### 5. Test Mode (Sample Data)
```bash
python main.py --test
```
Generates sample BTMA data for testing the pipeline.

## Output Files

| Command | Excel Output | CSV Output |
|---------|--------------|------------|
| `python main.py` | `btma_fabric_data.xlsx` | `btma_fabric_data.csv` |
| `--parse` | `btma_fabric_data_parsed.xlsx` | `{name}_companies.csv, {name}_products.csv, {name}_contacts.csv` |
| `--test` | `btma_sample_parsed.xlsx` | Individual CSV files |

## Python API Example

```python
from pdf_data_extractor import PDFExtractor, BTMAParser

# Extract
extractor = PDFExtractor('file.pdf')
extractor.extract_all()
extractor.to_excel('raw_data.xlsx')

# Parse
parser = BTMAParser()
parser.load_from_extractor(extractor)
parser.parse_all()
parser.to_excel_multisheet('structured_data.xlsx')
```

## Verification

Run test suite:
```bash
python test_extractor.py
```

This will:
- Test all imports
- Create sample data
- Validate Excel I/O
- Test parser functionality
- Verify CLI execution

## File Structure Created

```
BTMA/
├── pdf_data_extractor/
│   ├── __init__.py
│   ├── extractor.py      # Extraction engine
│   ├── parser.py         # Data parser
│   ├── cli.py           # CLI interface
│   └── config.py        # Configuration
├── main.py              # Main entry point
├── setup.py             # Installation script
├── test_extractor.py    # Test suite
├── requirements.txt     # Dependencies
└── README.md           # Full documentation
```

## Common Issues

**"Module not found" errors:**
```bash
source venv/bin/activate
pip install -r pdf_data_extractor/requirements.txt
```

**PDF not found:**
```bash
ls -la
# Ensure PDF is in current directory
```

**No text extracted (scanned PDF):**
```bash
python main.py --ocr
pip install pytesseract pdf2image
# Also install: tesseract-ocr (system package)
```

## Need Help?

See full documentation: `README.md`
