#!/usr/bin/env python3
"""
BLCFEA Member Data Scraper
Scrapes member information from https://blcfea.com/member.php and exports to CSV
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import sys

def scrape_members():
    """Scrape all member data from the member page"""

    url = "https://blcfea.com/member.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    print(f"Fetching members from {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        sys.exit(1)

    print(f"Page fetched successfully. Status: {response.status_code}")
    soup = BeautifulSoup(response.content, 'html.parser')

    members_data = []

    # Find all member links that have data-toggle="modal"
    member_links = soup.find_all('a', {'data-toggle': 'modal'})

    print(f"Found {len(member_links)} member entries")

    for link in member_links:
        member_number = ""
        company_name = ""
        name = ""
        designation = ""
        address = ""
        mobile = ""
        email = ""

        # Extract member number and company name from the link text
        link_text = link.get_text(strip=True)
        if link_text:
            # Split by first dot to separate number and company
            if '.' in link_text:
                parts = link_text.split('.', 1)
                member_number = parts[0].strip()
                company_name = parts[1].strip() if len(parts) > 1 else ""
            else:
                company_name = link_text

        # Get the modal id from data-target
        modal_id = link.get('data-target', '').lstrip('#')
        if not modal_id:
            continue

        # Find the corresponding modal div
        modal = soup.find('div', {'id': modal_id})
        if not modal:
            continue

        # Extract data from the table inside the modal
        table = modal.find('table')
        if table:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True).lower()
                    value = cells[1].get_text(strip=True)

                    if 'company' in label:
                        company_name = value if not company_name else company_name
                    elif 'name' in label:
                        name = value
                    elif 'desigantion' in label or 'designation' in label:  # Note: typo in original HTML
                        designation = value
                    elif 'address' in label:
                        address = value
                    elif 'mobile' in label or 'phone' in label:
                        mobile = value
                    elif 'email' in label:
                        email = value

        member_data = {
            'Member Number': member_number,
            'Company': company_name,
            'Contact Name': name,
            'Designation': designation,
            'Address': address,
            'Mobile': mobile,
            'Email': email
        }
        members_data.append(member_data)

    return members_data

def save_to_csv(members_data, filename='blcfea_members.csv'):
    """Save member data to CSV file"""

    if not members_data:
        print("No member data to save")
        return

    fieldnames = ['Member Number', 'Company', 'Contact Name', 'Designation', 'Address', 'Mobile', 'Email']

    try:
        with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(members_data)

        print(f"\nSuccessfully exported {len(members_data)} members to {filename}")
        print(f"\nSample of exported data:")
        print("-" * 80)
        for i, member in enumerate(members_data[:5], 1):
            print(f"{i}. {member.get('Company', 'N/A')} - {member.get('Contact Name', 'N/A')}")
            print(f"   Email: {member.get('Email', 'N/A')}")
            print(f"   Mobile: {member.get('Mobile', 'N/A')}")
            print()

        if len(members_data) > 5:
            print(f"... and {len(members_data) - 5} more members")

    except IOError as e:
        print(f"Error saving CSV file: {e}")
        sys.exit(1)

def main():
    print("=" * 80)
    print("BLCFEA Member Data Scraper")
    print("=" * 80)

    members = scrape_members()

    if not members:
        print("No member data found!")
        sys.exit(1)

    print(f"\nTotal members scraped: {len(members)}")

    # Save to CSV
    save_to_csv(members)

    print("\nDone!")

if __name__ == "__main__":
    main()
