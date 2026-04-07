#!/usr/bin/env python3
"""
Member Data Scraper for BKOA BD Website
Scrapes member information from https://bkoa-bd.com/member/ and individual member pages
Saves data to CSV format
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin, urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MemberScraper:
    def __init__(self, base_url="https://bkoa-bd.com/member/"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.members_data = []

    def fetch_page(self, url):
        """Fetch a webpage with error handling"""
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_member_ids_from_listing(self, soup):
        """Extract member IDs from the listing page"""
        member_ids = []

        # Look for links that match the pattern /member/?id=NUMBER
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'member' in href and 'id=' in href:
                # Extract ID from URL
                match = re.search(r'id=(\d+)', href)
                if match:
                    member_id = match.group(1)
                    if member_id not in member_ids:
                        member_ids.append(member_id)

        logger.info(f"Found {len(member_ids)} member IDs on the page")
        return member_ids

    def extract_member_details(self, soup, member_id):
        """Extract detailed information from a member's page"""
        member_info = {
            'id': member_id,
            'name': '',
            'picture': '',
            'address': '',
            'phone': '',
            'email': '',
            'member_type': '',
            'join_date': '',
            'company': '',
            'additional_info': ''
        }

        try:
            # Extract name - likely in a heading or specific element
            # Common patterns: h1, h2, or elements with class containing 'name', 'title', etc.
            name_selectors = [
                'h1', 'h2',
                '[class*="name"]',
                '[class*="title"]',
                '[class*="member-name"]'
            ]

            for selector in name_selectors:
                element = soup.select_one(selector)
                if element and element.get_text(strip=True):
                    member_info['name'] = element.get_text(strip=True)
                    break

            # Extract picture URL
            img = soup.find('img')
            if img and img.get('src'):
                member_info['picture'] = urljoin(self.base_url, img['src'])

            # Extract all text content and look for patterns
            all_text = soup.get_text(separator='\n', strip=True)

            # Extract email
            email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
            emails = re.findall(email_pattern, all_text)
            if emails:
                member_info['email'] = emails[0]

            # Extract phone numbers
            phone_pattern = r'(\+?88?[\d\s\-\(\)]{10,})'
            phones = re.findall(phone_pattern, all_text)
            if phones:
                member_info['phone'] = phones[0]

            # Extract address - look for address-related keywords
            address_keywords = ['address', 'location', 'area', 'road', 'street', 'city', 'dhaka']
            for keyword in address_keywords:
                if keyword.lower() in all_text.lower():
                    # Try to find the context around the keyword
                    lines = all_text.split('\n')
                    for line in lines:
                        if keyword.lower() in line.lower():
                            member_info['address'] = line.strip()
                            break
                    if member_info['address']:
                        break

            # Extract any structured data from tables or lists
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        label = cells[0].get_text(strip=True).lower()
                        value = cells[1].get_text(strip=True)

                        if any(word in label for word in ['name', 'member']):
                            member_info['name'] = value
                        elif 'email' in label or 'e-mail' in label:
                            member_info['email'] = value
                        elif 'phone' in label or 'mobile' in label or 'contact' in label:
                            member_info['phone'] = value
                        elif 'address' in label:
                            member_info['address'] = value
                        elif 'date' in label or 'join' in label:
                            member_info['join_date'] = value
                        elif 'company' in label or 'organization' in label:
                            member_info['company'] = value

            # Look for definition lists
            dls = soup.find_all('dl')
            for dl in dls:
                dts = dl.find_all('dt')
                dds = dl.find_all('dd')
                for dt, dd in zip(dts, dds):
                    label = dt.get_text(strip=True).lower()
                    value = dd.get_text(strip=True)

                    if 'name' in label:
                        member_info['name'] = value
                    elif 'email' in label:
                        member_info['email'] = value
                    elif 'phone' in label or 'mobile' in label:
                        member_info['phone'] = value
                    elif 'address' in label:
                        member_info['address'] = value

            logger.info(f"Extracted data for member {member_id}: {member_info['name']}")

        except Exception as e:
            logger.error(f"Error extracting details for member {member_id}: {e}")

        return member_info

    def scrape_all_members(self, start_id=1, max_members=700):
        """Main method to scrape all members"""
        logger.info("Starting member scraping process...")

        # First, get the listing page to discover member IDs
        logger.info("Fetching main listing page...")
        listing_soup = self.fetch_page(self.base_url)

        if not listing_soup:
            logger.error("Could not fetch the main listing page")
            return False

        # Extract all member IDs from the listing
        member_ids = self.extract_member_ids_from_listing(listing_soup)

        # If no IDs found from listing, try sequential approach (1 to 693)
        if not member_ids:
            logger.info("No member IDs found in listing, trying sequential approach...")
            member_ids = [str(i) for i in range(start_id, start_id + max_members)]

        logger.info(f"Total member IDs to scrape: {len(member_ids)}")

        # Scrape each member
        for i, member_id in enumerate(member_ids, 1):
            logger.info(f"Scraping member {i}/{len(member_ids)} (ID: {member_id})")

            member_url = f"{self.base_url}?id={member_id}"
            member_soup = self.fetch_page(member_url)

            if member_soup:
                member_info = self.extract_member_details(member_soup, member_id)
                self.members_data.append(member_info)
            else:
                logger.warning(f"Failed to fetch member {member_id}")

            # Be polite - delay between requests
            time.sleep(1)

        logger.info(f"Completed scraping. Total members collected: {len(self.members_data)}")
        return True

    def save_to_csv(self, filename="members_data.csv"):
        """Save collected member data to CSV"""
        if not self.members_data:
            logger.error("No data to save!")
            return False

        # Define CSV columns
        fieldnames = ['id', 'name', 'picture', 'address', 'phone', 'email', 'member_type', 'join_date', 'company', 'additional_info']

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.members_data)

            logger.info(f"Data saved to {filename} ({len(self.members_data)} records)")
            return True
        except Exception as e:
            logger.error(f"Error saving CSV: {e}")
            return False

def main():
    """Main execution"""
    scraper = MemberScraper()

    # Scrape all members (approximately 693 members)
    success = scraper.scrape_all_members(start_id=1, max_members=700)

    if success:
        # Save to CSV
        scraper.save_to_csv("bkoa_members.csv")

        # Print summary
        print("\n" + "="*50)
        print("SCRAPING COMPLETE")
        print("="*50)
        print(f"Total members scraped: {len(scraper.members_data)}")
        print(f"CSV file saved as: bkoa_members.csv")

        # Show sample of data
        if scraper.members_data:
            print("\nSample data (first 3 members):")
            for member in scraper.members_data[:3]:
                print(f"\nID: {member['id']}")
                print(f"Name: {member['name']}")
                print(f"Email: {member['email']}")
                print(f"Phone: {member['phone']}")
                print(f"Address: {member['address'][:100] if member['address'] else 'N/A'}")
    else:
        print("\nScraping failed. Check the logs for errors.")

if __name__ == "__main__":
    main()
