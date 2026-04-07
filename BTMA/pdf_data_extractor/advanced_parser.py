"""
Advanced Parser for BTMA Directory PDF
Extracts 300+ manufacturer entries with all contact details
"""

import pandas as pd
import re
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BTMADirectoryParser:
    """
    Advanced parser for BTMA fabric manufacturer directory.
    Handles multiple emails, phones, and comprehensive company data.
    """

    def __init__(self):
        self.entries = []
        self.raw_text = ""

    def load_text(self, text: str):
        """Load raw extracted text"""
        self.raw_text = text
        logger.info(f"Loaded {len(text)} characters of text")

    def parse_all_entries(self) -> pd.DataFrame:
        """
        Parse all manufacturer entries from directory text.
        Expected format: Company name, contact person, phones, emails, addresses, products
        """
        logger.info("Starting comprehensive parsing...")

        # Split into potential entry blocks
        entries = self._split_into_entries()

        logger.info(f"Found {len(entries)} potential entries")

        parsed_data = []
        for i, entry in enumerate(entries, 1):
            if i % 50 == 0:
                logger.info(f"Parsing entry {i}/{len(entries)}")

            parsed_entry = self._parse_single_entry(entry, i)
            if parsed_entry and self._is_valid_entry(parsed_entry):
                parsed_data.append(parsed_entry)

        logger.info(f"Successfully parsed {len(parsed_data)} valid entries")

        # Create DataFrame with all columns
        df = pd.DataFrame(parsed_data)

        # Ensure all expected columns exist
        expected_cols = [
            'entry_number', 'company_name', 'contact_person',
            'company_phone', 'personal_phone', 'company_email',
            'personal_email', 'website', 'address',
            'product_category', 'products', 'btma_member',
            'raw_text'
        ]

        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""

        # Reorder columns
        df = df[expected_cols]

        return df

    def _split_into_entries(self) -> List[str]:
        """
        Split raw text into individual manufacturer entries.
        BTMA directories typically have consistent patterns.
        """
        text = self.raw_text

        # Strategy 1: Split by double newlines (common in directories)
        blocks = [b.strip() for b in text.split('\n\n') if b.strip()]

        # If we got too few blocks, try alternative splitting
        if len(blocks) < 100:
            # Strategy 2: Look for numbered entries or company designations
            # Companies often end with Ltd., Limited, Mills, Industries, etc.
            pattern = r'(?=\n[A-Z][A-Za-z\s\.&]+(?:Ltd\.?|Limited|Mills|Industries|Textile|Fabrics|Group|Corporation|Plc)\n)'
            blocks = re.split(pattern, text)
            blocks = [b.strip() for b in blocks if b.strip() and len(b.strip()) > 30]

        # Strategy 3: If still too few, split by lines and group
        if len(blocks) < 100:
            lines = text.split('\n')
            blocks = self._group_lines_into_entries(lines)

        logger.info(f"Split into {len(blocks)} blocks")
        return blocks

    def _group_lines_into_entries(self, lines: List[str]) -> List[str]:
        """Group lines into logical entry blocks"""
        blocks = []
        current_block = []
        in_entry = False

        for line in lines:
            line = line.strip()
            if not line:
                if in_entry and current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                    in_entry = False
                continue

            # Detect start of new entry - typically capitalized company name
            # with business suffix
            company_suffixes = [
                r'Ltd\.?$', r'Limited$', r'Mills$', r'Industries$',
                r'Textile$', r'Fabrics$', r'Group$', r'Corporation$',
                r'Plc$', r'Inc\.?$', r'Co\.?$', r'Enterprises$'
            ]

            is_company = any(re.search(suffix, line, re.IGNORECASE) for suffix in company_suffixes)
            is_title_case = line and line[0].isupper() and not line.isupper()

            if is_company and len(line) < 100:
                if current_block:
                    blocks.append('\n'.join(current_block))
                    current_block = []
                in_entry = True

            current_block.append(line)

        if current_block:
            blocks.append('\n'.join(current_block))

        return blocks

    def _parse_single_entry(self, entry_text: str, entry_num: int) -> Optional[Dict]:
        """Parse a single manufacturer entry"""
        entry = {
            'entry_number': entry_num,
            'raw_text': entry_text[:500]  # Store truncated raw text
        }

        lines = [l.strip() for l in entry_text.split('\n') if l.strip()]

        if not lines:
            return None

        # Line 1: Usually company name
        entry['company_name'] = self._clean_company_name(lines[0])

        # Parse remaining lines for all fields
        combined_text = ' '.join(lines[1:]) if len(lines) > 1 else ''

        # Extract contact person (might be on second line)
        if len(lines) > 1 and self._looks_like_person_name(lines[1]):
            entry['contact_person'] = lines[1]
            combined_text = ' '.join(lines[2:])
        else:
            entry['contact_person'] = ""

        # Extract ALL phone numbers
        phones = self._extract_all_phones(entry_text)
        if len(phones) >= 2:
            entry['company_phone'] = phones[0]
            entry['personal_phone'] = phones[1]
        elif len(phones) == 1:
            entry['company_phone'] = phones[0]
            entry['personal_phone'] = ""
        else:
            entry['company_phone'] = ""
            entry['personal_phone'] = ""

        # Extract ALL emails
        emails = self._extract_all_emails(entry_text)
        if len(emails) >= 2:
            entry['company_email'] = emails[0]
            entry['personal_email'] = ', '.join(emails[1:])
        elif len(emails) == 1:
            entry['company_email'] = emails[0]
            entry['personal_email'] = ""
        else:
            entry['company_email'] = ""
            entry['personal_email'] = ""

        # Extract website
        website = self._extract_website(entry_text)
        entry['website'] = website

        # Extract address (lines with road, market, street, etc.)
        address_lines = []
        for line in lines:
            if any(keyword in line.lower() for keyword in
                   ['road', 'market', 'street', 'ward', 'thana', 'district',
                    'house', 'po box', 'bashundhara', 'motijheel', 'gulshan',
                    'banani', 'panthapath', 'shahid', 'sadar']):
                address_lines.append(line)

        entry['address'] = ', '.join(address_lines) if address_lines else ""

        # Extract products/fabric types
        products = self._extract_products(entry_text)
        entry['products'] = products

        # Determine product category
        entry['product_category'] = self._categorize_products(products)

        # Check BTMA membership (often marked)
        entry['btma_member'] = 'Yes' if 'BTMA' in entry_text.upper() or 'MEMBER' in entry_text.upper() else 'No'

        return entry

    def _clean_company_name(self, name: str) -> str:
        """Clean company name"""
        # Remove extra punctuation
        name = re.sub(r'^[^\w]+|[^\w]+$', '', name)
        # Remove "Prepared by" or similar headers
        name = re.sub(r'(?i)prepared by|department of|page \d+', '', name)
        return name.strip()

    def _looks_like_person_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        # Names typically: First Last, not all caps, not addresses
        if len(text) > 50:
            return False
        if text.isupper():
            return False
        # Contains Mr., Ms., Dr., etc.
        if re.search(r'^(Mr\.|Ms\.|Dr\.|Prof\.)\s', text, re.IGNORECASE):
            return True
        # Two words with capitals
        if re.match(r'^[A-Z][a-z]+\s+[A-Z][a-z]+$', text):
            return True
        return False

    def _extract_all_phones(self, text: str) -> List[str]:
        """Extract all phone numbers from text"""
        # Bangladeshi phone patterns
        patterns = [
            r'(\+?88)?[\s\-]?0\d{2}[\s\-]?\d{6,}',  # +88 02 9882368
            r'01[\s\-]?\d{8,}',  # Mobile: 017...
            r'\(\+?88\)[\s\-]?0\d{2}[\s\-]?\d{6,}',
        ]

        phones = []
        for pattern in patterns:
            found = re.findall(pattern, text)
            phones.extend([self._clean_phone(p) for p in found])

        # Deduplicate
        return list(dict.fromkeys(phones))[:5]  # Max 5 phones

    def _clean_phone(self, phone: str) -> str:
        """Standardize phone format"""
        # Remove spaces, dashes, parens but keep country code
        phone = re.sub(r'[\s\-\(\)]', '', phone)
        # Format: +8802XXXXXXX
        if phone.startswith('880'):
            phone = '+' + phone
        elif phone.startswith('88'):
            phone = '+' + phone
        elif phone.startswith('0') and len(phone) >= 11:
            phone = '+88' + phone
        return phone

    def _extract_all_emails(self, text: str) -> List[str]:
        """Extract all email addresses from text"""
        # Standard email regex
        email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
        emails = re.findall(email_pattern, text, re.IGNORECASE)

        # Clean and deduplicate
        cleaned = []
        for email in emails:
            email = email.lower().strip()
            if email not in cleaned:
                cleaned.append(email)

        return cleaned[:5]  # Max 5 emails

    def _extract_website(self, text: str) -> str:
        """Extract website/URL"""
        # Look for www. or http patterns
        url_pattern = r'(?:www\.)?[\w\-]+\.[a-z]{2,}(?:\.[a-z]{2,})?'
        urls = re.findall(url_pattern, text, re.IGNORECASE)

        for url in urls:
            if 'www.' in url.lower() or '.com' in url.lower():
                # Normalize
                if not url.startswith('http'):
                    url = 'www.' + url if not url.startswith('www.') else url
                return url

        return ""

    def _extract_products(self, text: str) -> str:
        """Extract products/fabric types"""
        # Look for product keywords
        product_keywords = [
            'poplin', 'twill', 'oxford', 'canvas', 'denim', 'jersey',
            'interlock', 'knit', 'woven', 'satin', 'chambray', 'check',
            'striped', 'plain', 'canvas', 'corduroy', 'velvet',
            'single jersey', 'double jersey', 'pique', 'rib',
            'fleece', 'terry', 'sweater', 'shirting', 'suiting',
            'comforter', 'bedding', 'home textile'
        ]

        found_products = []
        text_lower = text.lower()

        for keyword in product_keywords:
            if keyword in text_lower:
                found_products.append(keyword.title())

        # Also look for lines with "Product:" or similar
        product_lines = re.findall(r'Product[s:]?\s+(.+?)(?:\n|$)', text, re.IGNORECASE)
        for line in product_lines:
            items = [i.strip() for i in line.split(',')]
            found_products.extend([i.title() for i in items if len(i) > 2 and i.lower() not in [p.lower() for p in found_products]])

        return ', '.join(list(dict.fromkeys(found_products)))

    def _categorize_products(self, products: str) -> str:
        """Categorize based on products listed"""
        products_lower = products.lower()

        categories = {
            'Denim': ['denim'],
            'Knitted Fabrics': ['jersey', 'interlock', 'pique', 'rib', 'knit', 'fleece', 'terry'],
            'Woven Fabrics': ['poplin', 'twill', 'oxford', 'canvas', 'satin', 'chambray', 'plain', 'corduroy'],
            'Home Textile': ['comforter', 'bedding', 'home textile', 'sweater'],
            'Shirting': ['shirting'],
            'Suiting': ['suiting']
        }

        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in products_lower:
                    return category

        return 'Textile/Fabrics'

    def _is_valid_entry(self, entry: Dict) -> bool:
        """Validate entry has minimum required data"""
        company = entry.get('company_name', '')
        # Must have company name with at least 5 characters
        if not company or len(company) < 5:
            return False
        # Exclude header/footer lines
        exclude_patterns = [
            r'^Page \d+',
            r'^CONTINUED',
            r'^\[?[\d.]+\]?\s*$',  # Just numbers
            r'^Annual Report',
            r'^General',
        ]
        for pattern in exclude_patterns:
            if re.match(pattern, company):
                return False
        return True


def parse_btma_directory_text(text: str) -> pd.DataFrame:
    """
    Quick function to parse BTMA directory text

    Args:
        text: Raw text extracted from PDF

    Returns:
        pd.DataFrame with all manufacturer entries
    """
    parser = BTMADirectoryParser()
    parser.load_text(text)
    return parser.parse_all_entries()
