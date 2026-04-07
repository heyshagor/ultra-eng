#!/usr/bin/env python3
"""
Analyze BKOA website structure and scrape member data
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
from urllib.parse import urljoin
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BKOAWebsiteAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def fetch_page(self, url):
        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    def analyze_listing_page(self, html):
        """Analyze the structure of the member listing page"""
        soup = BeautifulSoup(html, 'html.parser')
        logger.info("=" * 60)
        logger.info("ANALYZING MEMBER LISTING PAGE")
        logger.info("=" * 60)

        # Find all links that contain 'member' and 'id='
        member_links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'member' in href and 'id=' in href:
                # Extract ID
                match = re.search(r'id=(\d+)', href)
                if match:
                    member_id = match.group(1)
                    if member_id not in [m['id'] for m in member_links]:
                        member_links.append({
                            'id': member_id,
                            'url': href if href.startswith('http') else urljoin('https://bkoa-bd.com', href),
                            'text': link.get_text(strip=True)[:50]
                        })

        logger.info(f"Found {len(member_links)} member links on listing page")
        for i, link in enumerate(member_links[:10], 1):
            logger.info(f"  {i}. ID: {link['id']}, URL: {link['url']}, Text: {link['text']}")

        if len(member_links) > 10:
            logger.info(f"  ... and {len(member_links) - 10} more")

        return member_links

    def analyze_member_page(self, html, member_id):
        """Analyze the structure of an individual member page"""
        soup = BeautifulSoup(html, 'html.parser')
        logger.info("=" * 60)
        logger.info(f"ANALYZING MEMBER PAGE - ID: {member_id}")
        logger.info("=" * 60)

        # Find the main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=re.compile(r'content|main|member'))

        if main_content:
            logger.info("Main content area found")

            # Look for tables
            tables = main_content.find_all('table')
            logger.info(f"Found {len(tables)} table(s)")

            for i, table in enumerate(tables, 1):
                logger.info(f"\nTable {i}:")
                rows = table.find_all('tr')
                for row in rows[:5]:  # Show first 5 rows
                    cols = row.find_all(['td', 'th'])
                    row_text = ' | '.join([col.get_text(strip=True) for col in cols])
                    logger.info(f"  {row_text}")

            # Look for definition lists
            dls = main_content.find_all('dl')
            logger.info(f"Found {len(dls)} definition list(s)")

            # Look for divs with labels and values
            forms = main_content.find_all(['div', 'p'], class_=re.compile(r'form-field|field|label|value'))
            logger.info(f"Found {len(forms)} potential form field areas")

            # Extract all text content
            all_text = main_content.get_text(separator='\n', strip=True)
            logger.info("\nAll text content (first 500 chars):")
            logger.info(all_text[:500] + "...")

            # Look for common data patterns
            patterns = {
                'emails': re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', all_text),
                'phones': re.findall(r'(\+?88?[\d\s\-\(\)]{10,})', all_text),
                'addresses': re.findall(r'(?:Address|Location)[:\s]*([^\n]+)', all_text, re.IGNORECASE)
            }

            for key, values in patterns.items():
                if values:
                    logger.info(f"\nFound {key}: {values[0] if len(values) == 1 else values}")

            # Look for images
            images = main_content.find_all('img')
            logger.info(f"\nFound {len(images)} image(s):")
            for img in images[:3]:
                src = img.get('src', '')
                alt = img.get('alt', '')
                logger.info(f"  - {src} (alt: {alt})")

            # Check for specific data fields
            logger.info("\nSearching for specific data fields:")

            field_selectors = {
                'Name': ['h1', 'h2', '.name', '.member-name', '.title'],
                'Company': ['.company', '.company-name', '.organization'],
                'Email': ['.email', '.e-mail'],
                'Phone': ['.phone', '.mobile', '.contact'],
                'Address': ['.address', '.location'],
                'Membership': ['.membership', '.member-no', '.id']
            }

            for field, selectors in field_selectors.items():
                for selector in selectors:
                    try:
                        elements = main_content.select(selector)
                        if elements:
                            logger.info(f"  {field} found with selector '{selector}': {elements[0].get_text(strip=True)[:100]}")
                            break
                    except:
                        continue

        else:
            logger.warning("No main content area found")

    def create_robust_scraper(self, member_links):
        """Create a final robust scraper based on analysis"""
        logger.info("=" * 60)
        logger.info("CREATING ROBUST SCRAPER BASED ON ANALYSIS")
        logger.info("=" * 60)

        # Fetch first few members to understand consistent patterns
        sample_members = []
        for link in member_links[:3]:
            html = self.fetch_page(link['url'])
            if html:
                sample_members.append({
                    'id': link['id'],
                    'html': html
                })
            time.sleep(1)

        # Analyze samples to determine extraction strategy
        if sample_members:
            self.determine_extraction_strategy(sample_members)

        return sample_members

    def determine_extraction_strategy(self, sample_members):
        """Determine the best extraction strategy based on sample pages"""
        logger.info("\nDetermining extraction strategy from samples...")

        # Common patterns to check
        strategies = {
            'table_based': False,
            'div_form_fields': False,
            'definition_list': False,
            'direct_text': False
        }

        for sample in sample_members:
            soup = BeautifulSoup(sample['html'], 'html.parser')
            main = soup.find('main') or soup.find('article') or soup

            # Check for tables
            if main.find_all('table'):
                strategies['table_based'] = True
                logger.info(f"Member {sample['id']}: Table structure detected")

            # Check for form fields with labels
            form_fields = main.find_all(['label', 'th'])
            if form_fields:
                strategies['div_form_fields'] = True
                logger.info(f"Member {sample['id']}: Form field structure detected")

            # Check for definition lists
            if main.find_all('dl'):
                strategies['definition_list'] = True
                logger.info(f"Member {sample['id']}: Definition list structure detected")

        logger.info(f"\nDetected strategies: {[k for k, v in strategies.items() if v]}")

    def run_analysis(self):
        """Main analysis function"""
        logger.info("Starting BKOA Website Analysis...")

        # 1. Analyze listing page
        listing_url = "https://bkoa-bd.com/member/"
        listing_html = self.fetch_page(listing_url)

        if not listing_html:
            logger.error("Failed to fetch listing page")
            return

        # 2. Extract all member links
        member_links = self.analyze_listing_page(listing_html)

        if not member_links:
            logger.warning("No member links found in listing page directly.")
            logger.info("The website might use JavaScript to load members or have a different structure.")
            logger.info("Attempting to discover members by checking common ID patterns...")

            # Try sequential IDs
            member_links = []
            for i in range(1, 700):
                test_url = f"https://bkoa-bd.com/member/?id={i}"
                html = self.fetch_page(test_url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    # Check if this page has member data (not 404 or redirect)
                    title = soup.find('title')
                    if title and 'member' in title.get_text().lower():
                        member_links.append({
                            'id': str(i),
                            'url': test_url,
                            'text': ''
                        })
                        logger.info(f"Found valid member page for ID: {i}")
                time.sleep(0.5)

            logger.info(f"Sequential search found {len(member_links)} member pages")

        # 3. Analyze sample member pages
        if member_links:
            self.create_robust_scraper(member_links)

        logger.info("\nAnalysis complete!")
        logger.info(f"Total members found: {len(member_links)}")

        return member_links

def main():
    analyzer = BKOAWebsiteAnalyzer()
    members = analyzer.run_analysis()

    if members:
        print("\n" + "="*60)
        print("ANALYSIS RESULTS")
        print("="*60)
        print(f"Total members found: {len(members)}")
        print("\nFirst 10 members:")
        for m in members[:10]:
            print(f"  ID: {m['id']} - URL: {m['url']}")

        # Save member list
        with open('member_links.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'url'])
            writer.writeheader()
            writer.writerows([{'id': m['id'], 'url': m['url']} for m in members])
        print(f"\nMember list saved to member_links.csv")

if __name__ == "__main__":
    main()
