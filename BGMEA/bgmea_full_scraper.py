#!/usr/bin/env python3
"""
BGMEA Complete Member Data Scraper
Scrapes list page and then each member's detail page to get all data.
Outputs a comprehensive CSV file.
"""

import requests
import csv
import time
import re
from html.parser import HTMLParser
from pathlib import Path

# Constants
BASE_URL = "https://www.bgmea.com.bd"
LIST_URL = f"{BASE_URL}/page/member-list"
OUTPUT_FILE = 'bgmea_all_members.csv'
DETAIL_DELAY = 1  # seconds between detail page requests (politeness)
START_FROM = 0  # index to start from (for resuming)

class MemberListParser(HTMLParser):
    """Parser for member list page table"""
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

def fetch(url):
    """Fetch URL with headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text

def parse_list_page(html):
    """Parse member list page HTML and return list of member rows"""
    parser = MemberListParser()
    parser.feed(html)
    return parser.rows

def determine_max_pages():
    """Fetch first page and find total number of pages from pagination links"""
    html = fetch(LIST_URL + "?page=1")
    page_numbers = re.findall(r'page=(\d+)', html)
    if page_numbers:
        max_page = max([int(p) for p in page_numbers if int(p) < 1000])
        return max_page
    return 213  # default

def scrape_member_list():
    """Scrape all member list pages and return list of members (with detail URL)"""
    max_page = determine_max_pages()
    print(f"Scraping member list: {max_page} pages")

    all_members = []
    for page in range(1, max_page + 1):
        try:
            print(f"  Page {page}/{max_page}...", end=' ')
            html = fetch(LIST_URL + f"?page={page}")
            members = parse_list_page(html)
            if members:
                all_members.extend(members)
                print(f"{len(members)} members")
            else:
                print("no data, stopping")
                break
            time.sleep(0.5)  # polite delay between list pages
        except Exception as e:
            print(f"Error: {e}")
            break

    # Ensure each member row has 5 columns: company, reg, contact, email, detail_url
    cleaned = []
    for row in all_members:
        if len(row) >= 5 and row[4].startswith(BASE_URL + '/member/'):
            cleaned.append(row[:5])
        elif len(row) == 4:
            # Missing details URL? Try to construct from reg number? Likely incomplete; skip
            continue
    print(f"Total members collected: {len(cleaned)}")
    return cleaned

def parse_detail_page(html):
    """Parse a member detail page and return a dict of additional fields"""
    data = {}

    # Helper: get td content for a given label, allowing any tags inside th
    def get_td_content(label):
        # regex: <th ...> any content that includes label ... </th> optional whitespace <td ...> (capture group) </td>
        pattern = rf'<th[^>]*>.*?{re.escape(label)}.*?</th>\s*<td[^>]*>(.*?)</td>'
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            # Strip HTML tags from content
            content = m.group(1)
            # Replace <br> with newlines, then remove all other tags
            text = re.sub(r'<br\s*/?>', '\n', content)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
        return ''

    # EPB Reg No (likely without inner tags but use same helper)
    data['epb_reg_no'] = get_td_content('EPB Reg No')

    # Director Information table
    directors = []
    # Find all 4-column rows inside the director table. To avoid picking up unrelated tables, we might limit to after "Director Informaiton" but okay.
    dir_rows = re.findall(
        r'<tr>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>\s*</tr>',
        html
    )
    for pos, name, mobile, email in dir_rows:
        directors.append({
            'position': pos.strip(),
            'name': name.strip(),
            'mobile': mobile.strip(),
            'email': email.strip()
        })
    data['directors'] = directors

    # Address tab: Contact Person info (Name, Designation, Phone, Email) - these are in strong tags within a td
    m_name = re.search(r'<strong>Name:</strong>\s*([^<]+)<', html)
    data['contact_name'] = m_name.group(1).strip() if m_name else ''
    m_desig = re.search(r'<strong>Designation:</strong>\s*([^<]+)<', html)
    data['contact_designation'] = m_desig.group(1).strip() if m_desig else ''
    m_phone = re.search(r'<strong>Phone:</strong>\s*([^<]+)<', html)
    data['contact_phone'] = m_phone.group(1).strip() if m_phone else ''
    m_email_addr = re.search(r'<strong>Email:</strong>\s*([^<]+)<', html)
    data['contact_email'] = m_email_addr.group(1).strip() if m_email_addr else ''

    # Mailing Address (note: the site uses "Mailling Address" with typo)
    addr_text = get_td_content('Mailling Address')
    data['mailing_address'] = addr_text

    # Final Information tab fields using helper
    data['website'] = get_td_content('Website')
    data['establishment_date'] = get_td_content('Date of Establishment')
    data['certifications'] = get_td_content('Certifications')
    data['principal_product'] = get_td_content('Principal Exportable Product')
    data['annual_turnover'] = get_td_content('Annual Turnover')

    # Factory Types: capture inner table
    factory_types = []
    ft_pattern = r'<th[^>]*>.*?Factory Type.*?</th>.*?<td[^>]*>\s*<table[^>]*>(.*?)</table>'
    m_ft = re.search(ft_pattern, html, re.DOTALL | re.IGNORECASE)
    if m_ft:
        table_inner = m_ft.group(1)
        ft_rows = re.findall(r'<tr[^>]*>\s*<td[^>]*>([^<]+)</td>\s*<td[^>]*>([^<]+)</td>', table_inner, re.DOTALL)
        for ftype, priority in ft_rows:
            factory_types.append(f"{ftype.strip()} (Priority {priority.strip()})")
    else:
        # fallback to simple text
        ft_text = get_td_content('Factory Type')
        if ft_text:
            factory_types.append(ft_text)
    data['factory_types'] = '; '.join(factory_types)

    # No. of Employees: may have nested table
    emp_info = ''
    emp_pattern = r'<th[^>]*>.*?No\.? of Employees.*?</th>.*?<td[^>]*>\s*<table[^>]*>(.*?)</table>'
    m_emp_table = re.search(emp_pattern, html, re.DOTALL | re.IGNORECASE)
    if m_emp_table:
        table_inner = m_emp_table.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_inner, re.DOTALL)
        parts = []
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if cells:
                cell_texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                if len(cell_texts) >= 2:
                    parts.append(' | '.join(cell_texts))
        emp_info = '; '.join(parts)
    else:
        # fallback to simple text extraction
        emp_info = get_td_content('No. of Employees')
    data['employees'] = emp_info

    # No of Machines: may have nested table
    mach_info = ''
    mach_pattern = r'<th[^>]*>.*?No of Machines.*?</th>.*?<td[^>]*>\s*<table[^>]*>(.*?)</table>'
    m_mach_table = re.search(mach_pattern, html, re.DOTALL | re.IGNORECASE)
    if m_mach_table:
        table_inner = m_mach_table.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_inner, re.DOTALL)
        parts = []
        for row in rows:
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if cells:
                cell_texts = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]
                if len(cell_texts) >= 2:
                    parts.append(' | '.join(cell_texts))
        mach_info = '; '.join(parts)
    else:
        mach_info = get_td_content('No of Machines')
    data['machines'] = mach_info

    # Production Capacity: likely simple text
    cap_text = get_td_content('Production Capacity')
    data['production_capacity'] = cap_text

    return data

def main():
    print("BGMEA Full Member Data Scraper")
    print("=" * 40)

    # Step 1: Get member list (from existing CSV if available)
    list_csv = 'bgmea_members.csv'
    members = []
    if Path(list_csv).exists():
        print(f"Reading member list from {list_csv}...")
        with open(list_csv, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            members = [row for row in reader if len(row) >= 5]
        print(f"Found {len(members)} members in CSV")
    else:
        print("Member list not found. Scraping list pages...")
        members = scrape_member_list()
        # Save intermediate list
        with open(list_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Company Name', 'BGMEA Reg No', 'Contact Person', 'Email Address', 'Details URL'])
            writer.writerows(members)
        print(f"Saved list to {list_csv}")

    # Step 2: Define output CSV with full columns
    out_header = [
        'Company Name', 'BGMEA Reg No', 'Contact Person', 'Email Address', 'Details URL',
        'EPB Reg No', 'Contact Name', 'Contact Designation', 'Contact Phone', 'Contact Email',
        'Mailing Address', 'Website', ' Establishment Date', 'Factory Types',
        'No. of Employees', 'No. of Machines', 'Production Capacity', 'Certifications',
        'Principal Exportable Product', 'Annual Turnover',
        # Director columns (up to 5 directors)
        'Director1_Position', 'Director1_Name', 'Director1_Mobile', 'Director1_Email',
        'Director2_Position', 'Director2_Name', 'Director2_Mobile', 'Director2_Email',
        'Director3_Position', 'Director3_Name', 'Director3_Mobile', 'Director3_Email',
        'Director4_Position', 'Director4_Name', 'Director4_Mobile', 'Director4_Email',
        'Director5_Position', 'Director5_Name', 'Director5_Mobile', 'Director5_Email',
    ]

    # Check if output file exists to resume
    start_idx = 0
    if Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            existing_lines = sum(1 for _ in f) - 1  # minus header
        start_idx = existing_lines
        print(f"Resuming from index {start_idx}")
        # Open in append mode
        out_f = open(OUTPUT_FILE, 'a', newline='', encoding='utf-8')
        writer = csv.writer(out_f)
    else:
        start_idx = 0
        out_f = open(OUTPUT_FILE, 'w', newline='', encoding='utf-8')
        writer = csv.writer(out_f)
        writer.writerow(out_header)

    print(f"Fetching detail pages for {len(members)} members (starting at {start_idx})...")

    # Process each member
    for idx, member in enumerate(members[start_idx:], start=start_idx):
        company, reg_no, contact, email, detail_url = member[:5]
        try:
            print(f"[{idx+1}/{len(members)}] {company[:50]}...", end=' ')
            html = fetch(detail_url)

            details = parse_detail_page(html)

            # Prepare row
            row = [
                company, reg_no, contact, email, detail_url,
                details.get('epb_reg_no', ''),
                details.get('contact_name', ''),
                details.get('contact_designation', ''),
                details.get('contact_phone', ''),
                details.get('contact_email', ''),
                details.get('mailing_address', ''),
                details.get('website', ''),
                details.get('establishment_date', ''),
                details.get('factory_types', ''),
                details.get('employees', ''),
                details.get('machines', ''),
                details.get('production_capacity', ''),
                details.get('certifications', ''),
                details.get('principal_product', ''),
                details.get('annual_turnover', ''),
            ]

            # Add director slots (up to 5)
            directors = details.get('directors', [])
            for i in range(5):
                if i < len(directors):
                    d = directors[i]
                    row.extend([d['position'], d['name'], d['mobile'], d['email']])
                else:
                    row.extend(['', '', '', ''])

            writer.writerow(row)
            out_f.flush()
            print("OK")
            time.sleep(DETAIL_DELAY)  # be polite
        except Exception as e:
            print(f"Error: {e}")
            # Write empty row? skip? We'll skip and continue
            continue

    out_f.close()
    print(f"\nAll done! Complete data saved to {OUTPUT_FILE}")
    print(f"Total records: {len(members)}")
    print("\nYou can open the CSV file in Excel:")
    print("  - Open Excel")
    print("  - File > Open > select bgmea_all_members.csv")
    print("  - If prompted, choose 'Delimited' and select Comma as delimiter")

if __name__ == '__main__':
    main()
