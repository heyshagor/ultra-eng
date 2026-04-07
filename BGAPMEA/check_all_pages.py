import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.bgapmea.org"

def check_pagination_details():
    """Check how many pages and members exist"""
    page_num = 1
    max_pages = 50  # Check up to 50 pages

    while page_num <= max_pages:
        if page_num == 1:
            url = f"{BASE_URL}/index.php/member"
        else:
            url = f"{BASE_URL}/index.php/member/index/{page_num * 15}"

        print(f"\nPage {page_num}: {url}")
        try:
            response = requests.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Count member links on this page
            links = soup.find_all('a', href=lambda x: x and 'member_details' in x)
            print(f"  Member links found: {len(links)}")

            if len(links) < 15:
                print(f"  -> Less than 15 links, might be last page")
                break

            # Look for pagination elements
            pagination_text = soup.get_text()
            if 'Next' in pagination_text:
                print(f"  -> 'Next' link exists")
            else:
                print(f"  -> No 'Next' link found")
                break

            # Show first few links
            for i, link in enumerate(links[:3], 1):
                print(f"    {i}. {link.get_text(strip=True)[:50]}")

        except Exception as e:
            print(f"  Error: {e}")
            break

        page_num += 1

    print(f"\nTotal pages checked: {page_num}")

if __name__ == "__main__":
    check_pagination_details()
