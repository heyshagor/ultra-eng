import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.bgapmea.org"

def check_specific_page(page_num):
    if page_num == 1:
        url = f"{BASE_URL}/index.php/member"
    else:
        url = f"{BASE_URL}/index.php/member/index/{page_num * 15}"
    print(f"Page {page_num} (offset {page_num*15}): {url}")
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=lambda x: x and 'member_details' in x)
        print(f"  Links found: {len(links)}")
        if links:
            print(f"  First: {links[0].get_text(strip=True)}")
            print(f"  Last: {links[-1].get_text(strip=True)}")
        return len(links)
    except Exception as e:
        print(f"  Error: {e}")
        return 0

# Check further pages
for p in [60, 80, 83]:
    count = check_specific_page(p)
    if count == 0:
        print(f"  -> No members on page {p}, probably past the end")
        break

# Also check the very last page by looking at page 83 which should be around 1245 members
# 1245 / 15 = 83 pages
