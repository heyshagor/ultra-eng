"""
Enhanced PDF Extractor for BTMA Directory
Captures all text and tables comprehensively
"""

import pdfplumber
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from .advanced_parser import parse_btma_directory_text

logger = logging.getLogger(__name__)


class EnhancedPDFExtractor:
    """Enhanced extractor for full text capture"""

    def __init__(self, pdf_path: str, use_ocr: bool = False):
        self.pdf_path = pdf_path
        self.use_ocr = use_ocr
        self.all_pages_text = []
        self.tables = []

    def extract_comprehensive(self) -> Dict[str, Any]:
        """Extract ALL text from PDF with better capture"""
        logger.info(f"Extracting comprehensive data from: {self.pdf_path}")

        all_text_parts = []

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                logger.info(f"Total pages: {len(pdf.pages)}")

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.debug(f"Processing page {page_num}")

                    # Extract text with different strategies
                    text = page.extract_text()

                    # If text extraction gave little result, try alternatives
                    if not text or len(text.strip()) < 100:
                        # Try extracting with different settings
                        text = page.extract_text(x_tolerance=2, y_tolerance=2)

                        if not text or len(text.strip()) < 100:
                            # Try raw extraction
                            text = page.extract_text(layout=True)

                    if text:
                        all_text_parts.append(text)
                        self.all_pages_text.append({
                            'page': page_num,
                            'text': text
                        })

                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            self.tables.append({
                                'page': page_num,
                                'data': pd.DataFrame(table)
                            })

                # Combine all text
                full_text = '\n\n'.join(all_text_parts)

                logger.info(f"Extracted {len(full_text)} characters total")
                logger.info(f"Found {len(self.tables)} tables")

                # Try to parse as directory
                df_parsed = parse_btma_directory_text(full_text)
                logger.info(f"Parsed {len(df_parsed)} manufacturer entries")

                return {
                    'full_text': full_text,
                    'pages': self.all_pages_text,
                    'tables': self.tables,
                    'parsed_data': df_parsed,
                    'metadata': {
                        'total_pages': len(pdf.pages),
                        'total_chars': len(full_text),
                        'entries_parsed': len(df_parsed),
                        'tables_found': len(self.tables)
                    }
                }

        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise

    def save_all_formats(self, base_name: str = 'btma_data'):
        """Extract and save in all formats"""
        logger.info("Starting comprehensive extraction...")
        results = self.extract_comprehensive()

        saved_files = {}

        # 1. Save raw full text
        text_file = f"{base_name}_full_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(results['full_text'])
        saved_files['text'] = text_file
        logger.info(f"Saved full text: {text_file}")

        # 2. Save all extracted tables (if any)
        if self.tables:
            tables_file = f"{base_name}_tables.xlsx"
            with pd.ExcelWriter(tables_file, engine='openpyxl') as writer:
                for i, table in enumerate(self.tables, 1):
                    sheet_name = f"Table_{i}"
                    table['data'].to_excel(writer, sheet_name=sheet_name, index=False)
            saved_files['tables'] = tables_file
            logger.info(f"Saved tables: {tables_file}")

        # 3. Save parsed directory data (main output)
        if 'parsed_data' in results and not results['parsed_data'].empty:
            csv_file = f"{base_name}_directory.csv"
            results['parsed_data'].to_csv(csv_file, index=False, encoding='utf-8-sig')
            saved_files['csv_directory'] = csv_file
            logger.info(f"Saved directory CSV: {csv_file}")

            excel_file = f"{base_name}_directory.xlsx"
            results['parsed_data'].to_excel(excel_file, index=False, engine='openpyxl')
            saved_files['excel_directory'] = excel_file
            logger.info(f"Saved directory Excel: {excel_file}")

        # 4. Create multi-sheet Excel with everything
        full_excel = f"{base_name}_complete.xlsx"
        with pd.ExcelWriter(full_excel, engine='openpyxl') as writer:
            # Summary
            summary = pd.DataFrame({
                'Metric': ['Total Pages', 'Total Characters', 'Entries Parsed', 'Tables Found'],
                'Value': [
                    results['metadata']['total_pages'],
                    results['metadata']['total_chars'],
                    results['metadata']['entries_parsed'],
                    len(self.tables)
                ]
            })
            summary.to_excel(writer, sheet_name='Summary', index=False)

            # Parsed data
            if 'parsed_data' in results and not results['parsed_data'].empty:
                results['parsed_data'].to_excel(writer, sheet_name='All_Entries', index=False)

            # Tables
            for i, table in enumerate(self.tables, 1):
                sheet_name = f"Table_{i}"[:31]
                table['data'].to_excel(writer, sheet_name=sheet_name, index=False)

        saved_files['excel_complete'] = full_excel
        logger.info(f"Saved complete Excel: {full_excel}")

        return saved_files, results


def extract_full_directory(pdf_path: str, output_base: str = 'btma_data') -> Dict:
    """
    Extract ALL data from BTMA directory PDF

    Args:
        pdf_path: Path to PDF file
        output_base: Base name for output files

    Returns:
        Dict with results and saved file paths
    """
    extractor = EnhancedPDFExtractor(pdf_path)
    return extractor.save_all_formats(output_base)
