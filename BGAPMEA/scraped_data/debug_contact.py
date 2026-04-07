from scraper import extract_member_data
import requests
from bs4 import BeautifulSoup
import re

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=30)
full_text = response.text

lines = []
for line in full_text.split('\n'):
    stripped = line.strip()
    if stripped:
        lines.append(re.sub(r'\s+', ' ', stripped))

# Remove footer
footer_start = None
for i, line in enumerate(lines):
    if 'BGAPMEA,' in line or 'Developed By' in line:
        footer_start = i
        break
if footer_start:
    lines = lines[:footer_start]

print(f"Total lines after cleaning: {len(lines)}\n")
for i, line in enumerate(lines):
    print(f"{i:3d}: {line}")

# Find indices of interest
membership_idx = None
address_idx = None
for i, line in enumerate(lines):
    if 'Membership:' in line:
        membership_idx = i
        print(f"\nMembership line at index {i}: {line}")
    if 'Company Address' in line and ':' in line:
        address_idx = i
        print(f"Company Address line at index {i}: {line}")

print(f"\nSearching for contact person between {membership_idx+1 if membership_idx is not None else '?'} and {address_idx if address_idx is not None else '?'}")
