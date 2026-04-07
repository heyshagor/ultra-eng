#!/usr/bin/env python3
"""
BJGEA Member List Scraper
Scrapes all member data from bjgea.net.bd and exports to CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re

BASE_URL = "https://bjgea.net.bd"
MEMBERS_URL = f"{BASE_URL}/content.php?f=Member-List&pg={{page}}"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def decode_cfemail(hex_str):
    """Decode Cloudflare protected email (data-cfemail attribute)."""
    try:
        r = int(hex_str[:2], 16)
        email = ''.join(chr(int(hex_str[i:i+2], 16) ^ r) for i in range(2, len(hex_str), 2))
        return email
    except Exception:
        return ''

def get_member_container_divs(html_content):
    """Extract the list of grid divs that contain member data."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all divs with grid classes
    all_grid_divs = soup.find_all('div', class_=lambda x: x and 'col-lg-' in str(x))

    # Group by parent
    parents = {}
    for div in all_grid_divs:
        parent = div.parent
        if parent:
            pid = id(parent)
            parents[pid] = parents.get(pid, []) + [div]

    if not parents:
        return []

    # Find parent with most grid children
    biggest_pid = max(parents.items(), key=lambda x: len(x[1]))[0]
    member_divs = parents[biggest_pid]

    # Filter: keep only divs that contain data (skip headers, nav, empty)
    data_divs = []
    for div in member_divs:
        text = div.get_text(strip=True)
        if not text:
            continue
        if any(skip in text for skip in ['● বাংলা', '● English', ' Hindi', 'Tuesday', 'April', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'January', 'February', 'March', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
            continue
        data_divs.append(div)

    return data_divs

def parse_name_field(text):
    """Extract name, designation, and member_since from name column."""
    result = {'name': '', 'designation': '', 'member_since': ''}

    # Extract Member Since
    since_match = re.search(r'Member\s+Since\s*[:\s]*(\d{4})', text)
    if since_match:
        result['member_since'] = since_match.group(1)
        text = text[:since_match.start()] + text[since_match.end():]

    # Extract designation (BJGEA Desig: ...)
    desig_match = re.search(r'BJGEA\s+Desig\s*[:\s]*([A-Za-z\s]+(?:\([^)]*\))?)', text)
    if desig_match:
        result['designation'] = desig_match.group(1).strip()
        text = re.sub(r'BJGEA\s+Desig\s*[:\s]*[A-Za-z\s]+(?:\([^)]*\))?', '', text)

    result['name'] = re.sub(r'\s+', ' ', text).strip()
    return result

def parse_org_field(text):
    """Extract organization (company name) and business role and address."""
    result = {'organization': '', 'org_role': '', 'address': ''}

    # Look for known business roles
    roles = ['Proprietor', 'Managing Director', 'Director', 'Owner', 'CEO', 'General Manager',
             'Executive Officer', 'Manager', 'Officer', 'Partner', 'President', 'Vice President']

    text_before_role = text
    address_part = ''

    for role in roles:
        if role in text:
            result['org_role'] = role
            parts = text.split(role, 1)
            result['organization'] = parts[0].strip()
            if len(parts) > 1:
                address_part = parts[1].strip()
            break

    if not result['org_role']:
        # No explicit role - try to find where address starts (contains city/Dhaka/road)
        # City names
        cities = ['Dhaka', 'Chittagong', 'Sylhet', 'Rajshahi', 'Barisal', 'Khulna', 'Rangpur', 'Mymensingh', 'Comilla', 'Narayanganj']
        # Address indicators
        addr_indicators = ['Road', 'House', 'Building', 'Tower', 'Floor', 'Level', 'Ward', 'Block', 'Area', 'Village', 'Post', 'P.O.', 'PS', 'Dist', 'C/A', 'Motijheel', 'Uttara', 'Gulshan', 'Banani', 'Dhanmondi', 'Mirpur', 'Shahjadpur']

        found = False
        for indicator in addr_indicators:
            idx = text.lower().find(indicator.lower())
            if idx > 5:  # Make sure not at very start
                result['address'] = text[idx:].strip()
                result['organization'] = text[:idx].strip()
                found = True
                break

        if not found:
            result['organization'] = text
    else:
        # We have org_role; address_part holds the remaining text
        if address_part:
            result['address'] = address_part

    # Clean up
    for key in ['organization', 'address']:
        if result[key]:
            result[key] = re.sub(r'\s+', ' ', result[key]).strip()

    return result

def parse_contact_field(div):
    """Extract mobile, tel, and email from contact column div."""
    result = {'mobile': '', 'tel': '', 'email': ''}

    # First, check for Cloudflare protected email
    cf_email_link = div.find('a', class_='__cf_email__')
    if cf_email_link and cf_email_link.get('data-cfemail'):
        hex_str = cf_email_link['data-cfemail']
        result['email'] = decode_cfemail(hex_str)

    # Get full text for phones
    text = div.get_text(strip=True)

    # Extract all Bangladeshi phone numbers (11 digits starting with 01)
    phones = re.findall(r'(?:\+?88)?01[3-9]\d{8}', text)

    # Extract mobile (marked with Mob:)
    mob_match = re.search(r'Mob\s*[:\s]*([+\d\s,]+)', text, re.IGNORECASE)
    if mob_match:
        mob_nums = re.findall(r'(?:\+?88)?01[3-9]\d{8}', mob_match.group(1))
        if mob_nums:
            result['mobile'] = mob_nums[0]
            # Remove these from phones list to avoid duplication
            phones = [p for p in phones if p not in mob_nums]

    # Extract Tel
    tel_match = re.search(r'Tel\s*[:\s]*([+\d\s,]+)', text, re.IGNORECASE)
    if tel_match:
        tel_nums = re.findall(r'(?:\+?88)?01[3-9]\d{8}|0\d{9,10}', tel_match.group(1))
        if tel_nums:
            result['tel'] = ', '.join(tel_nums)
            phones = [p for p in phones if p not in tel_nums]

    # If there are leftover phones and no mobile set, use first as mobile
    if not result['mobile'] and phones:
        result['mobile'] = phones[0]
        phones = phones[1:]

    # If still no tel and there are more phones, use as tel
    if not result['tel'] and phones:
        result['tel'] = ', '.join(phones)

    return result

def extract_members_from_html(html_content):
    """Extract members from the page HTML."""
    data_divs = get_member_container_divs(html_content)

    if not data_divs:
        print("No data divs found")
        return []

    print(f"Found {len(data_divs)} data divs")

    # Pattern: [S/N (number), name_div, org_div, contact_div] repeated
    members = []
    i = 0
    while i < len(data_divs):
        # Check if current div looks like an S/N (a small number)
        sn_text = data_divs[i].get_text(strip=True)
        if not sn_text.isdigit() or len(sn_text) > 3:
            i += 1
            continue

        # Have S/N, check next 3 divs exist
        if i + 3 >= len(data_divs):
            break

        name_div = data_divs[i+1]
        org_div = data_divs[i+2]
        contact_div = data_divs[i+3]

        # Parse fields
        name_data = parse_name_field(name_div.get_text(strip=True))
        org_data = parse_org_field(org_div.get_text(strip=True))
        contact_data = parse_contact_field(contact_div)

        member = {
            'company_name': org_data['organization'],
            'name': name_data['name'],
            'member_since': name_data['member_since'],
            'organization': org_data['org_role'],
            'address': org_data['address'],
            'mobile': contact_data['mobile'],
            'tel': contact_data['tel'],
            'email': contact_data['email'],
        }

        members.append(member)
        i += 4

    print(f"Extracted {len(members)} members")
    return members

def fetch_page(session, page_num):
    """Fetch a specific page of the member list."""
    url = MEMBERS_URL.format(page=page_num)
    print(f"Fetching page {page_num}...")
    try:
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching page {page_num}: {e}")
        return None

def scrape_all_members(max_pages=20, start_page=1):
    """Scrape all member pages."""
    all_members = []
    session = requests.Session()

    for page in range(start_page, start_page + max_pages):
        html = fetch_page(session, page)

        if not html:
            break

        members = extract_members_from_html(html)

        if not members:
            print(f"No members found on page {page}. Might be the end.")
            break

        all_members.extend(members)
        print(f"Found {len(members)} members on page {page} (total: {len(all_members)})")

        time.sleep(2)  # Be respectful

    return all_members

def save_to_csv(members, filename='bjgea_members.csv'):
    """Save members data to CSV file."""
    if not members:
        print("No members to save.")
        return

    fieldnames = ['company_name', 'name', 'member_since', 'organization',
                  'address', 'mobile', 'tel', 'email']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(members)

    print(f"\n✓ Saved {len(members)} members to {filename}")

def main():
    print("BJGEA Member List Scraper")
    print("=" * 60)

    try:
        all_members = scrape_all_members(max_pages=20, start_page=1)

        if all_members:
            save_to_csv(all_members)
            print("\n" + "=" * 60)
            print("SCRAPING COMPLETED!")
            print("=" * 60)
            print(f"Total members collected: {len(all_members)}")
        else:
            print("\nNo data collected.")

    except KeyboardInterrupt:
        print("\n\nScraping interrupted by user.")
        import sys; sys.exit(0)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback; traceback.print_exc()
        import sys; sys.exit(1)

if __name__ == "__main__":
    main()
