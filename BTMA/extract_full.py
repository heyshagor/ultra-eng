#!/usr/bin/env python3
"""
BTMA Full Directory Extractor
Extracts ALL manufacturers (300+) with complete contact details
"""

import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_data_extractor.enhanced_extractor import EnhancedPDFExtractor


def main():
    parser = argparse.ArgumentParser(
        description='BTMA Full Directory Extractor - Extract ALL manufacturer data with complete details',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf
  %(prog)s input.pdf -o mydirectory
  %(prog)s input.pdf --ocr --verbose
        """
    )

    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('-o', '--output', default='btma_full_data',
                       help='Output base name (default: btma_full_data)')
    parser.add_argument('--ocr', action='store_true',
                       help='Enable OCR for scanned PDFs')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    logger = logging.getLogger(__name__)

    print("\n" + "="*70)
    print(" BTMA FULL DIRECTORY EXTRACTOR")
    print("="*70)
    print(f"\nInput PDF: {args.input}")
    print(f"Output base: {args.output}")
    print(f"OCR: {'Enabled' if args.ocr else 'Disabled'}")
    print("\nThis will extract:")
    print("  • All manufacturer entries (300+)")
    print("  • Company names, contact persons")
    print("  • Multiple phone numbers")
    print("  • Multiple email addresses")
    print("  • Websites, addresses, products")
    print("  • BTMA membership status")
    print("="*70 + "\n")

    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found!")
        sys.exit(1)

    try:
        logger.info("Initializing enhanced extractor...")
        extractor = EnhancedPDFExtractor(args.input, use_ocr=args.ocr)

        logger.info("Starting comprehensive extraction...")
        saved_files, results = extractor.save_all_formats(args.output)

        print("\n" + "="*70)
        print(" EXTRACTION COMPLETE!")
        print("="*70)

        print("\n📄 Files Generated:")
        for file_type, filepath in saved_files.items():
            print(f"  ✓ {file_type}: {filepath}")

        print("\n📊 Summary:")
        print(f"  • Total pages: {results['metadata']['total_pages']}")
        print(f"  • Characters extracted: {results['metadata']['total_chars']:,}")
        print(f"  • Manufacturer entries: {results['metadata']['entries_parsed']}")
        print(f"  • Tables found: {results['metadata']['tables_found']}")

        if 'parsed_data' in results and not results['parsed_data'].empty:
            df = results['parsed_data']
            print(f"\n📈 Data Statistics:")
            print(f"  • Total records: {len(df)}")
            print(f"  • Columns: {len(df.columns)}")
            print(f"  • BTMA members: {df['btma_member'].value_counts().get('Yes', 0)}")
            print(f"  • With website: {(df['website'] != '').sum()}")
            print(f"  • With multiple emails: {(df['additional_emails'] != '').sum()}")

            print(f"\n📋 Sample of extracted data (first 5):")
            print("\n" + df.head(5).to_string())

        print("\n" + "="*70)
        print(" All data saved successfully!")
        print("="*70 + "\n")

    except Exception as e:
        logger.error(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nTroubleshooting:")
        print("  • Ensure the PDF file is valid and not password protected")
        print("  • For scanned PDFs, install Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
        print("  • Try --verbose for detailed error output")
        sys.exit(1)


if __name__ == '__main__':
    main()
