import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_bfllfea_members():
    """
    Scrape member data from https://bfllfea.com/general-member-list
    Extracts: company name, name, member no, contact, product
    """
    url = "https://bfllfea.com/general-member-list"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        members = []

        # NOTE: You need to inspect the actual HTML structure and update these selectors
        # Common patterns to look for:
        # - Table rows: member_elements = soup.select('table tr')
        # - Card elements: member_elements = soup.select('.member-card')
        # - List items: member_elements = soup.select('.member-list li')

        # Example if data is in a table:
        # rows = soup.select('table tr')
        # for row in rows[1:]:  # Skip header
        #     cols = row.select('td')
        #     if len(cols) >= 5:
        #         member = {
        #             'company_name': cols[0].get_text(strip=True),
        #             'name': cols[1].get_text(strip=True),
        #             'member_no': cols[2].get_text(strip=True),
        #             'contact': cols[3].get_text(strip=True),
        #             'product': cols[4].get_text(strip=True)
        #         }
        #         members.append(member)

        # TEMPORARY: Print the page structure to help identify selectors
        print("\n=== PAGE STRUCTURE ANALYSIS ===")
        print("Title:", soup.title.string if soup.title else "No title")

        # Look for common member container patterns
        possible_selectors = [
            'table', '.table', 'table tr',
            '.member', '.member-card', '.card',
            '.list', '.list-item',
            'tbody tr', 'thead'
        ]

        for selector in possible_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"\nFound {len(elements)} elements with selector '{selector}'")
                if selector.endswith('tr') or 'tr' in selector:
                    first = elements[0]
                    print(f"First {selector} HTML:\n{first[:500] if len(str(first)) > 500 else first}")

        # Check for specific IDs or classes
        print("\n=== ALL CLASSES FOUND ===")
        all_classes = set()
        for tag in soup.find_all(class_=True):
            all_classes.update(tag['class'])
        print(sorted(all_classes)[:20])

        print("\n=== ALL IDs FOUND ===")
        all_ids = [tag.get('id') for tag in soup.find_all(id=True)]
        print(sorted(set(all_ids))[:20])

        # YOU MUST UPDATE THIS SECTION BASED ON ACTUAL HTML STRUCTURE
        """
        PSEUDOCODE for extraction:

        member_elements = soup.select('PUT_CORRECT_SELECTOR_HERE')

        for element in member_elements:
            member = {
                'company_name': extract_text(element, 'CSS_SELECTOR_FOR_COMPANY'),
                'name': extract_text(element, 'CSS_SELECTOR_FOR_NAME'),
                'member_no': extract_text(element, 'CSS_SELECTOR_FOR_MEMBER_NO'),
                'contact': extract_text(element, 'CSS_SELECTOR_FOR_CONTACT'),
                'product': extract_text(element, 'CSS_SELECTOR_FOR_PRODUCT')
            }
            members.append(member)
        """

        # Save to CSV
        if members:
            filename = 'bfllfea_members.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['company_name', 'name', 'member_no', 'contact', 'product']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(members)

            print(f"\n✅ Successfully saved {len(members)} members to {filename}")
        else:
            print("\n❌ No members extracted. Please update the selectors in the script.")

    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    scrape_bfllfea_members()
