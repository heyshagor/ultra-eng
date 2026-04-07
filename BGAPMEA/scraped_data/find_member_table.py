import requests
from bs4 import BeautifulSoup
import re

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find the main content table that contains member details
# Looking for a table that has the member name
tables = soup.find_all('table')

for i, table in enumerate(tables):
    text = table.get_text()
    if 'Membership' in text or 'Member Status' in text or 'Company Address' in text:
        print(f"\n=== TABLE {i} (likely member data) ===")
        print(text[:2000])  # Print first 2000 chars

        # Try to extract data more precisely
        # Look for bold elements like <b>Company Address :</b>
        bold_labels = table.find_all(['b', 'strong'])
        print(f"\nFound {len(bold_labels)} bold labels:")
        for label in bold_labels[:]:
            label_text = label.get_text(strip=True)
            print(f"  - {label_text}")
            # Show the next sibling or parent content
            # The structure seems to be: <b>Label:</b> Value or <b>Label:</b><br/>Value
            if label.next_sibling:
                sibling = label.next_sibling
                if isinstance(sibling, str):
                    print(f"      Next sibling: {sibling.strip()[:100]}")
                elif sibling:
                    print(f"      Next element: {sibling.get_text(strip=True)[:100]}")
