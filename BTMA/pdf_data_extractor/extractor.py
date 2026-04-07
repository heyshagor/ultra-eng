"""
PDF Data Extractor Module
Extracts structured data from PDF files and exports to Excel/CSV
"""

import pdfplumber
import re
import pandas as pd
from typing import List, Dict, Optional, Union
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFExtractor:
    """Main class for extracting data from PDF files"""

    def __init__(self, pdf_path: str, use_ocr: bool = False):
        """
        Initialize PDF Extractor

        Args:
            pdf_path: Path to the PDF file
            use_ocr: Enable OCR for scanned/image-based PDFs (requires pytesseract)
        """
        self.pdf_path = pdf_path
        self.use_ocr = use_ocr
        self.pages_data = []
        self.tables = []

    def extract_all(self) -> Dict:
        """
        Extract all data from PDF

        Returns:
            Dictionary containing extracted text, tables, and metadata
        """
        logger.info(f"Extracting data from: {self.pdf_path}")

        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.metadata = {
                    'total_pages': len(pdf.pages),
                    'file_name': self.pdf_path.split('/')[-1]
                }

                for page_num, page in enumerate(pdf.pages, 1):
                    logger.info(f"Processing page {page_num}...")

                    # Extract text
                    text = page.extract_text()
                    if not text and self.use_ocr:
                        text = self._extract_with_ocr(page)

                    # Extract tables
                    tables = page.extract_tables()

                    page_data = {
                        'page_number': page_num,
                        'text': text or '',
                        'tables': tables,
                        'dimensions': {
                            'width': page.width,
                            'height': page.height
                        }
                    }
                    self.pages_data.append(page_data)

                logger.info("Extraction completed successfully")
                return self._structure_output()

        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise

    def _extract_with_ocr(self, page) -> str:
        """Extract text using OCR (pytesseract) - Optional dependency"""
        try:
            from pdf2image import convert_from_path
            import pytesseract

            # Convert PDF page to image
            images = convert_from_path(
                self.pdf_path,
                first_page=page.page_number,
                last_page=page.page_number
            )

            if images:
                # Extract text from image
                text = pytesseract.image_to_string(images[0])
                return text
        except ImportError:
            logger.warning("OCR dependencies not installed. Install: pip install pytesseract pdf2image")
            return None
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return None

    def _structure_output(self) -> Dict:
        """Structure the extracted data into a clean format"""
        output = {
            'metadata': self.metadata,
            'pages': self.pages_data
        }

        # Combine all text
        all_text = '\n'.join([p['text'] for p in self.pages_data if p['text']])
        output['full_text'] = all_text

        # Flatten tables
        all_tables = []
        for page in self.pages_data:
            for table_idx, table in enumerate(page['tables'], 1):
                df = pd.DataFrame(table)
                all_tables.append({
                    'page': page['page_number'],
                    'table_number': table_idx,
                    'data': df
                })
        output['tables'] = all_tables

        return output

    def to_csv(self, output_path: str, table_num: Optional[int] = None) -> str:
        """
        Export extracted data to CSV

        Args:
            output_path: Path for output CSV file
            table_num: Specific table number to export (None = all tables combined)

        Returns:
            Path to saved CSV file
        """
        if not self.pages_data:
            raise ValueError("No data extracted. Call extract_all() first.")

        # Combine all table data
        all_dfs = []
        for page in self.pages_data:
            for table in page['tables']:
                df = pd.DataFrame(table)
                df['page_number'] = page['page_number']
                all_dfs.append(df)

        if not all_dfs:
            # Export text as CSV with one row per line
            lines = []
            for page in self.pages_data:
                if page['text']:
                    for line in page['text'].split('\n'):
                        lines.append({'page': page['page_number'], 'text': line})
            final_df = pd.DataFrame(lines)
        else:
            final_df = pd.concat(all_dfs, ignore_index=True)

        # Save to CSV
        final_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"CSV saved to: {output_path}")
        return output_path

    def to_excel(self, output_path: str, sheet_names: Optional[List[str]] = None) -> str:
        """
        Export extracted data to Excel with multiple sheets

        Args:
            output_path: Path for output Excel file
            sheet_names: Custom names for sheets (auto-generated if None)

        Returns:
            Path to saved Excel file
        """
        if not self.pages_data:
            raise ValueError("No data extracted. Call extract_all() first.")

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                'Property': ['Total Pages', 'File Name', 'Tables Found', 'Pages with Text'],
                'Value': [
                    self.metadata['total_pages'],
                    self.metadata['file_name'],
                    len([t for p in self.pages_data for t in p['tables']]),
                    len([p for p in self.pages_data if p['text']])
                ]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)

            # Data sheets
            table_count = 0
            for page in self.pages_data:
                if page['tables']:
                    for table_idx, table in enumerate(page['tables'], 1):
                        table_count += 1
                        df = pd.DataFrame(table)
                        sheet_name = f"Page{page['page_number']}_Table{table_idx}"[:31]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

            # If no tables, create text sheet
            if table_count == 0:
                text_data = []
                for page in self.pages_data:
                    if page['text']:
                        for line_num, line in enumerate(page['text'].split('\n'), 1):
                            text_data.append({
                                'page': page['page_number'],
                                'line_number': line_num,
                                'text': line
                            })
                pd.DataFrame(text_data).to_excel(writer, sheet_name='Text', index=False)

        logger.info(f"Excel saved to: {output_path}")
        return output_path


def extract_pdf_to_excel(pdf_path: str, excel_path: str, use_ocr: bool = False) -> str:
    """Quick function to extract PDF to Excel"""
    extractor = PDFExtractor(pdf_path, use_ocr=use_ocr)
    extractor.extract_all()
    return extractor.to_excel(excel_path)


def extract_pdf_to_csv(pdf_path: str, csv_path: str, use_ocr: bool = False) -> str:
    """Quick function to extract PDF to CSV"""
    extractor = PDFExtractor(pdf_path, use_ocr=use_ocr)
    extractor.extract_all()
    return extractor.to_csv(csv_path)
