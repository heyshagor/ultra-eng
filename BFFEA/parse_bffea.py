#!/usr/bin/env python3
"""
BFFEA Member List Parser
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

# Find all member entries - they are in table rows with specific structure
# Looking for <tr> tags that contain company information
members = []

# The structure shows members alternating between left column (logo) and right column (details)
# Each member block is in a <tr> with two <td> children
tables = soup.find_all('table')
print(f"Found {len(tables)} tables")

# Find all tr elements that contain member data
# Based on the pattern, each member is in a <tr> with two <td> children
for tr in soup.find_all('tr'):
    tds = tr.find_all('td')
    if len(tds) >= 2:
        # Check if the second td contains a <b> tag with company name
        second_td = tds[1]
        bold_tag = second_td.find('b')
        if bold_tag:
            company_name = bold_tag.get_text(strip=True)
            if company_name and company_name.upper() not in ['BFFEA >> MEMBER']:
                # This is a member entry
                member = {'Company Name': company_name}

                # Get all text from this td
                full_text = second_td.get_text()

                # Extract various fields using regex patterns
                lines = full_text.split('\n')
                cleaned_lines = [line.strip() for line in lines if line.strip()]

                # Initialize fields
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

                for line in cleaned_lines:
                    # Skip the company name line (already captured)
                    if line == company_name:
                        continue

                    # Address lines (before Office:, Factory:, Head Office:, etc.)
                    if any(keyword in line for keyword in ['Office:', 'Registered Office:', 'Head Office:', 'Office & Factory:', 'Factory:', 'Head office & Factory:']):
                        current_section = 'address'
                        address_parts.append(line)
                    elif line.startswith('Tel:') or line.startswith('Phone No.:') or (re.match(r'^\d+-\d+', line) and 'Fax' not in line):
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
                    elif 'USFDA CODE' in line or 'USFDA Code' in line or 'USFDA Regd No' in line or 'USFDA Regd. No' in line or 'USFDA Code No.' in line:
                        # Check if it's both code and reg in one line
                        if 'USFDA Regd No' in line or 'USFDA Regd. No' in line:
                            usfda_regs.append(line)
                        else:
                            usfda_codes.append(line)
                        current_section = 'usfda'
                    elif line.startswith('BFFEA Membership No.') or line.startswith('BFFEA Membership No:'):
                        bffea_nos.append(line)
                        current_section = 'bffea'
                    elif line.startswith('Contact Person') or 'Mr.' in line or 'Mrs.' in line or 'Miss' in line or 'Dr.' in line:
                        contact_persons.append(line)
                        current_section = 'contact'
                    elif current_section == 'address' and not any(keyword in line for keyword in ['Tel:', 'Mob:', 'E-mail:', 'Web:', 'Brand:', 'BFFEA']):
                        address_parts.append(line)
                    elif current_section == 'contact' and ('Mr.' in line or 'Mrs.' in line or 'Miss' in line or 'Dr.' in line or 'Chairman' in line or 'Managing Director' in line or 'Director' in line or 'CEO' in line):
                        contact_persons.append(line)

                # Clean and join address
                member['Address'] = ' | '.join([re.sub(r'^(Office:|Factory:|Registered Office:|Head Office:|Office & Factory:|Head office & Factory:)\s*', '', part).strip() for part in address_parts])

                # Clean and join phones
                member['Phone'] = ' | '.join([re.sub(r'^(Tel:|Phone No\.:)\s*', '', phone).strip() for phone in phones])

                # Clean and join mobiles
                member['Mobile'] = ' | '.join([re.sub(r'^(Mob:|Mobile:)\s*', '', mobile).strip() for mobile in mobiles])

                # Clean and join emails
                member['Email'] = ' | '.join([re.sub(r'^(E-mail:|Email:)\s*', '', email).strip() for email in emails])

                # Clean and join websites
                member['Website'] = ' | '.join([re.sub(r'^(Web:|Website:)\s*', '', web).strip() for web in websites])

                # Clean and join brands
                member['Brand'] = ' | '.join([re.sub(r'^Brand:\s*', '', brand).strip() for brand in brands])

                # Clean and join EU approvals
                member['EU_Approval_No'] = ' | '.join([re.sub(r'^(EU Approval No\.|EU Approval No:)\s*', '', eu).strip() for eu in eu_approvals])

                # Clean and join USFDA codes
                member['USFDA_Code'] = ' | '.join([re.sub(r'^(USFDA CODE:|USFDA Code:|USFDA Code No\.)\s*', '', code).strip() for code in usfda_codes])

                # Clean and join USFDA reg numbers
                member['USFDA_Regd_No'] = ' | '.join([re.sub(r'^USFDA Regd No(?:\.|):\s*', '', reg).strip() for reg in usfda_regs])

                # Clean and join BFFEA membership numbers
                member['BFFEA_Membership_No'] = ' | '.join([re.sub(r'^(BFFEA Membership No\.|BFFEA Membership No:)\s*', '', bffea).strip() for bffea in bffea_nos])

                # Clean and join contact persons
                member['Contact_Persons'] = ' | '.join([re.sub(r'^Contact Person\s*', '', contact).strip() for contact in contact_persons])

                members.append(member)

print(f"Extracted {len(members)} members")

# Write to CSV
if members:
    fieldnames = ['Company Name', 'Address', 'Phone', 'Mobile', 'Email', 'Website', 'Brand',
                  'EU_Approval_No', 'USFDA_Code', 'USFDA_Regd_No', 'BFFEA_Membership_No', 'Contact_Persons']

    with open('bffea_members.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(members)

    print("CSV file 'bffea_members.csv' created successfully!")
    print(f"Total members: {len(members)}")
else:
    print("No members found!")
