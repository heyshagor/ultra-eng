import requests
from bs4 import BeautifulSoup
import re

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print("=== FULL PAGE SOURCE ===")
print(soup.prettify())

# Also save to file for easier inspection
with open('sample_member_page.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print("\n\n=== SUMMARY OF ELEMENTS ===")
print(f"Title: {soup.title.get_text(strip=True) if soup.title else 'N/A'}")
print(f"Number of tables: {len(soup.find_all('table'))}")
print(f"Number of divs: {len(soup.find_all('div'))}")
print(f"Number of spans: {len(soup.find_all('span'))}")
print(f"Number of paragraphs: {len(soup.find_all('p'))}")

print("\n=== Looking for form/field labels ===")
# Find all elements that might contain labels
labels = soup.find_all(['b', 'strong', 'label'])
for label in labels[:20]:
    text = label.get_text(strip=True)
    if text and len(text) < 50:
        print(f"  - {text}")

print("\n=== Text lines that contain 'Address', 'Phone', 'Email' ===")
text = soup.get_text()
lines = [line.strip() for line in text.split('\n') if line.strip()]
for line in lines:
    if any(keyword in line for keyword in ['Address', 'Phone', 'Email', 'Website', 'Products']):
        print(f"  {line}")
