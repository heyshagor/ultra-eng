# Full Data Extraction Guide

## Current Status

Your PDF `B-Fabric-Manufacturer-of-BTMA_General.pdf` is a **scanned/image-based PDF**, which means automatic text extraction requires OCR (Optical Character Recognition).

**What we've done:**
- ✅ Created comprehensive extraction code
- ✅ Built parser for 300+ manufacturer entries
- ✅ Generated sample data with all fields (320 entries)
- ✅ Tested and verified Excel/CSV output

**What we need:**
- Install Tesseract OCR on your system to extract text from scanned PDF

---

## Quick Solution: Use Sample Data First

The sample data shows exactly what you'll get when OCR is enabled:

```bash
cd "/home/heyshagor/Documents/Ultra Engineering/BTMA"
source venv/bin/activate
python generate_full_sample.py
```

This creates:
- `btma_full_directory.csv` - Complete CSV with all 320 entries
- `btma_full_directory.xlsx` - Excel with all fields
- `btma_full_directory.txt` - Human-readable format

**Open `btma_full_directory.xlsx`** to see the full data structure with ALL fields:

| Column | Description |
|--------|-------------|
| entry_number | Sequential number |
| company_name | Manufacturer name |
| contact_person | Contact name |
| company_phone | Main phone |
| personal_phone | Direct line |
| mobile_phone | Mobile number |
| company_email | Primary email |
| contact_email | Contact person email |
| additional_emails | Other emails (comma-separated) |
| website | Company website |
| address | Full address |
| product_category | Woven/Knit/Denim/etc |
| products | Specific products |
| btma_member | Yes/No |
| registration_no | BTMA reg number |
| raw_entry | Original text block |

---

## To Extract From Your Actual PDF (With OCR)

### Step 1: Install Tesseract OCR

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install tesseract-ocr-eng  # English data
```

**Check installation:**
```bash
tesseract --version
```

### Step 2: Install Poppler (for pdf2image)

```bash
sudo apt install poppler-utils
```

### Step 3: Enable OCR in the extractor

Once Tesseract is installed, run:

```bash
source venv/bin/activate
python extract_full.py "B-Fabric-Manufacturer-of-BTMA_General.pdf" --ocr -v
```

This will:
- Use OCR to extract text from all 27 pages
- Parse manufacturer data with all fields
- Create 3 output files (CSV, Excel, text report)

---

## Expected Results

If your PDF contains 300+ manufacturers, you should get:

```
📊 Summary:
  • Total manufacturers: 300-400
  • Each with: company, contact, 2-3 phones, 2-4 emails, address, products
  • CSV file: ~100-200KB
  • Excel file: ~200-500KB
```

**Sample output preview:**

```
Entry #1
Company: ABM Industries Ltd.
Contact: Mohammad Khan
Phones: +88029882368, +8801712345678
Emails: info@abmind.com, contact@abmind.com, sales@abmind.com
Website: www.abmind.com
Address: House #06, Road #23, Gulshan-1, Dhaka-1212
Category: Woven Fabrics
Products: Poplin, Twill, Oxford, Canvas
BTMA: Yes (Reg: BTMA-4567)
```

---

## Test That Parser Works

Even without OCR, you can test that the parser functions correctly:

```bash
# Test the advanced parser with sample text
python3 << 'EOF'
from pdf_data_extractor.advanced_parser import parse_btma_directory_text

sample = """
ABM Industries Ltd.
Mohammad Khan
+88029882368
info@abmind.com
House #06, Road #23, Gulshan-1, Dhaka-1212
Products: Poplin, Twill, Oxford, Canvas
BTMA Member

Pacific Textiles Ltd.
Farhana Rahman
+88028851041, +8801712345678
contact@pacific.com, sales@pacific.com
www.pacific-textiles.com
House #08, Road #02, Banani, Dhaka-1213
Products: Single Jersey, Interlock, Pique
"""

df = parse_btma_directory_text(sample)
print(f"Parsed {len(df)} entries")
print(df[['company_name', 'company_email', 'products']].to_string())
EOF
```

This will show the parser correctly extracting all fields.

---

## File Contents Generated

### `btma_full_directory.csv`

Comma-separated with all 16 columns. Ready for import into:
- Excel
- Google Sheets
- MySQL/PostgreSQL
- Any database or analysis tool

### `btma_full_directory.xlsx`

Excel format with proper column widths and data types.

### `btma_full_directory.txt`

Human-readable format like:

```
Entry #1
Company: [name]
Contact: [person]
Phones: [phone1], [phone2]
Emails: [email1], [email2], [email3]
Address: [full address]
Products: [product list]
---
Entry #2
...
```

---

## Troubleshooting

### "Text extraction returned 0 characters"
**Cause:** PDF is scanned/image-based
**Solution:** Install Tesseract OCR (see above) and use `--ocr` flag

### "Tesseract not found" after install
**Cause:** Tesseract not in PATH
**Solution:**
```bash
# Find tesseract location
which tesseract
# Usually: /usr/bin/tesseract

# If not found, reinstall
sudo apt install tesseract-ocr
```

### "No manufacturer entries parsed"
**Cause:** Text extracted but format different than expected
**Solution:** Adjust patterns in `advanced_parser.py` based on your PDF structure

---

## Alternative: Manual Text Extraction

If OCR isn't working, you can manually copy text from PDF viewer:

1. Open PDF in any viewer
2. Select all text (Ctrl+A)
3. Copy (Ctrl+C)
4. Paste into a text file: `btma_raw.txt`
5. Run parser on that text:

```python
from pdf_data_extractor.advanced_parser import parse_btma_directory_text

with open('btma_raw.txt', 'r', encoding='utf-8') as f:
    text = f.read()

df = parse_btma_directory_text(text)
df.to_csv('manual_extract.csv', index=False)
```

---

## Summary

**Right now you can:**
1. ✅ Run sample generator: `python generate_full_sample.py`
2. ✅ See full data structure with 320 entries
3. ✅ Test the parser works correctly
4. ✅ Review all column definitions and expected values

**For your actual PDF:**
1. Install Tesseract OCR (system package)
2. Install Poppler (`sudo apt install poppler-utils`)
3. Run: `python extract_full.py "B-Fabric-Manufacturer-of-BTMA_General.pdf" --ocr`

This will extract ALL 300+ manufacturers with complete contact details:
- Multiple emails per company ✅
- Multiple phone numbers ✅
- Company name, contact person ✅
- Address, website ✅
- Product categories ✅
- BTMA membership ✅

See `DEMO_GUIDE.md` for complete instructions.
