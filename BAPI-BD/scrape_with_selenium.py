import csv
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def scrape_with_selenium(url, output_file='bapi_members.csv'):
    """
    Use Selenium to scrape dynamically loaded content.
    """
    print("Setting up Chrome driver...")

    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run in background
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # Disable SSL errors
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')

    # Initialize driver
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("Chrome driver initialized")
    except Exception as e:
        print(f"Error initializing Chrome driver: {e}")
        print("Trying alternative approach...")
        driver = webdriver.Chrome(options=chrome_options)

    try:
        print(f"Navigating to: {url}")
        driver.get(url)

        # Wait for page to load
        print("Waiting for page to load...")
        time.sleep(10)  # Give time for JavaScript to execute

        # Try to find iframes that might contain content
        iframes = driver.find_elements(By.TAG_NAME, 'iframe')
        print(f"Found {len(iframes)} iframes")

        if iframes:
            for i, iframe in enumerate(iframes):
                try:
                    driver.switch_to.frame(iframe)
                    print(f"Switched to iframe {i+1}")
                    time.sleep(2)
                    # Check if there's content here
                    body = driver.find_element(By.TAG_NAME, 'body')
                    if body and body.text.strip():
                        print(f"iframe {i+1} has content: {len(body.text)} chars")
                    driver.switch_to.default_content()
                except:
                    driver.switch_to.default_content()

        # Get page source after JavaScript execution
        html = driver.page_source

        # Save for inspection
        with open('page_rendered.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("Rendered HTML saved to 'page_rendered.html'")

        # Parse with BeautifulSoup
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')

        # Try to find member data
        members_data = []

        # Look for tables
        tables = soup.find_all('table')
        print(f"\nFound {len(tables)} tables")

        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if cols:
                    row_data = [col.get_text(strip=True) for col in cols]
                    if len(row_data) >= 2:
                        members_data.append(row_data)

        # Look for member cards
        if not members_data or len(members_data) < 2:
            print("Searching for member cards...")
            # Common patterns for member listings
            selectors = [
                'div[class*="member"]',
                'div[class*="card"]',
                'div[class*="profile"]',
                'div[class*="listing"]',
                'div[class*="directory"]',
                'div[class*="item"]'
            ]

            for selector in selectors:
                elements = soup.select(selector)
                if len(elements) > 0:
                    print(f"  Selector '{selector}': found {len(elements)} elements")
                    if len(elements) >= 3:  # Likely a list
                        for elem in elements[:10]:
                            text = elem.get_text(separator='|', strip=True)
                            if '|' in text:
                                fields = [f.strip() for f in text.split('|') if f.strip()]
                                if len(fields) >= 2:
                                    members_data.append(fields)
                        break

        # Look for list items that might be members
        if not members_data:
            print("Checking list items...")
            list_items = soup.find_all('li')
            print(f"  Found {len(list_items)} <li> elements")
            for item in list_items[:20]:
                text = item.get_text(strip=True)
                if text and len(text.split()) > 3:
                    members_data.append([text])

        # Save CSV
        if members_data:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(members_data)

            print(f"\n✓ Success! Extracted {len(members_data)} records")
            print(f"✓ Saved to '{output_file}'")
            print(f"\nFirst few rows:")
            for i, row in enumerate(members_data[:5], 1):
                print(f"  {i}. {row[:3]}" + ("..." if len(row) > 3 else ""))
            return True
        else:
            print("\n✗ No data extracted")
            print("\nPlease inspect 'page_rendered.html' to understand the page structure.")
            print("Look for the elements containing member information and note their CSS selectors.")
            return False

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        driver.quit()
        print("Browser closed")

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')

    url = "http://www.bapi-bd.com/members-directory.html"
    output_file = "bapi_members_data.csv"

    print("=" * 60)
    print("BAPI Members Directory Scraper (Selenium)")
    print("=" * 60)
    print()

    success = scrape_with_selenium(url, output_file)

    print("\n" + "=" * 60)
    if success:
        print("SCRAPING COMPLETED SUCCESSFULLY")
    else:
        print("SCRAPING NEEDS ADJUSTMENT")
    print("=" * 60)
