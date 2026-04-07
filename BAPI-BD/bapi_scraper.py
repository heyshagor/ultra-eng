import requests
import csv
from bs4 import BeautifulSoup
import warnings
import sys

warnings.filterwarnings('ignore', message='Unverified HTTPS request')

def inspect_page(url):
    """Inspect the page structure first"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.content, 'html.parser')

    print("ANALYZING PAGE STRUCTURE...\n")

    # Check for tables
    tables = soup.find_all('table')
    print(f"Found {len(tables)} tables")
    for i, t in enumerate(tables[:3], 1):
        rows = t.find_all('tr')[:2]
        print(f"\nTable {i}:")
        for r in rows:
            cols = r.find_all(['td', 'th'])
            texts = [c.get_text(strip=True)[:30] for c in cols]
            print(f"  {texts}")

    # Check for member-like divs
    print("\nSearching for member containers...")
    all_divs = soup.find_all('div')
    potential = [d for d in all_divs if d.get_text(strip=True) and len(d.find_all()) >= 3]

    if potential:
        print(f"Found {len(potential)} potential member containers")
        print("Sample container:")
        sample = potential[0].get_text(separator=' | ', strip=True)[:200]
        print(f"  {sample}")

    # Save HTML
    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print("\nFull HTML saved to 'page.html'")

    return soup

def scrape_to_csv(url, output_file='members.csv'):
    """Scrape data and save to CSV"""
    print("\n" + "="*60)
    print("STARTING SCRAPE")
    print("="*60)

    soup = inspect_page(url)

    print("\n" + "="*60)
    print("EXTRACTING DATA")
    print("="*60)

    # Try different extraction methods
    data = []

    # Method 1: Table-based
    tables = soup.find_all('table')
    if tables:
        print("Using table extraction...")
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if cols:
                    row_data = [col.get_text(strip=True) for col in cols]
                    if len(row_data) >= 2:  # At least 2 columns
                        data.append(row_data)

    # Method 2: Card-based
    if not data:
        print("Using card-based extraction...")
        cards = soup.find_all(['div'], class_=lambda x: x and any(kw in str(x).lower() for kw in ['card', 'member', 'profile', 'item']))
        if not cards:
            # Fallback: divs with multiple lines
            cards = [d for d in soup.find_all('div') if d.get_text(strip=True) and '\n' in d.get_text()]

        for card in cards:
            lines = [line.strip() for line in card.get_text().split('\n') if line.strip()]
            if len(lines) >= 2:
                data.append(lines)

    if data:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)

        print(f"\n✓ Extracted {len(data)} records")
        print(f"✓ Saved to: {output_file}")
        print(f"\nFirst 3 rows:")
        for row in data[:3]:
            print(f"  {row[:4]}" + ("..." if len(row) > 4 else ""))
    else:
        print("\n✗ No data extracted.")
        print("Please open 'page.html' in a browser and inspect the structure.")
        print("You may need to adjust the selectors in this script.")

if __name__ == "__main__":
    url = "http://www.bapi-bd.com/members-directory.html"
    scrape_to_csv(url)
