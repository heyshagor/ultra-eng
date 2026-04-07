import requests
from bs4 import BeautifulSoup

url = "https://www.bgapmea.org/index.php/member/member_details/1561"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

print("Page title:", soup.title.get_text(strip=True))
print("\n=== Looking for data fields ===\n")

# Try to find a table or structured data
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

for i, table in enumerate(tables, 1):
    print(f"\n--- Table {i} ---")
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['td', 'th'])
        row_data = []
        for col in cols:
            label = col.find('b') or col.find('strong')
            if label:
                row_data.append(f"{label.get_text(strip=True)}: {col.get_text(strip=True)[:100]}")
            else:
                row_data.append(col.get_text(strip=True)[:100])
        if row_data:
            print(" | ".join(row_data))

# Look for definition lists
dls = soup.find_all('dl')
print(f"\n\nFound {len(dls)} definition lists")
for i, dl in enumerate(dls, 1):
    print(f"\n--- Definition List {i} ---")
    dts = dl.find_all('dt')
    dds = dl.find_all('dd')
    for dt, dd in zip(dts, dds):
        print(f"{dt.get_text(strip=True)}: {dd.get_text(strip=True)}")

# Look for divs with class containing 'detail', 'info', 'profile', etc.
print("\n\n=== Looking for divs with common detail classes ===")
for class_name in ['detail', 'info', 'profile', 'member', 'data']:
    divs = soup.find_all('div', class_=lambda x: x and class_name in x.lower())
    if divs:
        print(f"\nFound {len(divs)} divs with class containing '{class_name}'")
        for div in divs[:1]:
            print(div.get_text(strip=True)[:500])

# Print all text content to manually inspect
print("\n\n=== Full page text (first 3000 chars) ===")
text = soup.get_text(strip=True)
print(text[:3000])
