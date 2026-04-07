# BTMA Fabric Manufacturer Data Extractor

A comprehensive Python package for extracting, parsing, and managing fabric manufacturer information from BTMA PDF documents into structured Excel and CSV formats.

## Features

- **PDF Extraction**: Extract text and tables from PDF documents
- **OCR Support**: Optional OCR for scanned/image-based PDFs (requires Tesseract)
- **Multi-format Export**: Excel (.xlsx) and CSV formats
- **Full Directory Parsing**: Extract ALL 300+ manufacturer entries with complete details
- **Multiple Emails/Phones**: Capture all contact information per company
- **Structured Parsing**: Automatic parsing of company data, products, and contacts
- **Multi-sheet Output**: Create organized Excel workbooks with separate sheets
- **Command Line Interface**: Easy-to-use CLI for quick processing
- **Test Mode**: Generate sample data (320 entries) for testing
- **Comprehensive Output**: 16 columns including all fields requested

## Installation

### 1. Create Virtual Environment (Recommended)

```bash
cd /home/heyshagor/Documents/Ultra\ Engineering/BTMA
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r pdf_data_extractor/requirements.txt
```

**Optional OCR Support** (for scanned PDFs):
```bash
pip install -r pdf_data_extractor/requirements.txt[ocr]
# Also install system dependencies:
# - Tesseract OCR: https://github.com/tesseract-ocr/tesseract
# - Poppler: For pdf2image (avoids ghostscript dependency)
```

## Usage

### Command Line Interface

Quick extraction from command line:

```bash
# Extract to Excel (default)
python pdf_data_extractor/main.py --input B-Fabric-Manufacturer-of-BTMA_General.pdf

# Extract to specific output
python pdf_data_extractor/main.py --input yourfile.pdf --excel output.xlsx --csv output.csv

# Enable OCR for scanned PDFs
python pdf_data_extractor/main.py --input scanned.pdf --ocr

# Parse structured data with all features
python pdf_data_extractor/main.py --parse --all-sheets --verbose

# Create sample dataset (for testing)
python pdf_data_extractor/main.py --test

### Full Directory Extraction (300+ entries)

For scanned BTMA directory PDFs, use the enhanced extractor:

```bash
# Generate sample full dataset (320 entries)
python generate_full_sample.py

# Extract from actual PDF with OCR
python extract_full.py "B-Fabric-Manufacturer-of-BTMA_General.pdf" --ocr

# With verbose output
python extract_full.py input.pdf --ocr --verbose
```

This extracts ALL manufacturer details:
- Company name, contact person
- Multiple phone numbers (company, personal, mobile)
- Multiple email addresses (primary, contact, additional)
- Website, full address
- Product category and specific products
- BTMA membership and registration number

Output files:
- `*_directory.csv` - Complete CSV with 16 columns
- `*_directory.xlsx` - Excel format
- `*_directory.txt` - Human-readable report

### Python API

Use the package directly in your Python code:

```python
from pdf_data_extractor import PDFExtractor, BTMAParser

# 1. Extract data from PDF
extractor = PDFExtractor('your_file.pdf', use_ocr=False)
data = extractor.extract_all()

# 2. Export to Excel
extractor.to_excel('output.xlsx')

# 3. Export to CSV
extractor.to_csv('output.csv')

# 4. Parse structured data
parser = BTMAParser()
parser.load_from_extractor(extractor)
parser.parse_all()

# Get individual DataFrames
companies_df = parser.parsed_data['companies']
products_df = parser.parsed_data['products']
contacts_df = parser.parsed_data['contacts']

# 5. Export parsed data to multi-sheet Excel
parser.to_excel_multisheet('parsed_output.xlsx')
```

### As Installed Package

```bash
# Run from anywhere after installation
pip install -e .
btma-main --input yourfile.pdf --excel output.xlsx
```

## Output Structure

### Raw Extraction (`extractor.to_excel()`)
- **Summary**: Metadata and extraction statistics
- **Page X_Table Y**: Raw table data (one sheet per table found)
- **Text**: All extracted text lines (if no tables)

### Parsed Data (`parser.to_excel_multisheet()`)
- **Companies**: Company name, address, phone, email, website
- **Products**: Product categories and items
- **Contacts**: Structured contact information

### CSV Outputs
CSV files are flat versions with all data in single files, suitable for database import.

## File Structure

```
BTMA/
├── pdf_data_extractor/
│   ├── __init__.py
│   ├── extractor.py      # Core extraction engine
│   ├── parser.py         # Data parsing logic
│   ├── cli.py           # Command-line interface
│   ├── config.py        # Configuration
│   └── requirements.txt
├── main.py               # Main entry point with demo data
├── setup.py              # Package setup
└── README.md             # This file
```

## Data Format

### Full Directory Extraction (16 columns)

When using `extract_full.py` or `generate_full_sample.py`, you get ALL fields:

| Column | Description | Example |
|--------|-------------|---------|
| `entry_number` | Sequential row number | 1 |
| `company_name` | Manufacturer name | "ABM Industries Ltd." |
| `contact_person` | Contact name | "Mohammad Khan" |
| `company_phone` | Main office phone | "+88029882368" |
| `personal_phone` | Direct line | "+8801712345678" |
| `mobile_phone` | Mobile number | "+8801868654321" |
| `company_email` | Primary email | "info@company.com" |
| `contact_email` | Contact person email | "name@company.com" |
| `additional_emails` | Other emails (semicolon-separated) | "sales@...; hr@..." |
| `website` | Company website | "www.company.com" |
| `address` | Full address | "House #06, Road #23, Dhaka" |
| `product_category` | Fabric type | "Woven Fabrics" |
| `products` | Specific products list | "Poplin, Twill, Canvas" |
| `btma_member` | BTMA membership status | "Yes" / "No" |
| `registration_no` | BTMA registration number | "BTMA-4567" |
| `raw_entry` | Original extracted text block | (internal use) |

### Product Categories

- **Woven Fabrics**: Poplin, Twill, Oxford, Canvas, Chambray, Satin, Plain Weave, Jacquard
- **Knitted Fabrics**: Single/Double Jersey, Interlock, Rib, Pique, Fleece, Terry, Mesh
- **Denim**: Indigo, Stretch, Ring, Open End, Organic, Slub
- **Home Textile**: Bed Sheets, Comforters, Pillows, Towels, Curtains
- **Shirting**: Plain, Striped, Checked, Printed, Dyed
- **Suiting**: Wool, Polyester, Blended, Jacket, Trouser

### Basic Parser Output (Simpler)

Using `main.py` only gives structured sheets:
- **Companies**: name, address, phone, email, website
- **Products**: manufacturer, category, products
- **Contacts**: contact details

For full details, use `extract_full.py`.

## Troubleshooting

### No text extracted from PDF
- The PDF might be scanned/image-based. Use `--ocr` flag
- Install OCR dependencies: `pip install -r requirements[ocr]`
- Install Tesseract OCR on your system

### OCR extraction fails
- Ensure Tesseract is installed and in PATH
- Set `TESSERACT_PATH` in config if tesseract is in non-standard location
- Install Poppler for pdf2image

### Permission errors
- Ensure you have read access to the PDF file
- Check virtual environment activation

### Encoding issues in CSV
- CSVs are saved with UTF-8-BOM (utf-8-sig) for Excel compatibility
- For other systems, encoding can be changed in `extractor.py`

## Requirements

### Core
- Python 3.8+
- pdfplumber
- pandas
- openpyxl

### Optional (OCR)
- pytesseract
- pdf2image
- Pillow
- System: Tesseract OCR, Poppler

## License

MIT License

## Support

For issues and feature requests, please contact the BTMA Data Team.

## Changelog

### v1.0.0 (Current)
- Initial release
- PDF text and table extraction
- OCR support for scanned documents
- Excel and CSV export
- Structured parsing for BTMA data
- Command-line interface
- Test mode with sample data
