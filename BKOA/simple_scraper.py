#!/usr/bin/env python3
"""
Simple BKOA Member Scraper - No prompts, just works
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.data = []

    def get_member_ids(self):
        logger.info("Fetching member listing page...")
        try:
            r = self.session.get("https://bkoa-bd.com/member/", timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            ids = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if 'member' in href and 'id=' in href:
                    import re
                    m = re.search(r'id=(\d+)', href)
                    if m:
                        id_val = m.group(1)
                        if id_val not in ids:
                            ids.append(id_val)

            ids = sorted(ids, key=int)
            logger.info(f"Found {len(ids)} member IDs")
            return ids
        except Exception as e:
            logger.error(f"Failed to get member IDs: {e}")
            return []

    def scrape_member(self, member_id):
        url = f"https://bkoa-bd.com/member/?id={member_id}"
        try:
            r = self.session.get(url, timeout=15)
            if r.status_code != 200:
                return None

            if 'form-field' not in r.text:
                return None

            soup = BeautifulSoup(r.text, 'html.parser')
            member = {
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

            for row in soup.find_all('tr', class_='form-field'):
                th = row.find('th')
                td = row.find('td')
                if not th or not td:
                    continue

                label = th.get_text(strip=True).lower()
                value = td.get_text(strip=True, separator=' ')

                if 'image' in label:
                    img = td.find('img')
                    if img and img.get('src'):
                        member['image_url'] = img['src']
                elif 'company name' in label:
                    member['company_name'] = value
                elif 'membership number' in label:
                    member['membership_number'] = value
                elif 'name' in label and 'company' not in label:
                    member['name'] = value
                elif 'email' in label:
                    member['email'] = value
                elif 'mobile' in label or 'phone' in label:
                    member['mobile'] = value
                elif 'address' in label or 'office/factory address' in label:
                    member['address'] = value
                elif 'registration date' in label or 'join' in label:
                    member['registration_date'] = value

            # Check if we have meaningful data
            if member['company_name'] or member['name']:
                return member
            return None
        except Exception as e:
            logger.debug(f"Error scraping {member_id}: {e}")
            return None

    def run(self):
        ids = self.get_member_ids()
        if not ids:
            logger.error("No IDs found. Exiting.")
            return

        logger.info(f"Scraping {len(ids)} members...")
        results = []

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(self.scrape_member, iid): iid for iid in ids}
            for future in as_completed(futures):
                res = future.result()
                if res:
                    results.append(res)

        logger.info(f"Successfully scraped {len(results)} members")

        if results:
            fields = ['id', 'company_name', 'membership_number', 'name', 'email', 'mobile', 'address', 'registration_date', 'image_url']
            with open('bkoa_members.csv', 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(results)

            logger.info("Saved to bkoa_members.csv")

            print("\nFirst 3 results:")
            for r in results[:3]:
                print(f"\nID: {r['id']}")
                print(f"Company: {r['company_name']}")
                print(f"Name: {r['name']}")
                print(f"Mobile: {r['mobile']}")

if __name__ == '__main__':
    scraper = SimpleScraper()
    scraper.run()
