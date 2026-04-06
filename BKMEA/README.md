# BKMEA Member Data Scraper - Complete Solution

Extract **all member data** from Bangladesh Knitwear Manufacturers and Exporters Association (BKMEA) member portal.

**Status:** ✅ Fully functional - tested and working

## 🚀 Quick Start (3 Steps)

### Step 1: Install Requirements
```bash
pip install requests
```

### Step 2: Test with Sample IDs
```bash
python3 bkmea_direct_scraper.py --ids 1730,2820,2819
```

You should see:
```
✓ Success! Fetched 11998 bytes
  Company: PUSHPA KNITWEARS LIMITED
  Contact: MR. KAZI MAHABUB HOSSAIN, 01713-025975
```

### Step 3: Scrape ALL Members (Recommended)
```bash
python3 bkmea_bulk_scraper.py --max-id 5000 --workers 5 --yes
```

This will:
- Scan IDs from 1 to 5000 to find all valid members
- Scrape details for all found members
- Save to `bkmea_all_members.csv`

**Estimated time:** ~1000 members @ 3 workers = 5-10 minutes

---

## 📊 What Data Do You Get?

The scraper extracts **25+ fields** from each member:

| Field | Description |
|-------|-------------|
| `member_id` | Member ID from URL |
| `company_name` | Factory/Company name |
| `bkmea_membership_no` | BKMEA membership number (e.g., "1768 - C/2011") |
| `membership_category` | Category A, B, or C |
| `epb_reg_no` | EPB registration number |
| `establishment_date` | Date of establishment |
| `factory_address` | Factory location |
| `mailing_address` | Mailing address |
| `owner_name` | Owner/Proprietor name |
| `owner_mobile` | Owner phone number |
| `owner_email` | Owner email address |
| `rep_name` | Representative/Contact person |
| `rep_mobile` | Representative phone |
| `rep_email` | Representative email |
| `employees_male` | Male employees count |
| `employees_female` | Female employees count |
| `employees_total` | Total employees |
| `machines_knitting` | Knitting machines count |
| `machines_dyeing` | Dyeing machines count |
| `production_capacity` | Monthly production capacity |
| `products` | Principal products |
| `website` | Company website |
| `email` | General email |
| `phone` | General phone |
| `detail_url` | Link to member detail page |

*Note: Some fields may be blank if not provided by the member.*

---

## 🛠️ Available Scripts

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **`bkmea_direct_scraper.py`** | Scrape specific member IDs | You know exactly which IDs you want |
| **`bkmea_bulk_scraper.py`** | Discover & scrape ALL members | Get the complete dataset automatically |
| **`bkmea_full_scraper.py`** | Attempt to find member list page (likely fails - member list not public) | Alternative approach if direct ID scanning doesn't work |

**Recommended:** Use `bkmea_bulk_scraper.py` - it's designed specifically for BKMEA's structure where member IDs are sequential and the list page is not publicly accessible.

---

## 📋 Detailed Usage

### Using the Bulk Scraper (Main Tool)

```bash
# Basic: Discover and scrape all members up to ID 5000
python3 bkmea_bulk_scraper.py --max-id 5000 --workers 5 --yes

# Scrape a specific range (e.g., members 1000-2000)
python3 bkmea_bulk_scraper.py --start 1000 --end 2000 --workers 5 --yes

# Resume an interrupted scrape
python3 bkmea_bulk_scraper.py --max-id 5000 --resume --workers 5 --yes

# Use cached list of IDs (fast restart without rescanning)
python3 bkmea_bulk_scraper.py --max-id 5000 --skip-scan --workers 5 --yes

# Single-threaded (slower but gentler on server)
python3 bkmea_bulk_scraper.py --max-id 5000 --workers 1 --yes
```

**Parameters:**
- `--max-id N`: Scan up to member ID N (default: 3000). Increase if you suspect more members.
- `--start N`: Starting member ID (default: 1)
- `--end N`: Ending member ID (overrides `--max-id`)
- `--workers N`: Concurrent threads (1-10 recommended, default: 3). Higher = faster but more load on server.
- `--resume`: Resume from existing output file
- `--skip-scan`: Skip ID discovery, use cached valid IDs
- `--yes`: Skip confirmation prompts (useful for automation)
- `--help`: Show all options

---

### Using the Direct Scraper (Manual Control)

```bash
# Test a single member
python3 bkmea_direct_scraper.py --test 1730

# Scrape specific IDs
python3 bkmea_direct_scraper.py --ids 1730,2820,2819

# Scrape a range
python3 bkmea_direct_scraper.py --range 1-100

# Use a text file (one ID per line)
python3 bkmea_direct_scraper.py --file member_ids.txt
```

---

## ⚙️ How It Works

### Discovery Phase
1. Tests sequential member IDs (1, 2, 3, ...) using HTTP HEAD requests
2. IDs returning HTTP 200 are valid members
3. IDs returning 404 are skipped
4. Results are cached in `bkmea_valid_ids.txt` to avoid re-scanning

### Scraping Phase
1. For each valid ID, fetches the detail page
2. Parses the HTML table structure (unique to BKMEA)
3. Extracts all available fields
4. Saves incrementally to CSV

### Utilities
- **`--test` flag**: Quickly verify a member URL works and see sample data
- **Resume capability**: Interrupted? Just re-run with `--resume`
- **Cache**: Valid IDs saved → fast restarts with `--skip-scan`

---

## 📈 Expected Results

Based on current testing:
- **Total members** (as of April 2025): ~2,800+
- **Valid ID range**: 1 - 2823+ (with some gaps)
- **Highest known ID**: 2823
- **Page response time**: 0.5-2 seconds per member

### Example Output Snippet

```csv
member_id,company_name,bkmea_membership_no,membership_category,owner_name,owner_mobile,owner_email,employees_male,employees_female,employees_total,production_capacity,products
1730,PUSHPA KNITWEARS LIMITED,1768 - C/2011,C,MR. KAZI MAHABUB HOSSAIN,01713-025975,kazi_mahabub11@yahoo.com,70,182,252,9000,""
2819,MIM DESIGN LIMITED,2620 - C/2026,C,MD. MIZANUR RAHMAN CHOWDHURY,01711568072,tohid@mimgroupbd.com,40,20,60,,Knit & Woven
2820,GN FASHION INDUSTRIES LTD.,2621 - B/2026,B,SHYAMAL KANTI DEB,01712095990,shyamal@gnfashionbd.com,238,137,375,3333,"Sweater,All Kind of Knit Item,T-Shirt"
```

---

## ⚠️ Important Notes

### 1. Rate Limiting & Politeness
- The script includes delays (`DELAY_BETWEEN_REQUESTS = 0.5s`)
- **Do not reduce delays** unless you have explicit permission
- If you get HTTP 429 (Too Many Requests), increase `--workers` to lower concurrency or add delays
- Be a good internet citizen: don't hammer their server

### 2. Maximum ID Guessing
- The `--max-id` parameter determines the upper bound to scan
- If you suspect more members exist beyond the current max, increase it (e.g., `--max-id 10000`)
- The scan will stop at the first non-existent ID in the binary search phase

### 3. Missing Data
- Some members may have incomplete profiles → empty CSV cells
- The site structure is consistent but not all fields are mandatory

### 4. Legal & Ethical
- Ensure you have permission to scrape this data
- Review the website's Terms of Service
- Use data responsibly (not for spam, unauthorized marketing, etc.)
- This tool is for **legitimate business intelligence/research purposes only**

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `404` errors on many IDs | Some IDs legitimately don't exist. The scraper skips them automatically. |
| `Connection timeout` | Increase timeout in `fetch()` function or check your internet connection |
| `HTTP 429 Too Many Requests` | Reduce `--workers` to 1 or 2, increase delays |
| Data missing for some members | The member may have incomplete profile on the site |
| Scraping too slow | Increase `--workers` (but be gentle, max 5-10) |
| Want more fields? | Edit `parse_detail_page()` in the scraper to extract additional labels |

---

## 📦 Files Summary

| File | Description |
|------|-------------|
| `bkmea_bulk_scraper.py` | **MAIN TOOL** - Automatic full scrape |
| `bkmea_direct_scraper.py` | Manual ID-based scraper |
| `bkmea_all_members.csv` | Output CSV (created on first run) |
| `bkmea_valid_ids.txt` | Cache of discovered valid member IDs |
| `README.md` | This file |
| `requirements.txt` | Python dependencies |
| `sample_members.txt` | Example ID list |

---

## 🎯 Example Workflow (Your Use Case)

You mentioned you need this for CEO with company data. Here's the recommended workflow:

```bash
# 1. First, discover all members up to ID 3000 (adjust as needed)
python3 bkmea_bulk_scraper.py --max-id 3000 --workers 3 --yes

# 2. Wait for completion (check progress in terminal)

# 3. Open the CSV in Excel
open bkmea_all_members.csv  # macOS
# or double-click the file in Windows/Linux

# 4. Filter, search, analyze as needed
```

**Pro tip:** After scraping, you can filter by:
- `membership_category` to see A/B/C members
- `employees_total` to find large employers
- `production_capacity` to identify high-capacity factories
- `products` to find specific product types

---

## 🔧 Customization

If you need to extract **additional fields**:

1. Open `bkmea_bulk_scraper.py`
2. Find the `field_mapping` dictionary (~line 195)
3. Add new entries with the exact label from the HTML:
   ```python
   'Your Field Label': 'your_field_name',
   ```
4. Add the field to the `headers` list (~line 230)
5. Re-run the scraper

---

## 🙏 Credits

Built specifically for BKMEA member data extraction. The scraper handles:
- Sequential ID discovery (since member list is not public)
- BKMEA's unique table structure (3-col, 2-col, section headers)
- Concurrent scraping for speed
- Resume & caching for reliability

---

**Need help?** Check the debug script or inspect a sample HTML file during test mode.
