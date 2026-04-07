import csv

def clean_csv(input_file, output_file):
    """Clean up the scraped CSV data"""
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)

    # Find the header row (contains 'Sl. No.')
    header_index = None
    for i, row in enumerate(rows):
        if any('Sl. No.' in cell for cell in row if cell):
            header_index = i
            break

    if header_index is None:
        print("Header not found")
        return

    print(f"Found header at row {header_index + 1}")

    # Extract clean data
    clean_rows = []
    clean_rows.append(rows[header_index])  # Add header

    # Add data rows after header
    for row in rows[header_index + 1:]:
        # Skip empty or noise rows
        if not row or all(not cell or cell.strip() in ['×', 'search', 'Sort byRelevanceDate'] for cell in row):
            continue
        if len(row) >= 3 and row[0].strip().isdigit():  # First column is a number
            clean_rows.append(row)

    print(f"Extracted {len(clean_rows) - 1} data rows")

    # Write cleaned data
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(clean_rows)

    print(f"Cleaned data saved to '{output_file}'")

    # Also create a nicely formatted version with separate columns
    print("\nCreating detailed CSV with separated columns...")
    create_detailed_csv(clean_rows[1:])  # Skip header

def create_detailed_csv(data_rows):
    """Create a more structured CSV with separated fields"""
    detailed_rows = []

    for row in data_rows:
        # Ensure we have at least 3 columns
        if len(row) < 5:
            row = row + [''] * (5 - len(row))

        sl_no = row[0].strip()
        company_info = row[1].strip() if len(row) > 1 else ''
        representative = row[2].strip() if len(row) > 2 else ''
        telephone = row[3].strip() if len(row) > 3 else ''
        website = row[4].strip() if len(row) > 4 else ''

        # Parse company info to separate name, address, email
        parts = company_info.split('E-mail:') if 'E-mail:' in company_info else [company_info, '']
        company_address = parts[0].strip()
        email = parts[1].strip() if len(parts) > 1 else ''

        detailed_rows.append([
            sl_no,
            company_address,
            email,
            representative,
            telephone,
            website
        ])

    with open('bapi_members_detailed.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Sl. No.', 'Company Name & Address', 'Email', 'Representative', 'Telephone', 'Website'])
        writer.writerows(detailed_rows)

    print(f"Detailed CSV saved to 'bapi_members_detailed.csv'")
    print(f"Columns: {['Sl. No.', 'Company Name & Address', 'Email', 'Representative', 'Telephone', 'Website']}")

if __name__ == "__main__":
    clean_csv('bapi_members_data.csv', 'bapi_members_cleaned.csv')
