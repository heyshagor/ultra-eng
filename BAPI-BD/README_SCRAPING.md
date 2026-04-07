# BAPI Bangladesh Members Directory Scraper

Successfully scraped **169 member companies** from http://www.bapi-bd.com/members-directory.html

## Files Created

1. **bapi_members_detailed.csv** - Main cleaned dataset with separated columns:
   - Sl. No.
   - Company Name & Address
   - Email
   - Representative
   - Telephone
   - Website

2. **bapi_members_cleaned.csv** - Original table format (cleaned)
3. **bapi_members_data.csv** - Raw extracted data
4. **page_rendered.html** - Full HTML snapshot of the page
5. **scrape_with_selenium.py** - Main scraping script using Selenium (handles JavaScript)
6. **clean_data.py** - Data cleaning and structuring script

## Setup

The scraper uses Python 3 with these packages:
- selenium
- webdriver-manager
- beautifulsoup4
- requests
- lxml

Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Scraper

```bash
source venv/bin/activate
python scrape_with_selenium.py
```

This will:
1. Open Chrome in headless mode
2. Load the members directory page (bypasses Incapsula protection)
3. Extract all table data
4. Save to `bapi_members_data.csv`
5. Generate `page_rendered.html` for inspection

## Data Cleaning

```bash
python clean_data.py
```

This produces the final `bapi_members_detailed.csv` with clean, separated columns.

## Notes

- The website uses Incapsula anti-bot protection, so requests won't work directly
- Selenium with a real browser is required to render JavaScript content
- Chrome/Chromium must be installed on the system
- The scraper waits 10 seconds for page content to load completely
- Output includes multiple email addresses separated by commas
- Phone numbers with multiple lines are preserved

## Output Sample

```
Sl. No.,Company Name & Address,Email,Representative,Telephone,Website
01,"The ACME Laboratories Ltd.1/4 Kallayanpur, Mirpur Road, Dhaka-1207","msinha.md@acmeglobal.com,taseem@acmeglobal.com",Mr. Fahim Sinha,"9021993
9004194-6
9005620",Visit Website
02,"Aristopharma Ltd.Aristo Tower, 239 Bir Uttam Mir Shawkat Sarak, Tejgoan-Gulshan Link Road, Dhaka-1208","aih@aristopharma.com,apl@aristopharma.com",Mr. Ahmed Imtiaz Hassan,"09606332211-12
02226603965-66",Visit Website
...
```

## Customization

If you need to extract different information or the website structure changes, you can modify:
- The table extraction logic in `scrape_with_selenium.py` (lines 48-60)
- The CSS selectors to target specific elements
- The wait time (currently 10 seconds) if the page loads slowly

The script already saves `page_rendered.html` which you can inspect in a browser to identify new selectors.
