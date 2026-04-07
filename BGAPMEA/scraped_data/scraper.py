import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

BASE_URL = "https://www.bgapmea.org"

def extract_member_data(url):
    """Extract member details from a member detail page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        full_text = soup.get_text()

        # Initialize data dictionary
        data = {
            'Company Name': '',
            'Membership Number': '',
            'Member Status': '',
            'Contact Person': '',
            'Company Address': '',
            'Factory Address': '',
            'Phone': '',
            'Fax': '',
            'Email': '',
            'Website': '',
            'Products': '',
            'Detail URL': url
        }

        # Normalize text: replace multiple newlines/tabs/spaces with single newlines for line-based parsing
        lines = []
        for line in full_text.split('\n'):
            stripped = line.strip()
            if stripped:
                lines.append(stripped)
        # Also collapse multiple spaces within each line
        lines = [re.sub(r'\s+', ' ', line) for line in lines]

        # Remove footer lines (BGAPMEA address) from the end
        footer_start = None
        for i, line in enumerate(lines):
            if 'BGAPMEA,' in line or 'Developed By' in line:
                footer_start = i
                break
        if footer_start:
            lines = lines[:footer_start]

        # Mapping from label to dict key
        label_map = {
            'Company Address': 'Company Address',
            'Factory Address': 'Factory Address',
            'Phone': 'Phone',
            'Fax': 'Fax',
            'Email': 'Email',
            'Website': 'Website',
            'Products': 'Products'
        }

        # Now find the relevant lines
        # Strategy: Find positions of each field label, then extract the value on the same line
        field_indices = {}
        field_labels = list(label_map.keys())

        for i, line in enumerate(lines):
            for label in field_labels:
                if label in line and ':' in line:
                    # Ensure that the label appears at the start of a field (avoid matching in other text)
                    # Check if the line starts with the label or has the label followed by ':'
                    if re.match(rf'{re.escape(label)}\s*:', line) or line.startswith(label):
                        field_indices[label] = i
                        break

        # 1. Extract Membership Number and Company Name from the line containing "Membership:"
        membership_line_idx = None
        for i, line in enumerate(lines):
            if 'Membership:' in line:
                membership_line_idx = i
                membership_match = re.search(r'Membership:\s*(\d+)', line)
                if membership_match:
                    data['Membership Number'] = membership_match.group(1).strip()
                # Company name is everything before the "[Membership:" part
                if '[' in line:
                    company_part = line.split('[')[0].strip()
                    # Check that it's not some navigation text
                    if company_part and not any(kw in company_part for kw in ['Home', 'Member', 'Details']):
                        data['Company Name'] = company_part
                break

        # If company name not yet found, look at the line before the membership line
        if not data['Company Name'] and membership_line_idx is not None and membership_line_idx > 0:
            prev_line = lines[membership_line_idx - 1]
            if prev_line and not any(kw in prev_line for kw in ['Home', 'Member', 'Details', 'BGAPMEA']):
                data['Company Name'] = prev_line

        # 2. Extract Member Status (usually after membership line)
        if membership_line_idx is not None:
            # Search a few lines after membership for "Member Status"
            for i in range(membership_line_idx, min(membership_line_idx + 5, len(lines))):
                if 'Member Status' in lines[i]:
                    status_match = re.search(r'Member Status\s*:\s*(Active|Inactive)', lines[i])
                    if status_match:
                        data['Member Status'] = status_match.group(1).strip()
                    break

        # 3. Extract Contact Person
        # It appears between the membership/status section and the first address field
        # Determine a start position after the membership/status lines
        start_contact_search = membership_line_idx + 1 if membership_line_idx is not None else 0
        # Determine end position: first field label index
        first_field_labels = [label for label in ['Company Address', 'Factory Address'] if label in field_indices]
        if first_field_labels:
            first_field_idx = min(field_indices[label] for label in first_field_labels)
        else:
            first_field_idx = len(lines)

        contact_found = False
        for i in range(start_contact_search, first_field_idx):
            line = lines[i]
            # Skip lines that contain field labels or known noise
            if (line and not any(label in line for label in field_labels + ['Member Status']) and
                not line.lower().startswith('home') and not line.lower().startswith('member')):
                # Check if it looks like a person name: contains a comma and has letters/capitals
                if ',' in line and any(c.isalpha() for c in line):
                    data['Contact Person'] = line
                    contact_found = True
                    break

        # 4. Extract other fields using label positions
        for label, idx in field_indices.items():
            line = lines[idx]
            # Extract value after the label and colon
            if re.match(rf'{re.escape(label)}\s*:', line):
                value = line.split(':', 1)[1].strip()
            else:
                # Fallback: find label in line and take text after it
                parts = line.split(label, 1)
                if len(parts) > 1:
                    value = parts[1].strip()
                    if value.startswith(':'):
                        value = value[1:].strip()
                else:
                    value = ''
            data[label_map[label]] = value

        # Clean all fields
        for key in data:
            if isinstance(data[key], str):
                data[key] = re.sub(r'\s+', ' ', data[key]).strip()

        return data

    except Exception as e:
        print(f"Error extracting data from {url}: {e}")
        return None


def get_all_member_links():
    """Get all member detail page links by iterating through pagination"""
    all_links = []
    page_num = 1
    max_pages = 100  # Increased to capture all members (up to 1500)

    while page_num <= max_pages:
        if page_num == 1:
            url = f"{BASE_URL}/index.php/member"
        else:
            url = f"{BASE_URL}/index.php/member/index/{page_num * 15}"

        print(f"Fetching page {page_num}: {url}")
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            links_on_page = []
            for link in soup.find_all('a', href=lambda x: x and 'member_details' in x):
                full_url = link['href'] if link['href'].startswith('http') else f"{BASE_URL}{link['href']}"
                links_on_page.append(full_url)

            if not links_on_page:
                print(f"No member links found on page {page_num}. Stopping.")
                break

            all_links.extend(links_on_page)
            print(f"Found {len(links_on_page)} member links. Total so far: {len(all_links)}")

            # Check for next page
            next_link = soup.find('a', string=lambda x: x and 'Next' in x)
            if not next_link:
                print("No 'Next' link found. Reached last page.")
                break

            page_num += 1
            time.sleep(1)  # Be polite to the server

        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            break

    # Remove duplicates
    unique_links = list(set(all_links))
    print(f"\nTotal unique member detail links: {len(unique_links)}")
    return unique_links


def main():
    print("Starting BGAPMEA member scraper...\n")

    # Step 1: Get all member detail page URLs
    member_urls = get_all_member_links()

    # Step 2: Scrape data from each member page
    all_data = []
    total = len(member_urls)

    for i, url in enumerate(member_urls, 1):
        print(f"Scraping member {i}/{total}: {url}")
        data = extract_member_data(url)
        if data:
            all_data.append(data)
        else:
            print(f"  Failed to extract data from {url}")

        # Progress save every 10 members
        if i % 10 == 0:
            temp_df = pd.DataFrame(all_data)
            temp_df.to_csv('bgapmea_members_temp.csv', index=False, encoding='utf-8-sig')
            print(f"  Progress saved: {len(all_data)} members")

        time.sleep(1)  # Be polite

    # Step 3: Save to CSV
    if all_data:
        df = pd.DataFrame(all_data)
        output_file = 'bgapmea_members.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\n✓ Successfully saved {len(all_data)} members to {output_file}")
        print(f"\nColumns: {', '.join(df.columns.tolist())}")
        print(f"\nSample data:")
        print(df.head())
    else:
        print("No data was scraped.")


if __name__ == "__main__":
    main()
