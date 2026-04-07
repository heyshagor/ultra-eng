#!/usr/bin/env python3
"""
Generate comprehensive sample BTMA directory data (300+ entries)
Demonstrates all fields: names, companies, multiple phones, multiple emails, etc.
"""

import pandas as pd
import random
from datetime import datetime
from typing import Dict

# Sample data pools
SURNAMES = ['Khan', 'Ahmed', 'Chowdhury', 'Rahman', 'Hossain', 'Islam', 'Uddin', 'Ali', 'Mia', 'Haque', 'Mollah', 'Sheikh', 'Miah', 'Bhuiyan', 'Sarker']
FIRST_NAMES_MALE = ['Mohammad', 'Abdul', 'Md', 'Shahid', 'Alam', 'Faruk', 'Kawsar', 'Motin', 'Salim', 'Masud', 'Nurul', 'Jashim', 'Rashed', 'Sohel', 'Anwar', 'Kamal', 'Jamal', 'Rafiq', 'Monir']
FIRST_NAMES_FEMALE = ['Mahmuda', 'Kohinoor', 'Shamima', 'Farhana', 'Tahmina', 'Nasrin', 'Jahanara', 'Asma', 'Rokeya', 'Laila', 'Sultana', 'Begum', 'Nargis', 'Rina', 'Mina']

COMPANY_SUFFIXES = ['Ltd.', 'Limited', 'Mills Ltd.', 'Industries Ltd.', 'Textiles Ltd.', 'Fabrics Ltd.', 'Group', 'Corporation', 'Plc']
COMPANY_PREFIXES = ['ABM', 'Apex', 'Beximco', 'Square', 'Pacific', 'Fakir', 'Noman', 'MM', 'HR', 'DBL', 'Karni', 'Chisty', 'Akij', 'Husa', 'Bitumen', 'Chandra', 'Dawood', 'Eastern', 'Family', 'Gemini']

PRODUCTS = {
    'Woven Fabrics': ['Poplin', 'Twill', 'Oxford', 'Canvas', 'Chambray', 'Denim', 'Satin', 'Plain Weave', 'Jacquard', 'Herringbone'],
    'Knitted Fabrics': ['Single Jersey', 'Double Jersey', 'Interlock', 'Rib', 'Pique', 'Fleece', 'Terry', 'Mesh', 'Pointelle', 'Lacoste'],
    'Denim': ['Indigo Denim', 'Stretch Denim', 'Ring Denim', 'Open End Denim', 'Organic Denim', 'Slub Denim'],
    'Home Textile': ['Bed Sheet', 'Comforter', 'Pillow', 'Blanket', 'Curtain', 'Bedding Set', 'Terry Towel'],
    'Shirting': ['Plain Shirting', 'Striped Shirting', 'Checked Shirting', 'Printed Shirting', 'Dyed Shirting'],
    'Suiting': ['Wool Suiting', 'Polyester Suiting', 'Blended Suiting', 'Jacket Suiting', 'Trouser Suiting']
}

CITIES = {
    'Dhaka': ['Gulshan', 'Banani', 'Panthapath', 'Motijheel', 'Dilkusha', 'Mirpur', 'Uttara', 'Mohakhali', 'Bashundhara', 'Baridhara'],
    'Narayanganj': ['Narayanganj', 'Adamjeenagar', 'Kanchpur'],
    'Gazipur': ['Tongi', 'Gazipur', 'Konabari'],
    'Chittagong': ['Agrabad', ' Hathazari', 'Patenga'],
    'Sramikpara': ['Sramikpara']
}

AREAS = ['Ward #', 'Road #', 'House #', 'Building #', 'Flat #', 'Shop #', 'BSCIC', 'Industrial Area', 'CEPZ', 'DIT']

def generate_email(name, company):
    """Generate email from name and company"""
    domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'company.com', 'bdmail.net']
    name_part = re.sub(r'[^a-z]', '', name.lower())[:8] if name else ''
    company_part = re.sub(r'[^a-z]', '', company.lower())[:10] if company else ''
    domain = random.choice(domains)

    if random.random() < 0.3 and company_part:
        return f"{name_part}@{company_part}.com"
    else:
        return f"{name_part}@{domain}"


def generate_phone():
    """Generate Bangladeshi phone number"""
    prefixes = ['02', '017', '018', '019', '016']
    prefix = random.choice(prefixes)
    if prefix == '02':
        number = f"{prefix}-{random.randint(1000000, 9999999)}"
    else:
        number = f"{prefix}-{random.randint(1000000, 9999999)}"
    return number


def generate_full_address():
    """Generate full address"""
    city = random.choice(list(CITIES.keys()))
    area = random.choice(CITIES[city])
    area_type = random.choice(AREAS)
    number = str(random.randint(1, 200))
    street = random.choice(['Rupkothar', 'Main', 'East', 'West', 'North', 'South', 'Bashundhara', 'Pallabi', 'Kawran'])

    patterns = [
        f"House #{number}, {area_type} {number}, {area}, {city}",
        f"{area_type} {number}, {street} Road, {area}, {city}",
        f"Building #{number}, {area}, {city}",
        f"{number}, {street} {area}, {city}-{random.randint(1000, 9999)}",
        f"Shop #{number}, {area_type}, {area}, {city}"
    ]

    return random.choice(patterns)


def generate_single_entry(entry_num: int) -> Dict:
    """Generate a single manufacturer entry"""

    # Company name
    prefix = random.choice(COMPANY_PREFIXES)
    suffix = random.choice(COMPANY_SUFFIXES)
    company_name = f"{prefix} {random.choice(['', 'Group ', ''])}{' '.join(random.sample(['Textile', 'Fabrics', 'Industries', 'Mills', 'Manufacturing'], random.randint(1,2)))} {suffix}".strip()
    if random.random() < 0.3:
        company_name = f"{prefix} {suffix}"

    # Contact person
    gender = random.choice(['male', 'female'])
    if gender == 'male':
        first = random.choice(FIRST_NAMES_MALE)
    else:
        first = random.choice(FIRST_NAMES_FEMALE)
    surname = random.choice(SURNAMES)
    contact_person = f"{first} {surname}"

    # Phone numbers (2-3)
    phones = [generate_phone() for _ in range(random.randint(2, 3))]

    # Email addresses (2-4)
    emails = [
        generate_email(contact_person, company_name),
        generate_email(company_name, '') if random.random() < 0.7 else None,
        generate_email('info', company_name) if random.random() < 0.6 else None,
        generate_email('sales', company_name) if random.random() < 0.5 else None,
    ]
    emails = [e for e in emails if e][:4]  # Remove None, max 4

    # Website
    if random.random() < 0.8:
        company_simple = re.sub(r'[^a-z]', '', company_name.lower())[:15]
        website = f"www.{company_simple}.com"
    else:
        website = ""

    # Address
    address = generate_full_address()

    # Products
    product_cat = random.choice(list(PRODUCTS.keys()))
    available = PRODUCTS[product_cat]
    k = min(random.randint(3, 6), len(available))
    product_list = random.sample(available, k=k)
    products = ', '.join(product_list)

    # BTMA Member (mostly Yes)
    btma_member = 'Yes' if random.random() < 0.85 else 'No'

    return {
        'entry_number': entry_num,
        'company_name': company_name,
        'contact_person': contact_person,
        'company_phone': phones[0] if phones else "",
        'personal_phone': phones[1] if len(phones) > 1 else "",
        'mobile_phone': phones[2] if len(phones) > 2 else "",
        'company_email': emails[0] if emails else "",
        'contact_email': emails[1] if len(emails) > 1 else "",
        'additional_emails': '; '.join(emails[2:]) if len(emails) > 2 else "",
        'website': website,
        'address': address,
        'product_category': product_cat,
        'products': products,
        'btma_member': btma_member,
        'registration_no': f"BTMA-{random.randint(1000, 9999)}" if btma_member == 'Yes' else "",
        'raw_entry': f"{company_name}\n{contact_person}\n{phones[0] if phones else ''}\n{emails[0] if emails else ''}\n{address}\n{products}"
    }


def generate_full_dataset(num_entries: int = 320) -> pd.DataFrame:
    """Generate full BTMA directory dataset"""
    print(f"Generating {num_entries} manufacturer entries...")

    entries = []
    for i in range(1, num_entries + 1):
        entry = generate_single_entry(i)
        entries.append(entry)

        if i % 50 == 0:
            print(f"  Generated {i}/{num_entries}...")

    df = pd.DataFrame(entries)

    # Reorder columns logically
    column_order = [
        'entry_number', 'company_name', 'contact_person',
        'company_phone', 'personal_phone', 'mobile_phone',
        'company_email', 'contact_email', 'additional_emails',
        'website', 'address',
        'product_category', 'products',
        'btma_member', 'registration_no',
        'raw_entry'
    ]

    return df[column_order]


def main():
    print("="*60)
    print(" BTMA FULL SAMPLE DATA GENERATOR")
    print("="*60)
    print()
    print("Generating comprehensive dataset with following fields:")
    print("  - Entry Number")
    print("  - Company Name")
    print("  - Contact Person")
    print("  - Company Phone")
    print("  - Personal Phone")
    print("  - Mobile Phone")
    print("  - Company Email")
    print("  - Contact Email")
    print("  - Additional Emails")
    print("  - Website")
    print("  - Full Address")
    print("  - Product Category")
    print("  - Products List")
    print("  - BTMA Member")
    print("  - Registration No.")
    print()
    print(f"Total entries: 320")
    print()

    # Generate
    df = generate_full_dataset(320)

    # Save to CSV
    csv_file = 'btma_full_directory.csv'
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    print(f"\n✓ CSV saved: {csv_file} ({len(df)} rows, {len(df.columns)} columns)")

    # Save to Excel
    excel_file = 'btma_full_directory.xlsx'
    df.to_excel(excel_file, index=False, engine='openpyxl')
    print(f"✓ Excel saved: {excel_file}")

    # Save readable text version
    txt_file = 'btma_full_directory.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("BTMA Fabric Manufacturer Directory\n")
        f.write(f"Generated: {datetime.now()}\n")
        f.write(f"Total Manufacturers: {len(df)}\n\n")
        f.write("="*80 + "\n\n")

        for _, row in df.iterrows():
            f.write(f"Entry #{row['entry_number']}\n")
            f.write(f"Company: {row['company_name']}\n")
            f.write(f"Contact: {row['contact_person']}\n")
            f.write(f"Phones: {row['company_phone']}")
            if row['personal_phone']:
                f.write(f", {row['personal_phone']}")
            if row['mobile_phone']:
                f.write(f", {row['mobile_phone']}")
            f.write("\n")
            f.write(f"Emails: {row['company_email']}")
            if row['contact_email']:
                f.write(f", {row['contact_email']}")
            if row['additional_emails']:
                f.write(f", {row['additional_emails']}")
            f.write("\n")
            if row['website']:
                f.write(f"Website: {row['website']}\n")
            f.write(f"Address: {row['address']}\n")
            f.write(f"Category: {row['product_category']}\n")
            f.write(f"Products: {row['products']}\n")
            f.write(f"BTMA Member: {row['btma_member']}")
            if row['registration_no']:
                f.write(f" (Reg: {row['registration_no']})")
            f.write("\n")
            f.write("-"*80 + "\n\n")

    print(f"✓ Text report: {txt_file}")

    # Summary by category
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"Total Manufacturers: {len(df)}")
    print(f"\nBy Product Category:")
    for cat, count in df['product_category'].value_counts().items():
        print(f"  {cat}: {count}")
    print(f"\nBTMA Members: {df['btma_member'].value_counts().get('Yes', 0)}")
    print(f"Non-Members: {df['btma_member'].value_counts().get('No', 0)}")
    print(f"\nMultiple Emails: {len(df[df['additional_emails'] != ''])}")
    print(f"Multiple Phones: {len(df[df['mobile_phone'] != ''])}")
    print(f"Has Website: {len(df[df['website'] != ''])}")
    print()

    print("="*60)
    print("Files created:")
    print("  1. btma_full_directory.csv  - Complete CSV")
    print("  2. btma_full_directory.xlsx - Complete Excel")
    print("  3. btma_full_directory.txt  - Human-readable format")
    print("="*60)

    return df


if __name__ == '__main__':
    import re
    df_result = main()
