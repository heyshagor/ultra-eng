#!/usr/bin/env python3
"""
Debug helper for BKMEA scraper
Fetches a member detail page and shows what fields can be extracted.
Use this to identify correct field labels for your specific site.
"""

import requests
import re

def fetch(url):
    """Fetch URL with headers"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.text

def extract_all_table_headers(html):
    """Extract all table header labels to see what fields are available"""
    # Find all th elements
    th_pattern = r'<th[^>]*>(.*?)</th>'
    headers = re.findall(th_pattern, html, re.DOTALL | re.IGNORECASE)
    # Clean up
    cleaned = []
    for h in headers:
        h_clean = re.sub(r'<[^>]+>', '', h).strip()
        if h_clean:
            cleaned.append(h_clean)
    return cleaned

def show_field_labels(html):
    """Display field labels found in the page"""
    headers = extract_all_table_headers(html)
    print("\n FIELD LABELS FOUND IN DETAIL PAGE:")
    print("=" * 50)
    unique = sorted(set(headers))
    for h in unique:
        print(f"  - {h}")

def test_extraction(html):
    """Test extraction with common field patterns"""
    print("\n TESTING COMMON FIELD EXTRACTIONS:")
    print("=" * 50)

    test_labels = [
        'EPB Reg No', 'EPB Registration No',
        'Contact Person', 'Name', 'Contact Name',
        'Designation', 'Position',
        'Phone', 'Mobile', 'Contact No',
        'Email', 'E-mail',
        'Address', 'Mailing Address', 'Office Address',
        'Website', 'Web Site',
        'Date of Establishment', 'Establishment',
        'Certifications', 'Certification',
        'Principal Product', 'Main Product', 'Product',
        'Annual Turnover', 'Turnover',
        'Factory Type', 'Type of Factory',
        'No. of Employees', 'Employees',
        'No of Machines', 'Machines',
        'Production Capacity', 'Capacity',
    ]

    for label in test_labels:
        pattern = rf'<th[^>]*>.*?{re.escape(label)}.*?</th>\s*<td[^>]*>(.*?)</td>'
        m = re.search(pattern, html, re.DOTALL | re.IGNORECASE)
        if m:
            content = m.group(1)
            text = re.sub(r'<br\s*/?>', '\n', content)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            print(f"\n  {label}:")
            print(f"    {text[:100]}{'...' if len(text) > 100 else ''}")

def main():
    print("BKMEA Scraper Debug Tool")
    print("=" * 50)

    # You can change this URL to test different members
    test_url = input("Enter member detail URL to test (or press Enter for default 1730): ").strip()
    if not test_url:
        test_url = "https://member.bkmea.com/member/details/1730"

    print(f"\nFetching: {test_url}")
    try:
        html = fetch(test_url)
        print(f"Successfully fetched {len(html)} bytes")

        show_field_labels(html)
        test_extraction(html)

        # Optionally save HTML for manual inspection
        save = input("\nDo you want to save the HTML to a file for inspection? (y/n): ").lower()
        if save == 'y':
            filename = 'bkmea_detail_sample.html'
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Saved to {filename}")
            print("Open this file in a text editor to see exact HTML structure.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
