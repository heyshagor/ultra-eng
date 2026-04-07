#!/usr/bin/env python3
"""
BFFEA Member List Parser v3 - Simple and robust extraction
"""

import re
import csv
from bs4 import BeautifulSoup

# Read the HTML file
with open('bffea_member_list.html', 'r', encoding='iso-8859-1') as f:
    html_content = f.read()

# Parse HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the inner table that contains all members
# Looking for the table with width="98%"
inner_table = None
for table in soup.find_all('table'):
    if table.get('width') == '98%':
        inner_table = table
        break

if not inner_table:
    print("Could not find inner table")
    exit(1)

# Get all TR elements in the table
all_trs = inner_table.find_all('tr')
print(f"Found {len(all_trs)} <tr> elements")

members = []
current_member = None

for tr in all_trs:
    tds = tr.find_all('td')

    if len(tds) >= 2:
        first_td = tds[0]
        second_td = tds[1]

        # Check if this TR starts a new member (has img in first td + bold in second)
        img_tag = first_td.find('img')
        bold_tag = second_td.find('b')

        if img_tag is not None and bold_tag:
            # Save previous member if exists
            if current_member and current_member['Company Name']:
                members.append(current_member)

            # Start new member
            company_name = bold_tag.get_text(strip=True)
            if company_name and company_name.upper() != 'BFFEA >> MEMBER':
                current_member = {
                    'Company Name': company_name,
                    'Address': '',
                    'Phone': '',
                    'Mobile': '',
                    'Email': '',
                    'Website': '',
                    'Brand': '',
                    'EU_Approval_No': '',
                    'USFDA_Code': '',
                    'USFDA_Regd_No': '',
                    'BFFEA_Membership_No': '',
                    'Contact_Persons': ''
                }

                # Extract data from this member's second td only
                text = second_td.get_text()

                # Parse the text line by line
                lines = [line.strip() for line in text.split('\n') if line.strip()]

                # Remove company name from lines
                lines = [l for l in lines if l != company_name]

                # Temporary storage for raw data
                address_lines = []
                phone_lines = []
                mobile_lines = []
                email_lines = []
                website_lines = []
                brand_lines = []
                eu_lines = []
                usfda_code_lines = []
                usfda_reg_lines = []
                bffea_lines = []
                contact_lines = []

                current_area = 'address'

                for line in lines:
                    if line.startswith('Tel:') or line.startswith('Phone No.:'):
                        current_area = 'phone'
                        phone_lines.append(line)
                    elif line.startswith('Mob:') or line.startswith('Mobile:'):
                        current_area = 'mobile'
                        mobile_lines.append(line)
                    elif line.startswith('E-mail:') or line.startswith('Email:'):
                        current_area = 'email'
                        email_lines.append(line)
                    elif line.startswith('Web:') or line.startswith('Website:'):
                        current_area = 'website'
                        website_lines.append(line)
                    elif line.startswith('Brand:'):
                        current_area = 'brand'
                        brand_lines.append(line)
                    elif 'EU Approval No.' in line or 'EU Approval No:' in line:
                        current_area = 'eu'
                        eu_lines.append(line)
                    elif 'USFDA CODE' in line or 'USFDA Code' in line or 'USFDA Code No.' in line:
                        current_area = 'usfda'
                        usfda_code_lines.append(line)
                    elif 'USFDA Regd No' in line or 'USFDA Regd. No' in line:
                        current_area = 'usfda'
                        usfda_reg_lines.append(line)
                    elif line.startswith('BFFEA Membership No.') or line.startswith('BFFEA Membership No:'):
                        current_area = 'bffea'
                        bffea_lines.append(line)
                    elif line.startswith('Contact Person'):
                        current_area = 'contact'
                        contact_lines.append(line)
                    elif current_area == 'address':
                        address_lines.append(line)
                    elif current_area == 'contact':
                        if any(m in line for m in ['Mr.', 'Mrs.', 'Miss', 'Dr.', 'Chairman', 'Managing Director', 'Director', 'CEO']):
                            contact_lines.append(line)

                # Clean and join
                def clean_prefix(text, prefixes):
                    for prefix in prefixes:
                        if text.startswith(prefix):
                            return text[len(prefix):].strip()
                    return text

                addr_clean = [clean_prefix(l, ['Office:', 'Registered Office:', 'Head Office:', 'Office & Factory:', 'Factory:', 'Head office & Factory:']) for l in address_lines]
                current_member['Address'] = ' | '.join(addr_clean)

                current_member['Phone'] = ' | '.join([clean_prefix(l, ['Tel:', 'Phone No.:']) for l in phone_lines])
                current_member['Mobile'] = ' | '.join([clean_prefix(l, ['Mob:', 'Mobile:']) for l in mobile_lines])
                current_member['Email'] = ' | '.join([clean_prefix(l, ['E-mail:', 'Email:']) for l in email_lines])
                current_member['Website'] = ' | '.join([clean_prefix(l, ['Web:', 'Website:']) for l in website_lines])
                current_member['Brand'] = ' | '.join([clean_prefix(l, ['Brand:']) for l in brand_lines])
                current_member['EU_Approval_No'] = ' | '.join([clean_prefix(l, ['EU Approval No.', 'EU Approval No:']) for l in eu_lines])
                current_member['USFDA_Code'] = ' | '.join([clean_prefix(l, ['USFDA CODE:', 'USFDA Code:', 'USFDA Code No.']) for l in usfda_code_lines])
                current_member['USFDA_Regd_No'] = ' | '.join([re.sub(r'^USFDA Regd No(?:\.|):\s*', '', l) for l in usfda_reg_lines])
                current_member['BFFEA_Membership_No'] = ' | '.join([clean_prefix(l, ['BFFEA Membership No.', 'BFFEA Membership No:']) for l in bffea_lines])

                contact_clean = []
                for c in contact_lines:
                    c_text = c
                    for prefix in ['Contact Person', 'Contact-Mr.', 'Mob :']:
                        c_text = re.sub(prefix, '', c_text, flags=re.IGNORECASE).strip()
                    contact_clean.append(c_text)
                current_member['Contact_Persons'] = ' | '.join(contact_clean)

# Save last member
if current_member and current_member['Company Name']:
    members.append(current_member)

print(f"Extracted {len(members)} members")

# Write to CSV
if members:
    fieldnames = ['Company Name', 'Address', 'Phone', 'Mobile', 'Email', 'Website', 'Brand',
                  'EU_Approval_No', 'USFDA_Code', 'USFDA_Regd_No', 'BFFEA_Membership_No', 'Contact_Persons']

    with open('bffea_members_clean.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(members)

    print("CSV file 'bffea_members_clean.csv' created successfully!")
    print(f"Total members: {len(members)}")
else:
    print("No members found!")
