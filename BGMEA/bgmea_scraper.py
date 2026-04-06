#!/usr/bin/env python3
"""
BGMEA Member Data Scraper
Scrapes all member data from bgmea.com.bd and saves to CSV/Excel
"""

import requests
import csv
import time
from html.parser import HTMLParser
import re

class MemberTableParser(HTMLParser):
    """Parser to extract member rows from HTML table"""
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tbody = False
        self.in_tr = False
        self.in_td = False
        self.current_row = []
        self.cell_parts = []
        self.cell_href = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'table' and 'table-responsive' in attrs_dict.get('class', ''):
            self.in_table = True
        elif tag == 'tbody' and self.in_table:
            self.in_tbody = True
        elif tag == 'tr' and self.in_tbody:
            self.in_tr = True
            self.current_row = []
            self.cell_href = None
        elif tag == 'td' and self.in_tr:
            self.in_td = True
            self.cell_parts = []
            self.cell_href = None
        elif tag == 'a' and self.in_td and 'href' in attrs_dict:
            self.cell_href = attrs_dict['href']

    def handle_endtag(self, tag):
        if tag == 'table':
            self.in_table = False
        elif tag == 'tbody':
            self.in_tbody = False
        elif tag == 'tr':
            self.in_tr = False
            if self.current_row and len(self.current_row) >= 4:
                self.rows.append(self.current_row.copy())
        elif tag == 'td':
            self.in_td = False
            if self.cell_href:
                self.current_row.append(self.cell_href)
            else:
                text = ''.join(self.cell_parts).strip()
                self.current_row.append(text)

    def handle_data(self, data):
        if self.in_td:
            self.cell_parts.append(data)

def fetch_page(page_num):
    """Fetch a specific page of member list"""
    url = f"https://www.bgmea.com.bd/page/member-list?page={page_num}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def parse_members(html_content):
    """Parse HTML and extract member data"""
    parser = MemberTableParser()
    parser.feed(html_content)
    return parser.rows

def main():
    output_file = 'bgmea_members.csv'

    print("Starting BGMEA member data scraping...")

    # First, find total number of pages by checking page 1 for pagination
    first_page = fetch_page(1)
    # Look for the highest page number in pagination
    page_numbers = re.findall(r'page=(\d+)', first_page)
    if page_numbers:
        max_page = max([int(p) for p in page_numbers if int(p) < 1000])
        print(f"Found approximately {max_page} pages")
    else:
        max_page = 213  # default based on observation
        print(f"Using default max pages: {max_page}")

    # Open CSV file
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Company Name', 'BGMEA Reg No', 'Contact Person', 'Email Address', 'Details URL'])

        total_members = 0

        # Iterate through all pages
        for page in range(1, max_page + 1):
            try:
                print(f"Fetching page {page}/{max_page}...", end=' ')
                html = fetch_page(page)
                members = parse_members(html)

                if not members:
                    print(f"No members found. Stopping at page {page}.")
                    break

                # Write members to CSV
                for member in members:
                    writer.writerow(member)

                total_members += len(members)
                print(f"Found {len(members)} members (Total: {total_members})")

                # Be polite: delay to avoid overwhelming server
                time.sleep(1)

            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page}: {e}")
                break
            except Exception as e:
                print(f"Error parsing page {page}: {e}")
                continue

    print(f"\nCompleted! Total members scraped: {total_members}")
    print(f"Data saved to: {output_file}")
    print("\nYou can open this CSV file in Excel:")
    print("  - Open Excel")
    print("  - File > Open > select bgmea_members.csv")
    print("  - Excel will guide you through the import wizard")

if __name__ == '__main__':
    main()
