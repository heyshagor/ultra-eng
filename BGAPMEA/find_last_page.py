import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.bgapmea.org"

def check_page(offset):
    url = f"{BASE_URL}/index.php/member/index/{offset}"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a', href=lambda x: x and 'member_details' in x)
        return len(links)
    except:
        return 0

# Binary search for last page with members
low, high = 1200, 1250
last_with_members = 1200

while low <= high:
    mid = (low + high) // 2
    count = check_page(mid)
    print(f"Offset {mid}: {count} links")
    if count > 0:
        last_with_members = mid
        low = mid + 1
    else:
        high = mid - 1

print(f"\nLast offset with members: {last_with_members}")
print(f"Estimated total members: ~{last_with_members + 15}")
