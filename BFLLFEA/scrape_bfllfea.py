import requests
from bs4 import BeautifulSoup
import csv
import time

def scrape_bfllfea_members():
    """
    Scrape member data from https://bfllfea.com/general-member-list
    Extracts: company name, name, member no, contact, product
    """
    url = "https://bfllfea.com/general-member-list"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"Fetching {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        members = []

        # NOTE: You need to inspect the actual HTML structure and update these selectors
        # Common patterns to look for:
        # - Table rows: member_elements = soup.select('table tr')
        # - Card elements: member_elements = soup.select('.member-card')
        # - List items: member_elements = soup.select('.member-list li')

        # Example if data is in a table:
        # rows = soup.select('table tr')
        # for row in rows[1:]:  # Skip header
        #     cols = row.select('td')
        #     if len(cols) >= 5:
        #         member = {
        #             'company_name': cols[0].get_text(strip=True),
        #             'name': cols[1].get_text(strip=True),
        #             'member_no': cols[2].get_text(strip=True),
        #             'contact': cols[3].get_text(strip=True),
        #             'product': cols[4].get_text(strip=True)
        #         }
        #         members.append(member)

        # Extract member data from table rows
        rows = soup.select('tbody tr')

        for row in rows:
            cells = row.select('td')
            # Skip header rows or rows with insufficient data
            if len(cells) < 5:
                continue

            # Check if this is a header row (contains SL. NO or other header text)
            first_cell = cells[0].get_text(strip=True)
            if 'SL. NO' in first_cell or 'NO' in first_cell:
                continue

            # Extract data from each column
            # Columns: SL. NO, NAME AND ADDRESS OF THE FIRM, MEMBERSHIP NO., CONTACT INFO, PRODUCT
            raw_firm_info = cells[1].get_text(strip=True) if len(cells) > 1 else ''
            member_no = cells[2].get_text(strip=True) if len(cells) > 2 else ''
            raw_contact = cells[3].get_text(strip=True) if len(cells) > 3 else ''
            product = cells[4].get_text(strip=True) if len(cells) > 4 else ''

            # Separate phone number and email from contact field
            phone = ''
            email = ''

            if raw_contact:
                import re

                # Look for email pattern - must start with a letter to avoid matching phone digits
                email_match = re.search(r'[a-zA-Z][a-zA-Z0-9._%+-]*@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_contact)
                if email_match:
                    email = email_match.group()
                    # Extract phone: typically starts with +88 or 0 and contains digits, spaces, hyphens
                    # Phone is usually at the beginning, email at the end (concatenated)
                    contact_before_email = raw_contact[:email_match.start()].strip()

                    # Phone number patterns: starts with +88 or 0 and contains digits, spaces, hyphens
                    # Try to extract a valid phone number
                    phone_match = re.search(r'(\+88\s?[\d\-\s]+|0[\d\-\s]+)', contact_before_email)
                    if phone_match:
                        phone = phone_match.group().strip()
                    else:
                        phone = contact_before_email
                else:
                    # No email found, entire contact is phone
                    phone = raw_contact

            # Parse the firm info to separate company name, contact person, and address
            company_name = raw_firm_info
            contact_person = ''

            # Define title keywords that appear after contact person name
            title_keywords = ['PROPRIETOR', 'CHAIRMAN', 'MANAGING DIRECTOR', 'DIRECTOR', 'OWNER', 'PARTNER', 'MANAGING']

            # First, find the last occurrence of a title keyword
            title_pos = -1
            found_title = None
            for keyword in title_keywords:
                # Use case-insensitive search
                pattern = keyword.upper()
                text_upper = raw_firm_info.upper()
                pos = text_upper.rfind(pattern)
                if pos > title_pos:
                    title_pos = pos
                    found_title = keyword

            if title_pos > 0:
                # Everything after the title is address, everything before contains company and person
                before_title = raw_firm_info[:title_pos].strip(' .,-')
                after_title = raw_firm_info[title_pos + len(found_title):].strip(' .,-')

                # Now look for person name (usually starts with MR., MD., etc.)
                person_markers = ['MR. ', 'MD. ', 'HAJJEE ', 'ALHAJ ', 'MR ', 'MD ']
                person_start = -1
                for marker in person_markers:
                    # Case-insensitive search
                    marker_pos = before_title.upper().find(marker.upper())
                    if marker_pos >= 0:
                        person_start = marker_pos + len(marker)
                        person_name_part = before_title[person_start:].strip(' .,-')
                        # Remove any trailing title words from person name (in case they're attached)
                        for title_word in title_keywords:
                            if title_word.upper() in person_name_part.upper():
                                # Find exact position case-insensitively
                                tw_pos = person_name_part.upper().find(title_word.upper())
                                person_name_part = person_name_part[:tw_pos].strip(' .,-')
                        # Reconstruct name with original casing of the marker
                        person_name = before_title[marker_pos:marker_pos+len(marker)].strip() + ' ' + person_name_part
                        person_name = person_name.strip()
                        company_name = before_title[:marker_pos].strip(' .,-')
                        contact_person = person_name
                        break

                # If no person marker found, company name might be the entire before_title
                if person_start == -1:
                    company_name = before_title
                    contact_person = found_title if found_title else ''

            # If we couldn't parse, use raw as company and leave name empty

            member = {
                'company_name': company_name,
                'name': contact_person,
                'member_no': member_no,
                'phone': phone,
                'email': email,
                'product': product
            }
            members.append(member)

        # Save to CSV
        if members:
            filename = 'bfllfea_members.csv'
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['company_name', 'name', 'member_no', 'phone', 'email', 'product']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(members)

            print(f"\n✅ Successfully saved {len(members)} members to {filename}")
        else:
            print("\n❌ No members extracted. Please update the selectors in the script.")

    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    scrape_bfllfea_members()
