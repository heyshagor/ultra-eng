# BKOA Member Data Scraper

This script scrapes member information from https://bkoa-bd.com/member/ and exports it to CSV format.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the scraper:

```bash
python member_scraper.py
```

The script will:
- Fetch the main member listing page
- Discover all member IDs (approximately 693 members)
- Visit each member's individual page
- Extract: name, picture URL, address, phone, email, and other details
- Save all data to `bkoa_members.csv`

## Output

The CSV file contains the following columns:
- `id`: Member ID from URL parameter
- `name`: Member name
- `picture`: URL to member picture
- `address`: Member address
- `phone`: Phone number
- `email`: Email address
- `member_type`: Type of membership (if available)
- `join_date`: Date when member joined
- `company`: Company/organization name
- `additional_info`: Any other captured details

## Notes

- The script includes a 1-second delay between requests to be respectful to the server
- Logging information is displayed in the console
- If the website structure changes, you may need to update the CSS selectors in `extract_member_details()` method
- Make sure you have permission to scrape the website

## Customization

If the website uses different HTML structure, you can modify the selectors in the `extract_member_details()` method:

- Update `name_selectors` list with appropriate CSS selectors
- Modify table extraction logic if data is in tables
- Adjust regex patterns for email/phone extraction

## Troubleshooting

- If scraping fails, check your internet connection
- Verify the website URL is accessible
- Check if the website has anti-scraping measures (like Cloudflare)
- Increase timeout in `fetch_page()` method if needed
