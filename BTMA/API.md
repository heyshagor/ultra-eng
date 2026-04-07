# API Reference

## Classes

### PDFExtractor

Main class for extracting data from PDF files.

```python
from pdf_data_extractor import PDFExtractor
```

#### `__init__(pdf_path: str, use_ocr: bool = False)`

Initialize the extractor.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `use_ocr` (bool): Enable OCR for scanned PDFs (default: False)

**Example:**
```python
extractor = PDFExtractor('document.pdf', use_ocr=False)
```

#### `extract_all() -> Dict`

Extract all data from the PDF.

**Returns:**
- `Dict` containing:
  - `metadata`: dict with file info and page count
  - `pages`: list of page data (text, tables, dimensions)
  - `full_text`: combined text from all pages
  - `tables`: list of all extracted tables as DataFrames

**Example:**
```python
data = extractor.extract_all()
print(f"Total pages: {data['metadata']['total_pages']}")
```

#### `to_csv(output_path: str, table_num: Optional[int] = None) -> str`

Export extracted data to CSV.

**Parameters:**
- `output_path` (str): Destination CSV file path
- `table_num` (int, optional): Specific table number to export (None = all)

**Returns:**
- `str`: Path to saved CSV file

**Example:**
```python
extractor.to_csv('output.csv')
```

#### `to_excel(output_path: str, sheet_names: Optional[List[str]] = None) -> str`

Export extracted data to Excel with multiple sheets.

**Parameters:**
- `output_path` (str): Destination XLSX file path
- `sheet_names` (List[str], optional): Custom sheet names (auto-generated if None)

**Returns:**
- `str`: Path to saved Excel file

**Example:**
```python
extractor.to_excel('output.xlsx')
```

---

### BTMAParser

Parser for structured BTMA fabric manufacturer data.

```python
from pdf_data_extractor import BTMAParser
```

#### `load_from_extractor(extractor: PDFExtractor) -> BTMAParser`

Load data from a PDFExtractor instance.

**Parameters:**
- `extractor` (PDFExtractor): An extractor with data loaded

**Returns:**
- `BTMAParser`: Self for chaining

**Example:**
```python
parser = BTMAParser().load_from_extractor(extractor)
```

#### `parse_all()`

Run all parsing methods (companies, products, contacts).

**Example:**
```python
parser.parse_all()
```

#### `parse_companies() -> pd.DataFrame`

Parse company information.

**Returns:**
- `pd.DataFrame`: Companies with name, address, phone, email, website

#### `parse_products() -> pd.DataFrame`

Parse product information.

**Returns:**
- `pd.DataFrame`: Product categories and items

#### `parse_contacts() -> pd.DataFrame`

Parse contact information.

**Returns:**
- `pd.DataFrame`: Contacts with company and details

#### `get_all_parsed() -> Dict[str, pd.DataFrame]`

Get all parsed DataFrames.

**Returns:**
- `Dict`: Dictionary with keys 'companies', 'products', 'contacts'

**Example:**
```python
all_data = parser.get_all_parsed()
companies_df = all_data['companies']
```

#### `to_excel_multisheet(output_path: str) -> str`

Export all parsed data to multi-sheet Excel file.

**Parameters:**
- `output_path` (str): Destination XLSX file path

**Returns:**
- `str`: Path to saved Excel file

**Example:**
```python
parser.to_excel_multisheet('parsed_data.xlsx')
```

---

## Convenience Functions

Quick one-liner functions for common tasks.

### `extract_pdf_to_excel(pdf_path: str, excel_path: str, use_ocr: bool = False) -> str`

Extract PDF directly to Excel.

**Example:**
```python
from pdf_data_extractor import extract_pdf_to_excel
extract_pdf_to_excel('input.pdf', 'output.xlsx')
```

### `extract_pdf_to_csv(pdf_path: str, csv_path: str, use_ocr: bool = False) -> str`

Extract PDF directly to CSV.

**Example:**
```python
from pdf_data_extractor import extract_pdf_to_csv
extract_pdf_to_csv('input.pdf', 'output.csv')
```

---

## Complete Workflow Example

```python
from pdf_data_extractor import PDFExtractor, BTMAParser

# 1. Extract from PDF
extractor = PDFExtractor('btma_fabric.pdf', use_ocr=False)
extractor.extract_all()

# 2. Export raw data
extractor.to_excel('raw_data.xlsx')
extractor.to_csv('raw_data.csv')

# 3. Parse structured data
parser = BTMAParser()
parser.load_from_extractor(extractor)
parser.parse_all()

# 4. Get individual DataFrames
companies = parser.parsed_data['companies']
products = parser.parsed_data['products']
contacts = parser.parsed_data['contacts']

print(f"Found {len(companies)} companies")
print(f"Found {len(products)} product entries")

# 5. Export parsed data
parser.to_excel_multisheet('structured_data.xlsx')

# 6. Or export individual CSVs
for name, df in parser.get_all_parsed().items():
    df.to_csv(f'{name}.csv', index=False)
```

---

## Notes

- All file paths can be absolute or relative
- Excel files use `openpyxl` engine (xlsx format)
- CSV files use UTF-8-BOM encoding for Excel compatibility
- OCR requires `pytesseract` and `pdf2image` packages
- The parser uses regex patterns to identify company information; results may vary based on PDF formatting
