#!/usr/bin/env python3
"""
Parse BGMEA Associate Members PDF (BuyingHouse_AssociateMember.pdf)
Extracts member data and saves to CSV.
"""

import re
import csv
from pathlib import Path

PDF_TEXT = '/tmp/associate_members.txt'  # we'll create this

def convert_pdf_to_text():
    """Convert PDF to text using pdftotext if not already done"""
    import subprocess
    if not Path(PDF_TEXT).exists():
        subprocess.run(['pdftotext', '-layout', '/tmp/associate_members.pdf', PDF_TEXT], check=True)
    with open(PDF_TEXT, 'r', encoding='utf-8') as f:
        return f.read()

def parse_columns(text):
    """
    The PDF has 3 columns per page. Using -layout, each line has spaces aligning columns.
    We'll split each line into three parts based on fixed column positions.
    Determine column positions by sampling the header line.
    """
    lines = text.split('\n')
    # Find the header line that says "List of Associate Member..."
    header_idx = next(i for i, line in enumerate(lines) if 'List of Associate Member' in line)
    header_line = lines[header_idx]
    # The three column names are: probably empty, then the next two? Actually we need to find where each column block starts.
    # We'll use a heuristic: each member entry occupies 6 lines: Name, Designation, Company (Reg), Addr1, Addr2/Contact, then blank.
    # Instead, we can split the entire text into three separate column strings by noticing that the columns are separated by a gap of at least 5 spaces.
    # We'll go line by line and split on multiple spaces.
    columns = [[] for _ in range(3)]
    for line in lines:
        # Skip header and lines before actual data
        # Determine column breaks: find positions where there are 3+ consecutive spaces
        parts = re.split(r'\s{3,}', line)
        # parts length likely 3 or more (some lines may be empty in some columns)
        if len(parts) >= 3:
            for i in range(3):
                columns[i].append(parts[i] if i < len(parts) else '')
        else:
            # line may be a continuation within a column, assign to first column that is not empty? Or distribute?
            # For simplicity, treat as additional line for first column?
            if any(part.strip() for part in parts):
                # If not all parts empty, maybe this is a continuation line that didn't break into 3 cols.
                # Append to the last non-empty column? We'll add to the first column as continuation of previous block.
                columns[0].append(line)
                columns[1].append('')
                columns[2].append('')
    # Now each column is a list of lines (some may be blank). We'll process each column separately.
    return columns

def parse_column(lines):
    """
    Parse a single column's lines into member records.
    Each member record is a list of fields: Name, Designation, Company (with Reg), Address, Town/City, Phone, Email, etc.
    The pattern:
    Line1: Name
    Line2: Designation
    Line3: Company (Reg: X)
    Next line(s): Address lines (typically 2 lines)
    Then: Tel: ... or Phone ...
    Then: Email: ...
    Possibly there are more lines (e.g., additional contact numbers).
    There may be blank lines separating members.
    """
    members = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        # Name line (should be name, not starting with common titles like "Managing", "Proprietor", but those can be names too)
        name = line
        i += 1
        if i >= len(lines): break
        designation = lines[i].strip()
        i += 1
        if i >= len(lines): break
        company = lines[i].strip()
        i += 1

        # Address lines: expect at least 1-2 lines until we hit a line with "Tel:" or "Phone" or "Email"
        address_lines = []
        while i < len(lines):
            l = lines[i].strip()
            if not l:
                i += 1
                continue
            if l.startswith('Tel:') or l.startswith('Phone') or l.startswith('Email'):
                break
            address_lines.append(l)
            i += 1
        address = ' '.join(address_lines)

        # Now capture Tel, Email, maybe Phone
        tel = ''
        email = ''
        # The current line may contain Tel/Phone or Email
        while i < len(lines):
            l = lines[i].strip()
            if not l:
                i += 1
                continue
            if l.startswith('Tel:'):
                tel = l
            elif l.startswith('Phone'):
                tel = l
            elif l.startswith('Email:'):
                email = l[6:]  # remove "Email:"
            else:
                # Could be something else or next member name
                break
            i += 1

        members.append({
            'Name': name,
            'Designation': designation,
            'Company': company,
            'Address': address,
            'Contact': tel,
            'Email': email
        })
    return members

def main():
    print("Parsing Associate Members PDF...")
    text = convert_pdf_to_text()
    print(f"Text length: {len(text)} chars")
    columns = parse_columns(text)
    print(f"Column lines: {[len(col) for col in columns]}")

    all_members = []
    for idx, col in enumerate(columns):
        print(f"Parsing column {idx+1}...")
        col_members = parse_column(col)
        print(f"  Found {len(col_members)} members")
        all_members.extend(col_members)

    # Write to CSV
    out_file = 'bgmea_associate_members.csv'
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['Name', 'Designation', 'Company', 'Address', 'Contact', 'Email'])
        writer.writeheader()
        writer.writerows(all_members)

    print(f"\nSaved {len(all_members)} associate members to {out_file}")

if __name__ == '__main__':
    main()
