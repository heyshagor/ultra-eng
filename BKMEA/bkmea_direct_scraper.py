#!/usr/bin/env python3
"""
BKMEA Member Detail Scraper
Directly scrape member detail pages using member IDs.
The BKMEA site uses a specific table structure:
  - 3-column rows: [Label, "", Value] for main company info
  - 2-column rows: [Label, Value] for subsections
  - 1-column rows: Section headers (e.g., "Owner Details")

Usage:
  python bkmea_direct_scraper.py --ids 1730,2820,2819
  python bkmea_direct_scraper.py --range 1-100
  python bkmea_direct_scraper.py --file ids.txt
"""

import requests
import csv
import time
import re
import argparse
from pathlib import Path
from collections import defaultdict

BASE_URL = "https://member.bkmea.com"
DETAIL_URL_TEMPLATE = f"{BASE_URL}/member/details/{{member_id}}"
OUTPUT_FILE = 'bkmea_members_data.csv'
DETAIL_DELAY = 1  # seconds between requests (be polite)

def fetch(url):
    """Fetch URL with headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text

def parse_table_rows(html):
    """Parse the main table and return structured data"""
    # Find main table
    table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
    if not table_match:
        return {}

    table_html = table_match.group(1)
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)

    data = {}
    current_section = 'main'

    for row in rows:
        # Extract cells
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
        cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]

        if not cells:
            continue

        # Determine row type by cell count
        if len(cells) == 1:
            # Section header (e.g., "Owner Details", "Representative Details")
            current_section = cells[0]
            data[current_section] = {}
        elif len(cells) == 2:
            # Two-column: [Label, Value] - subsection data
            label, value = cells
            if current_section not in data:
                data[current_section] = {}
            data[current_section][label] = value
        elif len(cells) >= 3:
            # Three-column: [Label, "", Value] - main company info
            label = cells[0]
            value = cells[2] if len(cells) > 2 else ''
            data[label] = value

    return data

def parse_detail_page(html):
    """Parse member detail page and return flattened data"""
    raw_data = parse_table_rows(html)

    # Flatten the hierarchical structure
    flattened = {}

    # Main company info
    company_fields = {
        'Factory Name': 'company_name',
        'BKMEA Membership No.': 'bkmea_membership_no',
        'Membership Category': 'membership_category',
        'Date of Establishedment': 'establishment_date',
        'Factory Adress': 'factory_address',
        'Mailing Address': 'mailing_address',
        'Website': 'website',
        'Email Address': 'email',
        'Phone': 'phone',
        'Production Capacity': 'production_capacity',
        'Products': 'products',
    }

    for raw_label, field_key in company_fields.items():
        flattened[field_key] = raw_data.get(raw_label, '')

    # Owner Details section
    owner_section = raw_data.get('Owner Details', {})
    flattened['owner_name'] = owner_section.get('Owner Name', '')
    flattened['owner_email'] = owner_section.get('Email Address', '')
    flattened['owner_mobile'] = owner_section.get('Mobile No.', '')

    # Representative Details section
    rep_section = raw_data.get('Representative Details', {})
    flattened['rep_name'] = rep_section.get('Name', '')
    flattened['rep_email'] = rep_section.get('Email Address', '')
    flattened['rep_mobile'] = rep_section.get('Mobile No.', '')

    # Number of Employees section (ratios)
    employees_section = raw_data.get('Number of Employees', {})
    flattened['employees_male'] = employees_section.get('Male', '')
    flattened['employees_female'] = employees_section.get('Female', '')
    flattened['employees_others'] = employees_section.get('Others', '')
    flattened['employees_total'] = employees_section.get('Total', '')

    # Number of Machine section
    machines_section = raw_data.get('Number of Machine', {})
    flattened['machines_knitting'] = machines_section.get('Knitting', '')
    flattened['machines_dyeing'] = machines_section.get('Dyeing', '')

    # EPB Registration (may be in main table or elsewhere)
    flattened['epb_reg_no'] = ''

    # Extract any EPB number from the raw data
    for key, value in raw_data.items():
        if isinstance(value, str) and 'EPB' in key:
            flattened['epb_reg_no'] = value
            break
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                if 'EPB' in subkey:
                    flattened['epb_reg_no'] = subvalue
                    break

    return flattened, raw_data

def flatten_row(member_id, detail_url, details):
    """Convert parsed details to flat CSV row"""
    row = {
        'Member_ID': member_id,
        'Detail_URL': detail_url,
    }

    # Main fields mapping to friendly column names
    field_mapping = {
        'company_name': 'Company_Name',
        'bkmea_membership_no': 'BKMEA_Membership_No',
        'membership_category': 'Membership_Category',
        'establishment_date': 'Establishment_Date',
        'factory_address': 'Factory_Address',
        'mailing_address': 'Mailing_Address',
        'website': 'Website',
        'email': 'Email',
        'phone': 'Phone',
        'production_capacity': 'Production_Capacity',
        'products': 'Products',
        'owner_name': 'Owner_Name',
        'owner_email': 'Owner_Email',
        'owner_mobile': 'Owner_Mobile',
        'rep_name': 'Representative_Name',
        'rep_email': 'Representative_Email',
        'rep_mobile': 'Representative_Mobile',
        'employees_male': 'Employees_Male',
        'employees_female': 'Employees_Female',
        'employees_others': 'Employees_Others',
        'employees_total': 'Employees_Total',
        'machines_knitting': 'Machines_Knitting',
        'machines_dyeing': 'Machines_Dyeing',
        'epb_reg_no': 'EPB_Reg_No',
    }

    for key, col_name in field_mapping.items():
        row[col_name] = details.get(key, '')

    return row

def test_member(member_id):
    """Test scraping a single member"""
    url = DETAIL_URL_TEMPLATE.format(member_id=member_id)
    print(f"Testing: {url}")
    try:
        html = fetch(url)
        if html and len(html) > 1000:
            print(f"✓ Success! Fetched {len(html)} bytes")
            details, raw = parse_detail_page(html)
            print(f"✓ Parsed successfully")
            print(f"  Company: {details.get('company_name', 'N/A')}")
            print(f"  Membership: {details.get('bkmea_membership_no', 'N/A')}")
            print(f"  Owner: {details.get('owner_name', 'N/A')}")
            print(f"  Contact: {details.get('owner_mobile', 'N/A')}")
            print(f"  Email: {details.get('owner_email', 'N/A')}")
            return True
        else:
            print("✗ Page content too short or empty")
            return False
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"✗ Member {member_id} not found (404)")
        else:
            print(f"✗ HTTP Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def scrape_members(member_ids, resume_from=0):
    """Scrape multiple members and save to CSV"""
    output_path = Path(OUTPUT_FILE)

    # Check if existing file to resume
    if output_path.exists() and resume_from == 0:
        with open(output_path, 'r', encoding='utf-8') as f:
            existing_count = sum(1 for _ in f) - 1
        if existing_count > 0:
            resume_from = existing_count
            print(f"Found existing output with {existing_count} rows, will resume from index {resume_from}")

    # Process members
    for idx, member_id in enumerate(member_ids):
        if idx < resume_from:
            continue

        url = DETAIL_URL_TEMPLATE.format(member_id=member_id)
        print(f"[{idx+1}/{len(member_ids)}] ID {member_id}...", end=' ')

        try:
            html = fetch(url)
            details, raw = parse_detail_page(html)

            row = flatten_row(member_id, url, details)

            # Write row (with header if new file)
            file_exists = output_path.exists()
            with open(output_path, 'a' if file_exists else 'w', newline='', encoding='utf-8') as f:
                if not file_exists:
                    # Determine fieldnames from first row
                    fieldnames = ['Member_ID', 'Detail_URL'] + sorted([k for k in row.keys() if k not in ('Member_ID', 'Detail_URL')])
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                else:
                    # Append - need to ensure all columns match
                    with open(output_path, 'r', encoding='utf-8') as rf:
                        reader = csv.DictReader(rf)
                        fieldnames = reader.fieldnames

                    # Add any new columns
                    new_columns = set(row.keys()) - set(fieldnames)
                    if new_columns:
                        print(f"\n⚠ New columns detected: {new_columns}")
                        print("  Recreating file with expanded headers...")
                        # Read all existing rows
                        with open(output_path, 'r', encoding='utf-8') as rf:
                            existing_rows = list(csv.DictReader(rf))
                        fieldnames = sorted(list(set(fieldnames + list(row.keys()))))
                        # Rewrite everything
                        with open(output_path, 'w', newline='', encoding='utf-8') as wf:
                            writer = csv.DictWriter(wf, fieldnames=fieldnames)
                            writer.writeheader()
                            writer.writerows(existing_rows)
                            writer.writerow({k: row.get(k, '') for k in fieldnames})
                        print("  ✓ Saved with new columns")
                        time.sleep(DETAIL_DELAY)
                        continue

                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writerow(row)

            if not output_path.exists():
                output_path.touch()
                with open(output_path, 'a', newline='', encoding='utf-8') as f:
                    fieldnames = ['Member_ID', 'Detail_URL'] + sorted([k for k in row.keys() if k not in ('Member_ID', 'Detail_URL')])
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerow(row)

            print("OK")
            time.sleep(DETAIL_DELAY)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"Not found (404), skipping")
            else:
                print(f"HTTP error: {e}, skipping")
            time.sleep(DETAIL_DELAY)
            continue
        except Exception as e:
            print(f"Error: {e}, skipping")
            time.sleep(DETAIL_DELAY)
            continue

    print(f"\n✓ Scraping complete! Data saved to {OUTPUT_FILE}")
    print(f"  Total members processed: {len(member_ids)}")
    print(f"  Output file: {output_path.absolute()}")
    print("\nTo open in Excel:")
    print("  - Open Excel")
    print("  - File > Open > select bkmea_members_data.csv")
    print("  - Choose 'Delimited' > Comma > Finish")

def main():
    parser = argparse.ArgumentParser(description='BKMEA Member Detail Scraper')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--ids', type=str, help='Comma-separated member IDs (e.g., "1730,2820,2819")')
    group.add_argument('--range', type=str, help='Range of IDs (e.g., "1-100")')
    group.add_argument('--file', type=str, help='Text file with one member ID per line')
    group.add_argument('--test', type=str, help='Test a single member ID to see if scraping works')

    args = parser.parse_args()

    if args.test:
        success = test_member(args.test)
        exit(0 if success else 1)

    # Determine member IDs list
    member_ids = []

    if args.ids:
        member_ids = [mid.strip() for mid in args.ids.split(',') if mid.strip()]

    elif args.range:
        if '-' in args.range:
            start, end = map(int, args.range.split('-'))
            member_ids = list(range(start, end + 1))
        else:
            start = int(args.range)
            member_ids = [start]

    elif args.file:
        with open(args.file, 'r') as f:
            member_ids = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    # Validate IDs are numeric
    try:
        member_ids = [str(int(mid)) for mid in member_ids]
    except ValueError:
        print("Error: All member IDs must be numeric")
        exit(1)

    print(f"BKMEA Member Scraper")
    print(f"=" * 50)
    print(f"Total members to scrape: {len(member_ids)}")
    if member_ids:
        print(f"Range: {member_ids[0]} to {member_ids[-1]}")

    # Quick test of first member
    print(f"\nTesting first member (ID {member_ids[0]})...")
    if not test_member(member_ids[0]):
        print("\n⚠ WARNING: First member test failed!")
        print("This might mean:")
        print("  1. The member ID is invalid")
        print("  2. The site structure is different than expected")
        response = input("\nContinue anyway? (y/N): ").lower()
        if response != 'y':
            exit(1)

    # Proceed with scraping
    print(f"\nStarting full scrape...")
    scrape_members(member_ids)

if __name__ == '__main__':
    main()
