import requests
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.bgapmea.org"

def get_member_links_from_page(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []

    for link in soup.find_all('a', href=lambda x: x and 'member_details' in x):
        full_url = link['href'] if link['href'].startswith('http') else f"{BASE_URL}{link['href']}"
        links.append({
            'text': link.get_text(strip=True),
            'url': full_url
        })

    return links

def get_all_member_links():
    all_links = []
    page_num = 1
    max_pages = 20  # Safety limit

    while page_num <= max_pages:
        if page_num == 1:
            url = f"{BASE_URL}/index.php/member"
        else:
            url = f"{BASE_URL}/index.php/member/index/{page_num * 15}"  # 15 items per page

        print(f"Fetching page {page_num}: {url}")
        links = get_member_links_from_page(url)

        if not links:
            print(f"No links found on page {page_num}. Stopping.")
            break

        all_links.extend(links)
        print(f"Found {len(links)} member links. Total so far: {len(all_links)}")

        # Check if there's a next page
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        next_link = soup.find('a', string=lambda x: x and 'Next' in x)

        if not next_link:
            print("No 'Next' link found. Assuming last page.")
            break

        page_num += 1
        time.sleep(1)  # Be polite

    return all_links

if __name__ == "__main__":
    all_members = get_all_member_links()
    print(f"\nTotal members found: {len(all_members)}")
    for i, member in enumerate(all_members[:20], 1):
        print(f"{i}. {member['text']} - {member['url']}")
