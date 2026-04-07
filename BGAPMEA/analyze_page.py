import requests
from bs4 import BeautifulSoup

url = "https://www.bgapmea.org/index.php/member"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Find all member detail links
member_links = []
for link in soup.find_all('a', href=True):
    if 'member_details' in link['href']:
        full_url = link['href'] if link['href'].startswith('http') else f"https://www.bgapmea.org{link['href']}"
        member_links.append({
            'text': link.get_text(strip=True),
            'url': full_url
        })

print(f"Found {len(member_links)} member detail links")
for i, link in enumerate(member_links[:10], 1):
    print(f"{i}. {link['text']} - {link['url']}")
