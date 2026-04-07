#!/usr/bin/env python3
"""
Final BKOA Member Scraper - Optimized with exact structure knowledge

Data structure discovered:
- Listing page: https://bkoa-bd.com/member/
- Individual member: https://bkoa-bd.com/member/?id=<ID>
- Data displayed in <tr class="form-field"> tables
- Fields: Image, Company Name, Membership Number, Name, Email, Mobile No., Office/Factory Address, Registration Date
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

class BKOAFinalScraper:
    def __init__(self, base_url="https://bkoa-bd.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        self.members_data = []

    def fetch_page(self, url, timeout=15):
        """Fetch a webpage with error handling and retry logic"""
        for attempt in range(3):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()

                # Check if page has member data (look for form-field class)
                if 'form-field' not in response.text:
                    return None

                return response.text
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < 2:
                    time.sleep(2)
                else:
                    return None

    def extract_member_ids(self, listing_html):
        """Extract all member IDs from the listing page HTML"""
        soup = BeautifulSoup(listing_html, 'html.parser')
        member_ids = []

        # Find all links with member?id= pattern
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'member' in href and 'id=' in href:
                match = re.search(r'id=(\d+)', href)
                if match:
                    member_id = match.group(1)
                    if member_id not in member_ids:
                        member_ids.append(member_id)

        logger.info(f"Extracted {len(member_ids)} unique member IDs from listing page")
        return sorted(member_ids, key=int)

    def extract_member_data(self, html, member_id):
        """Extract member data from HTML using the exact structure"""
        soup = BeautifulSoup(html, 'html.parser')

        member_info = {
            'id': member_id,
            'company_name': '',
            'membership_number': '',
            'name': '',
            'email': '',
            'mobile': '',
            'address': '',
            'registration_date': '',
            'image_url': ''
        }

        # Find all form-field rows
        rows = soup.find_all('tr', class_='form-field')

        for row in rows:
            # Get the label (th) and value (td)
            th = row.find('th')
            td = row.find('td')

            if not th or not td:
                continue

            label = th.get_text(strip=True).lower()
            value = td.get_text(strip=True, separator=' ')

            # Map labels to fields
            if 'image' in label:
                img = td.find('img')
                if img and img.get('src'):
                    member_info['image_url'] = urljoin(self.base_url, img['src'])
            elif 'company name' in label:
                member_info['company_name'] = value
            elif 'membership number' in label:
                member_info['membership_number'] = value
            elif 'name' in label and 'company' not in label:
                member_info['name'] = value
            elif 'email' in label:
                member_info['email'] = value
            elif 'mobile' in label or 'phone' in label:
                member_info['mobile'] = value
            elif 'address' in label or 'office/factory address' in label:
                member_info['address'] = value
            elif 'registration date' in label or 'join' in label:
                member_info['registration_date'] = value

        # Clean up whitespace in all fields
        for key in member_info:
            if isinstance(member_info[key], str):
                member_info[key] = ' '.join(member_info[key].split())

        return member_info

    def scrape_member(self, member_id):
        """Scrape a single member by ID"""
        url = f"{self.base_url}/member/?id={member_id}"
        html = self.fetch_page(url)

        if html:
            data = self.extract_member_data(html, member_id)
            # Only include if we have at least a company name or member name
            if data['company_name'] or data['name']:
                logger.info(f"Scraped ID {member_id}: {data['company_name'] or data['name']}")
                return data
            else:
                logger.warning(f"ID {member_id}: No data found")
                return None
        else:
            logger.warning(f"ID {member_id}: Failed to fetch")
            return None

    def scrape_all_members(self, member_ids, max_workers=10):
        """Scrape all members using thread pool for speed"""
        logger.info(f"Starting to scrape {len(member_ids)} members...")
        logger.info(f"Using up to {max_workers} parallel workers")

        total_scraped = 0
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_id = {executor.submit(self.scrape_member, mid): mid for mid in member_ids}

            # Process completed tasks
            for future in as_completed(future_to_id):
                member_id = future_to_id[future]
                try:
                    result = future.result()
                    if result:
                        self.members_data.append(result)
                        total_scraped += 1
                except Exception as e:
                    logger.error(f"Error processing ID {member_id}: {e}")

                # Small delay to be polite (handled by ThreadPoolExecutor's work queue)

        logger.info(f"Scraping complete. Successfully scraped {total_scraped} members.")
        return total_scraped

    def save_to_csv(self, filename="bkoa_members_final.csv"):
        """Save data to CSV"""
        if not self.members_data:
            logger.error("No data to save!")
            return False

        fieldnames = ['id', 'company_name', 'membership_number', 'name', 'email', 'mobile', 'address', 'registration_date', 'image_url']

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.members_data)

            logger.info(f"CSV saved: {filename} ({len(self.members_data)} records)")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            return False

def main():
    """Main execution"""
    scraper = BKOAFinalScraper()

    # Step 1: Get the listing page
    logger.info("Fetching member listing page...")
    listing_url = "https://bkoa-bd.com/member/"
    listing_html = scraper.fetch_page(listing_url, timeout=30)

    if not listing_html:
        logger.error("Failed to fetch listing page. Exiting.")
        return

    # Step 2: Extract all member IDs
    member_ids = scraper.extract_member_ids(listing_html)

    if not member_ids:
        logger.error("No member IDs found. Exiting.")
        return

    # Save member IDs list
    with open('member_ids_list.txt', 'w') as f:
        f.write('\n'.join(member_ids))
    logger.info(f"Member ID list saved to member_ids_list.txt")

    # Step 3: Scrape all members (with optional test run)
    if len(member_ids) > 50:
        logger.info(f"Found {len(member_ids)} members. This may take a while.")
        response = input(f"Scrape all {len(member_ids)} members? (y/n): ").strip().lower()
        if response != 'y':
            logger.info("Scraping cancelled.")
            return

    # Scrape all (use concurrent requests but be respectful)
    total = scraper.scrape_all_members(member_ids, max_workers=8)
    scraper.save_to_csv()

    # Summary
    print("\n" + "="*60)
    print("SCRAPING COMPLETE")
    print("="*60)
    print(f"Total member IDs found: {len(member_ids)}")
    print(f"Members successfully scraped: {total}")
    print(f"CSV file: bkoa_members_final.csv")

    if scraper.members_data:
        print("\nSample data (first 3 entries):")
        for m in scraper.members_data[:3]:
            print(f"\nID: {m['id']}")
            print(f"Company: {m['company_name']}")
            print(f"Name: {m['name']}")
            print(f"Membership #: {m['membership_number']}")
            print(f"Mobile: {m['mobile']}")
            print(f"Email: {m['email']}")

if __name__ == "__main__":
    main()
