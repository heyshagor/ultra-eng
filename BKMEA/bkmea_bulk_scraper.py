#!/usr/bin/env python3
"""
BKMEA Bulk Member Scraper
Since the member list is not publicly accessible, this script discovers members by
testing sequential member IDs and scraping all valid ones.

Strategy:
1. Find the approximate maximum member ID using binary search
2. Test all IDs in the range 1 to max_id to find which ones are valid
3. Scrape each valid member's detail page

Usage:
  python bkmea_bulk_scraper.py
  python bkmea_bulk_scraper.py --max-id 5000
  python bkmea_bulk_scraper.py --start 2000 --end 3000
"""

import requests
import csv
import time
import re
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
from threading import Lock

BASE_URL = "https://member.bkmea.com"
DETAIL_URL_TEMPLATE = f"{BASE_URL}/member/details/{{member_id}}"
OUTPUT_FILE = 'bkmea_all_members.csv'
VALID_IDS_CACHE = 'bkmea_valid_ids.txt'

# Thread pool settings (be careful not to overload server)
MAX_WORKERS = 3  # concurrent requests (increase with caution)
DELAY_BETWEEN_REQUESTS = 0.5  # seconds

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
})

def check_member_exists(member_id):
    """Check if a member ID is valid by making a HEAD request"""
    url = DETAIL_URL_TEMPLATE.format(member_id=member_id)
    try:
        r = session.head(url, timeout=10, allow_redirects=True)
        return r.status_code == 200
    except:
        return False

def find_max_id_parallel(start=1000, step=1000, max_attempts=10):
    """Find the approximate maximum ID by testing exponential bounds"""
    print(" discovering maximum member ID...")
    print("-" * 50)

    # Find an upper bound
    current = start
    for attempt in range(max_attempts):
        if check_member_exists(current):
            print(f"ID {current:,} exists, trying higher...")
            start = current
            current += step
        else:
            print(f"ID {current:,} does NOT exist")
            break
    else:
        print(f"Reached max attempts ({max_attempts})")
        return current

    # Binary search between last valid (start) and first invalid (current)
    low = start
    high = current - 1
    print(f"\nBinary search between {low:,} and {high:,}...")

    while low < high:
        mid = (low + high + 1) // 2
        if check_member_exists(mid):
            print(f"  ID {mid:,} exists → lower bound = {mid:,}")
            low = mid
        else:
            print(f"  ID {mid:,} invalid → upper bound = {mid-1:,}")
            high = mid - 1
        time.sleep(0.2)

    print(f"\n✓ Maximum ID determined: {low:,}")
    return low

def scan_id_range(start_id, end_id, max_workers, auto_use_cache=False):
    """Scan a range of IDs and return list of valid IDs"""
    print(f"\nScanning IDs from {start_id:,} to {end_id:,}...")
    total = end_id - start_id + 1
    valid_ids = []

    # Check cache first
    cache_file = Path(VALID_IDS_CACHE)
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            cached_ids = [int(line.strip()) for line in f if line.strip()]
        print(f"Found {len(cached_ids)} IDs in cache")
        use_cache = auto_use_cache
        if not auto_use_cache:
            try:
                use_cache = input("Use cached valid IDs? (Y/n): ").lower() != 'n'
            except EOFError:
                use_cache = True
        if use_cache:
            return cached_ids

    # Use thread pool to speed up checking
    lock = Lock()
    checked_count = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(check_member_exists, i): i for i in range(start_id, end_id + 1)}

        for future in as_completed(futures):
            member_id = futures[future]
            try:
                exists = future.result()
                if exists:
                    with lock:
                        valid_ids.append(member_id)
                        print(f"  ✓ ID {member_id:,} valid (total found: {len(valid_ids)})", end='\r')
            except Exception as e:
                print(f"\n  ✗ ID {member_id}: error {e}")

            with lock:
                checked_count += 1
                if checked_count % 100 == 0:
                    print(f"\nProgress: {checked_count:,}/{total:,} checked, {len(valid_ids):,} valid", end='\r')

    print(f"\n\n✓ Scan complete: {len(valid_ids):,} valid IDs found out of {total:,} tested")

    # Save valid IDs to cache
    with open(cache_file, 'w') as f:
        for vid in sorted(valid_ids):
            f.write(f"{vid}\n")
    print(f"✓ Valid IDs saved to {VALID_IDS_CACHE}")

    return sorted(valid_ids)

def fetch_member_detail(member_id):
    """Fetch and parse full member details"""
    url = DETAIL_URL_TEMPLATE.format(member_id=member_id)
    try:
        html = session.get(url, timeout=30).text

        # Parse detail page (same as before)
        table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
        if not table_match:
            return None

        table_html = table_match.group(1)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL | re.IGNORECASE)

        data = {}
        current_section = 'main'

        for row in rows:
            cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', row, re.DOTALL | re.IGNORECASE)
            if not cells:
                continue

            clean_cells = [re.sub(r'<[^>]+>', '', c).strip() for c in cells]

            if len(clean_cells) == 1:
                current_section = clean_cells[0]
                data[current_section] = {}
            elif len(clean_cells) == 2:
                label, value = clean_cells
                if current_section not in data:
                    data[current_section] = {}
                data[current_section][label] = value
            elif len(clean_cells) >= 3:
                label = clean_cells[0]
                value = clean_cells[2] if len(clean_cells) > 2 else ''
                data[label] = value

        # Flatten
        flattened = {
            'member_id': member_id,
            'detail_url': url,
        }

        field_mapping = {
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

        for raw, key in field_mapping.items():
            flattened[key] = data.get(raw, '')

        # Sections
        owner = data.get('Owner Details', {})
        flattened['owner_name'] = owner.get('Owner Name', '')
        flattened['owner_email'] = owner.get('Email Address', '')
        flattened['owner_mobile'] = owner.get('Mobile No.', '')

        rep = data.get('Representative Details', {})
        flattened['rep_name'] = rep.get('Name', '')
        flattened['rep_email'] = rep.get('Email Address', '')
        flattened['rep_mobile'] = rep.get('Mobile No.', '')

        emp = data.get('Number of Employees', {})
        flattened['employees_male'] = emp.get('Male', '')
        flattened['employees_female'] = emp.get('Female', '')
        flattened['employees_total'] = emp.get('Total', '')

        mach = data.get('Number of Machine', {})
        flattened['machines_knitting'] = mach.get('Knitting', '')
        flattened['machines_dyeing'] = mach.get('Dyeing', '')

        # EPB Reg No
        for key, value in data.items():
            if isinstance(value, str) and 'EPB' in key and 'Reg' in key:
                flattened['epb_reg_no'] = value
                break
        else:
            flattened['epb_reg_no'] = ''

        return flattened

    except Exception as e:
        print(f"\n  ✗ Error fetching ID {member_id}: {e}")
        return None

def scrape_all_members(valid_ids, resume_from=0, max_workers=MAX_WORKERS):
    """Scrape all valid member IDs and save to CSV"""
    total = len(valid_ids)

    # CSV headers
    headers = [
        'member_id', 'detail_url', 'company_name', 'bkmea_membership_no',
        'membership_category', 'epb_reg_no', 'establishment_date',
        'factory_address', 'mailing_address', 'website', 'email', 'phone',
        'owner_name', 'owner_mobile', 'owner_email',
        'rep_name', 'rep_mobile', 'rep_email',
        'employees_male', 'employees_female', 'employees_total',
        'machines_knitting', 'machines_dyeing',
        'production_capacity', 'products',
    ]

    output_path = Path(OUTPUT_FILE)
    mode = 'a' if resume_from > 0 else 'w'
    out_f = open(output_path, mode, newline='', encoding='utf-8')
    writer = csv.DictWriter(out_f, fieldnames=headers)

    if resume_from == 0:
        writer.writeheader()

    success = 0
    errors = 0

    print(f"\nScraping {total:,} members (starting from {resume_from:,})...")
    print("=" * 60)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {}
        for idx, member_id in enumerate(valid_ids):
            if idx < resume_from:
                continue
            futures[executor.submit(fetch_member_detail, member_id)] = (idx, member_id)

        for future in as_completed(futures):
            idx, member_id = futures[future]
            try:
                details = future.result(timeout=30)
                if details:
                    # Ensure all fields exist
                    row = {h: details.get(h, '') for h in headers}
                    writer.writerow(row)
                    out_f.flush()
                    success += 1
                else:
                    errors += 1
            except Exception as e:
                errors += 1
                print(f"\n  ✗ ID {member_id}: {str(e)[:100]}")

            # Progress update
            if (idx + 1) % 10 == 0:
                print(f"\nProgress: {idx+1:,}/{total:,} | Success: {success:,} | Errors: {errors:,}", end='')

            time.sleep(DELAY_BETWEEN_REQUESTS)

    out_f.close()
    print(f"\n" + "=" * 60)
    print("SCRAPING COMPLETE!")
    print(f"Total members processed: {total:,}")
    print(f"Successfully saved: {success:,}")
    print(f"Failed: {errors:,}")
    print(f"Output file: {output_path.absolute()}")

def main():
    parser = argparse.ArgumentParser(description='BKMEA Bulk Member Scraper')
    parser.add_argument('--max-id', type=int, default=3000, help='Maximum member ID to scan (default: 3000)')
    parser.add_argument('--start', type=int, default=1, help='Starting member ID (default: 1)')
    parser.add_argument('--end', type=int, help='Ending member ID (overrides --max-id)')
    parser.add_argument('--workers', type=int, default=3, help=f'Number of concurrent workers (default: {MAX_WORKERS})')
    parser.add_argument('--resume', action='store_true', help='Resume from existing output/cache')
    parser.add_argument('--skip-scan', action='store_true', help='Skip ID scanning, use cached valid IDs')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt and start immediately')

    args = parser.parse_args()

    end_id = args.end if args.end else args.max_id

    print("BKMEA Bulk Member Scraper")
    print("=" * 60)

    # Step 1: Find valid member IDs
    if args.skip_scan and Path(VALID_IDS_CACHE).exists():
        with open(VALID_IDS_CACHE, 'r') as f:
            valid_ids = [int(line.strip()) for line in f]
        print(f"Loaded {len(valid_ids):,} valid IDs from cache")
    else:
        valid_ids = scan_id_range(args.start, end_id, max_workers=args.workers, auto_use_cache=args.yes)
        valid_ids = [vid for vid in valid_ids if vid <= args.max_id]

    if not valid_ids:
        print("No valid member IDs found. Exiting.")
        return

    print(f"\nTotal valid members to scrape: {len(valid_ids):,}")

    # Step 2: Scrape details
    resume_from = 0
    if args.resume and Path(OUTPUT_FILE).exists():
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            resume_from = sum(1 for _ in f) - 1
        print(f"Resuming from member #{resume_from + 1:,}")

    if not args.yes:
        confirm = input("\nStart scraping? (Y/n): ").lower()
        if confirm == 'n':
            print("Aborted.")
            return

    scrape_all_members(valid_ids, resume_from, max_workers=args.workers)

if __name__ == '__main__':
    main()
