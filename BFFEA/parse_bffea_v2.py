#!/usr/bin/env python3
"""
BFFEA Member List Parser v2
Extracts member data from HTML and saves to CSV for SEO & Marketing
"""

import re
import csv
from bs4 import BeautifulSoup

# Read the HTML file
with open('bffea_member_list.html', 'r', encoding='iso-8859-1') as f:
    html_content = f.read()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all tr elements that contain member data
members = []

for tr in soup.find_all('tr'):
    tds = tr.find_all('td')

    # Looking for the pattern: first td has width="15%" (logo), second td has width="50%" (details)
    if len(tds) >= 2:
        first_td = tds[0]
        second_td = tds[1]

        # Check if first td has an img tag (logo) - this indicates it's a member entry
        img_tag = first_td.find('img')
        bold_tag = second_td.find('b')

        if img_tag is not None and bold_tag:
            company_name = bold_tag.get_text(strip=True)

            # Skip if it's not a real company entry
            if not company_name or company_name.upper() in ['BFFEA >> MEMBER']:
                continue

            # Extract text from ONLY this second td (not the whole document)
            full_text = second_td.get_text()

            # Initialize member dict
            member = {'Company Name': company_name}

            # Split into lines and clean
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]

            # Remove the company name line from lines
            lines = [line for line in lines if line != company_name]

            # Initialize field lists
            address_parts = []
            phones = []
            mobiles = []
            emails = []
            websites = []
            brands = []
            eu_approvals = []
            usfda_codes = []
            usfda_regs = []
            bffea_nos = []
            contact_persons = []

            current_section = 'general'

            for line in lines:
                # Detect section headers
                if any(keyword in line for keyword in ['Office:', 'Registered Office:', 'Head Office:', 'Office & Factory:', 'Factory:', 'Head office & Factory:']):
                    current_section = 'address'
                    address_parts.append(line)
                elif line.startswith('Tel:') or line.startswith('Phone No.:'):
                    phones.append(line)
                    current_section = 'phone'
                elif line.startswith('Mob:') or line.startswith('Mobile:'):
                    mobiles.append(line)
                    current_section = 'mobile'
                elif line.startswith('E-mail:') or line.startswith('Email:'):
                    emails.append(line)
                    current_section = 'email'
                elif line.startswith('Web:') or line.startswith('Website:'):
                    websites.append(line)
                    current_section = 'website'
                elif line.startswith('Brand:'):
                    brands.append(line)
                    current_section = 'brand'
                elif 'EU Approval No.' in line or 'EU Approval No:' in line:
                    eu_approvals.append(line)
                    current_section = 'eu'
                elif 'USFDA CODE' in line or 'USFDA Code' in line or 'USFDA Code No.' in line:
                    usfda_codes.append(line)
                    current_section = 'usfda'
                elif 'USFDA Regd No' in line or 'USFDA Regd. No' in line:
                    usfda_regs.append(line)
                    current_section = 'usfda'
                elif line.startswith('BFFEA Membership No.') or line.startswith('BFFEA Membership No:'):
                    bffea_nos.append(line)
                    current_section = 'bffea'
                elif line.startswith('Contact Person'):
                    contact_persons.append(line)
                    current_section = 'contact'
                elif current_section == 'address' and not any(line.startswith(kw) for kw in ['Tel:', 'Mob:', 'E-mail:', 'Web:', 'Brand:', 'BFFEA']):
                    address_parts.append(line)
                elif current_section == 'contact':
                    # Capture contact person lines
                    if any(marker in line for marker in ['Mr.', 'Mrs.', 'Miss', 'Dr.', 'Chairman', 'Managing Director', 'Director', 'CEO', 'Deputy Managing Director', 'Executive Director']):
                        contact_persons.append(line)

            # Clean and consolidate address
            cleaned_address = []
            for part in address_parts:
                # Remove prefixes like "Office:", "Factory:", etc.
                cleaned = re.sub(r'^(Office:|Registered Office:|Head Office:|Office & Factory:|Factory:|Head office & Factory:)\s*', '', part, flags=re.IGNORECASE)
                cleaned_address.append(cleaned.strip())
            member['Address'] = ' | '.join(cleaned_address)

            # Clean phones
            member['Phone'] = ' | '.join([re.sub(r'^(Tel:|Phone No\.:)\s*', '', p, flags=re.IGNORECASE).strip() for p in phones])

            # Clean mobiles
            member['Mobile'] = ' | '.join([re.sub(r'^(Mob:|Mobile:)\s*', '', m, flags=re.IGNORECASE).strip() for m in mobiles])

            # Clean emails
            member['Email'] = ' | '.join([re.sub(r'^(E-mail:|Email:)\s*', '', e, flags=re.IGNORECASE).strip() for e in emails])

            # Clean websites
            member['Website'] = ' | '.join([re.sub(r'^(Web:|Website:)\s*', '', w, flags=re.IGNORECASE).strip() for w in websites])

            # Clean brands
            member['Brand'] = ' | '.join([re.sub(r'^Brand:\s*', '', b, flags=re.IGNORECASE).strip() for b in brands])

            # Clean EU approvals
            member['EU_Approval_No'] = ' | '.join([re.sub(r'^(EU Approval No\.|EU Approval No:)\s*', '', e, flags=re.IGNORECASE).strip() for e in eu_approvals])

            # Clean USFDA codes
            member['USFDA_Code'] = ' | '.join([re.sub(r'^(USFDA CODE:|USFDA Code:|USFDA Code No\.)\s*', '', c, flags=re.IGNORECASE).strip() for c in usfda_codes])

            # Clean USFDA regs
            member['USFDA_Regd_No'] = ' | '.join([re.sub(r'^USFDA Regd No(?:\.|):\s*', '', r).strip() for r in usfda_regs])

            # Clean BFFEA membership numbers
            member['BFFEA_Membership_No'] = ' | '.join([re.sub(r'^(BFFEA Membership No\.|BFFEA Membership No:)\s*', '', b, flags=re.IGNORECASE).strip() for b in bffea_nos])

            # Clean contact persons
            cleaned_contacts = []
            for contact in contact_persons:
                for prefix in ['Contact Person', 'Contact-Mr.', 'Mob :']:
                    contact = re.sub(prefix, '', contact, flags=re.IGNORECASE).strip()
                cleaned_contacts.append(contact)
            member['Contact_Persons'] = ' | '.join(cleaned_contacts)

            members.append(member)

print(f"Extracted {len(members)} members")

# Write to CSV
if members:
    fieldnames = ['Company Name', 'Address', 'Phone', 'Mobile', 'Email', 'Website', 'Brand',
                  'EU_Approval_No', 'USFDA_Code', 'USFDA_Regd_No', 'BFFEA_Membership_No', 'Contact_Persons']

    with open('bffea_members_v2.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(members)

    print("CSV file 'bffea_members_v2.csv' created successfully!")
    print(f"Total members: {len(members)}")
else:
    print("No members found!")
