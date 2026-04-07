import requests
from bs4 import BeautifulSoup

url = "https://www.bgapmea.org/index.php/member/member_details/1561"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

response = requests.get(url, headers=headers, timeout=30)
print(f"Status code: {response.status_code}")
print(f"Content length: {len(response.content)}")

soup = BeautifulSoup(response.content, 'html.parser')

# Check for presence of key strings
content = response.text
print(f"\nChecking for key patterns in response:")
print(f"  Contains 'Membership:': {'Membership:' in content}")
print(f"  Contains 'Company Address': {'Company Address' in content}")
print(f"  Contains '<b>': {'<b>' in content.lower()}")

# Find all b tags
b_tags = soup.find_all('b')
print(f"\nFound {len(b_tags)} <b> tags")
for b in b_tags[:10]:
    print(f"  - {b.get_text(strip=True)}")

# Save the raw HTML to inspect
with open('member_page_with_ua.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())
print("\nSaved HTML to member_page_with_ua.html")
