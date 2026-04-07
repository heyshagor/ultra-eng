"""
Advanced Data Parser for BTMA Fabric Manufacturer Information
Parses and structures raw extracted data into meaningful records
"""

import pandas as pd
import re
from typing import List, Dict, Any
import logging
from .extractor import PDFExtractor

logger = logging.getLogger(__name__)


class BTMAParser:
    """Parser specifically designed for BTMA fabric manufacturer data"""

    def __init__(self):
        self.raw_data = None
        self.parsed_data = {}

    def load_from_extractor(self, extractor: PDFExtractor) -> 'BTMAParser':
        """Load data from a PDFExtractor instance"""
        if not extractor.pages_data:
            raise ValueError("Extractor has no data. Call extract_all() first.")
        self.raw_data = extractor._structure_output()
        return self

    def parse_companies(self) -> pd.DataFrame:
        """
        Parse company information from the PDF
        Expected patterns: Company Name, Address, Phone, Email, Website
        """
        companies = []

        if not self.raw_data:
            raise ValueError("No data loaded. Use load_from_extractor() first.")

        # Combine all text
        full_text = self.raw_data['full_text']
        lines = full_text.split('\n')

        current_company = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to detect company name (usually in caps or with specific patterns)
            if self._is_company_name(line):
                if current_company and len(current_company.get('name', '')) > 2:
                    companies.append(current_company)
                current_company = {'company_name': line, 'raw_lines': [line]}

            # Parse contact information
            elif current_company:
                current_company['raw_lines'].append(line)

                # Extract email
                emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', line)
                if emails and 'email' not in current_company:
                    current_company['email'] = emails[0]

                # Extract phone
                phones = re.findall(r'(\+?88)?[\s\-]?[\d\s]{10,}', line)
                if phones and 'phone' not in current_company:
                    current_company['phone'] = phones[0].strip()

                # Extract address (lines that contain street/road/market/etc)
                if any(keyword in line.lower() for keyword in
                       ['road', 'market', 'street', 'po box', 'ward', 'thana', 'district']):
                    if 'address' not in current_company:
                        current_company['address'] = line
                    else:
                        current_company['address'] += ', ' + line

                # Extract website
                if 'www.' in line.lower() or '.com' in line.lower():
                    current_company['website'] = line

        # Add last company
        if current_company and len(current_company.get('company_name', '')) > 2:
            companies.append(current_company)

        # Clean and create DataFrame
        df = pd.DataFrame(companies)
        if not df.empty:
            # Clean column names
            df.columns = [col.lower().replace('_', ' ').title() for col in df.columns]
            # Keep only essential columns if they exist
            essential_cols = ['Company Name', 'Address', 'Phone', 'Email', 'Website']
            existing_cols = [col for col in essential_cols if col in df.columns]
            if existing_cols:
                df = df[existing_cols]

        self.parsed_data['companies'] = df
        return df

    def _is_company_name(self, line: str) -> bool:
        """Detect if a line is likely a company name"""
        line = line.strip()

        # Check patterns common in BTMA directory
        patterns = [
            r'^[A-Z][A-Z\s\.&]+$',  # All caps with spaces
            r'^[A-Z][a-zA-Z\s\.&]+(?:\s+Ltd\.?)?$',  # Company name with Ltd
            r'^[A-Z][a-zA-Z\s\.\-&]+(?:Mills|Industries|Textile|Fabrics)?$',
        ]

        for pattern in patterns:
            if re.match(pattern, line):
                return True

        # Check if line is very short (likely not a full company entry)
        if len(line) < 5:
            return False

        return False

    def parse_products(self) -> pd.DataFrame:
        """Parse product information"""
        products = []
        full_text = self.raw_data['full_text']
        lines = full_text.split('\n')

        current_section = None
        for line in lines:
            line = line.strip().lower()

            # Detect product categories
            if any(keyword in line for keyword in ['fabric', 'textile', 'yarn', 'cotton']):
                current_section = line
            elif line and current_section and not self._is_company_name(line):
                products.append({
                    'category': current_section,
                    'product': line
                })

        df = pd.DataFrame(products)
        if not df.empty:
            df['category'] = df['category'].str.title()
            df['product'] = df['product'].str.title()

        self.parsed_data['products'] = df
        return df

    def parse_contacts(self) -> pd.DataFrame:
        """Parse contact information systematically"""
        contacts = []

        if 'companies' in self.parsed_data:
            companies_df = self.parsed_data['companies']
            for _, row in companies_df.iterrows():
                contact = {'company': row.get('Company Name', '')}
                for col in ['Phone', 'Email', 'Website', 'Address']:
                    if col in row:
                        contact[col.lower()] = row[col]
                contacts.append(contact)

        df = pd.DataFrame(contacts)
        self.parsed_data['contacts'] = df
        return df

    def get_all_parsed(self) -> Dict[str, pd.DataFrame]:
        """Get all parsed DataFrames"""
        if not self.parsed_data:
            self.parse_all()

        return self.parsed_data

    def parse_all(self):
        """Run all parsing methods"""
        logger.info("Starting full parsing...")
        self.parse_companies()
        self.parse_products()
        self.parse_contacts()
        logger.info("Parsing completed")

    def to_excel_multisheet(self, output_path: str):
        """Export all parsed data to Excel with multiple sheets"""
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for name, df in self.parsed_data.items():
                if not df.empty:
                    sheet_name = name[:31]  # Excel sheet name limit
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        logger.info(f"Parsed data saved to: {output_path}")
        return output_path
