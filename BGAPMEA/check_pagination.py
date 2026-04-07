import requests
from bs4 import BeautifulSoup

url = "https://www.bgapmea.org/index.php/member"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print("Checking for pagination...")
# Look for pagination links
pagination = soup.find_all('a', string=lambda x: x and ('Next' in x or 'Page' in x or (any(c.isdigit() for c in x.strip()) if x else False)))
print(f"Found {len(pagination)} potential pagination elements:")
for p in pagination:
    print(f"  - {p.get_text(strip=True)}: {p.get('href', '')}")

# Count total member links on page
member_links = soup.find_all('a', href=lambda x: x and 'member_details' in x)
print(f"\nTotal member links on this page: {len(member_links)}")
