# BJGEA Member List Scraper

This script scrapes member data from the BJGEA website (bjgea.net.bd) and exports it to a CSV file.

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Step 1: Inspect the page structure

The first time you run this, you need to understand how the data is structured on the website. Run:

```bash
python scrape_members.py --inspect
```

This will fetch page 1 and show you:
- How many tables are on the page
- Table headers and column structure
- Sample data from the first row
- Any email or phone patterns found

**Important:** Look at the column order and adjust the `extract_members_from_html()` function accordingly. The function uses column indices (0-based), so you need to map which column contains:
- Company name
- Person's name
- Member since date
- Organization
- Address
- Mobile number
- Telephone
- Email address

### Step 2: Run the full scraper

Once you've verified/reviewed the column mapping, run:

```bash
python scrape_members.py
```

This will:
- Scrape pages 1 through 20 (or until no more members are found)
- Save all data to `bjgea_members.csv`

## CSV Output Columns

The script produces a CSV file with these columns:

- `company_name` - Company name
- `name` - Contact person's name
- `member_since` - Date when member joined
- `organization` - Organization/business type
- `address` - Physical address
- `mobile` - Mobile phone number
- `tel` - Telephone number
- `email` - Email address

## Customizing the Script

If the page structure is different from what the script expects, edit the `extract_members_from_html()` function:

1. Change the table identification logic (the header keywords check)
2. Adjust the column index mapping to match your actual table structure
3. If the site uses div-based layouts instead of tables, modify the extraction logic

## Important Notes

- The script includes a 2-second delay between page requests to be respectful to the server
- If the website uses JavaScript to load data, this script won't work (let me know and we'll need a different approach)
- Make sure you have permission to scrape this data for your SEO/Marketing use case
- Future version checks may need to be adjusted if the website structure changes

## Troubleshooting

**No data collected?**
- Run `--inspect` first to see if the table structure is recognized
- Check if the table headers match the `member_keywords` pattern
- Print the full `col_texts` list to see what data you're getting

**Wrong data in columns?**
- Adjust the column indices in the mapping section (0-based indexing)
- The order of columns in your table may be different

**403/Forbidden error?**
- Some sites block automated requests
- You may need different headers or a delay between requests
- Check if the site requires login or has anti-scraping measures

## Files

- `scrape_members.py` - Main scraping script
- `requirements.txt` - Python dependencies
- `README.md` - This file

## License

This script is provided as-is for legitimate data collection purposes. Please ensure compliance with the website's terms of service.
