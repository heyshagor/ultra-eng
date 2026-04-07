import requests
from bs4 import BeautifulSoup
import re

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

print("=== Looking for the member table ===")

# Find the main table with member details
member_table = None
for table in soup.find_all('table'):
    print(f"\nChecking a table with {len(table.find_all('b'))} bold elements")
    if table.find('b', string=lambda x: x and 'Company Address' in str(x)):
        print("  -> Found bold with 'Company Address'!")
        member_table = table
        break
    if len(table.find_all('b')) >= 3:
        print("  -> Has 3+ bold elements, could be candidate")
        if not member_table:
            member_table = table  # use last candidate

if member_table:
    print(f"\nUsing a table with {len(member_table.find_all('b'))} bold tags")
    bolds = member_table.find_all('b')
    print("Bold labels found:")
    for b in bolds:
        print(f"  - '{b.get_text(strip=True)}'")

    first_bold = bolds[0] if bolds else None
    if first_bold:
        # Get all previous content
        print("\nPrevious content before first bold:")
        prev = first_bold.previous_sibling
        while prev:
            if isinstance(prev, str):
                print(f"  Text: '{prev.strip()}'")
            elif prev.name:
                print(f"  Element <{prev.name}>: {prev.get_text(strip=True)[:100]}")
            prev = prev.previous_sibling
else:
    print("No member table found!")
