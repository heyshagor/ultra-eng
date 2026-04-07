import requests
from bs4 import BeautifulSoup
import re

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')
full_text = soup.get_text()

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

# Show lines around the membership/address
for i, line in enumerate(lines):
    if i >= 50 and i <= 80:
        print(f"{i:3d}: {line}")

# Find indices
membership_idx = None
address_idx = None
field_labels = ['Company Address', 'Factory Address', 'Phone', 'Fax', 'Email', 'Website', 'Products']

for i, line in enumerate(lines):
    if 'Membership:' in line:
        membership_idx = i
    if 'Company Address' in line and ':' in line:
        address_idx = i

print(f"\nMembership at {membership_idx}, Company Address at {address_idx}")

if membership_idx is not None and address_idx is not None:
    print(f"\nLines between membership+1 ({membership_idx+1}) and address ({address_idx-1}):")
    for i in range(membership_idx+1, address_idx):
        line = lines[i]
        print(f"{i:3d}: {line}")
        # Check if line matches contact criteria
        is_label = any(label in line for label in field_labels + ['Member Status'])
        is_noise = line.lower().startswith('home') or line.lower().startswith('member')
        if line and not is_label and not is_noise:
            print(f"   ^ Candidate for contact (matches criteria)")
            if re.search(r'[A-Za-z]\.\s*[A-Za-z]+,', line) or re.search(r'^[A-Za-z]+,\s*[A-Za-z]', line) or re.search(r'[A-Za-z]+,.*[A-Za-z]\.', line):
                print(f"   ^^^ MATCH! Name pattern found")
            else:
                print(f"   No name pattern match")
        else:
            print(f"   Excluded: is_label={is_label}, is_noise={is_noise}")
