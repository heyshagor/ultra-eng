#!/usr/bin/env python3
"""
BTMA Fabric Manufacturer Data Extractor - Main Entry Point

This script extracts all information from the BTMA PDF and exports it to
Excel and CSV formats with structured parsing.

Usage:
    python main.py [options]

Options:
    --input PATH        Path to PDF file (default: B-Fabric-Manufacturer-of-BTMA_General.pdf)
    --excel PATH        Excel output path (default: btma_fabric_data.xlsx)
    --csv PATH          CSV output path (default: btma_fabric_data.csv)
    --parse             Parse structured data (companies, products, contacts)
    --all-sheets        Create multi-sheet Excel with all parsed data
    --ocr               Enable OCR for scanned PDFs
    --verbose           Enable debug logging
    --test              Run in test mode (create sample data)
"""

import os
import sys
import argparse
from pathlib import Path
import pandas as pd

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pdf_data_extractor.extractor import PDFExtractor
from pdf_data_extractor.parser import BTMAParser


def create_sample_data():
    """Create sample data for testing when PDF is not readable"""
    print("Creating sample BTMA fabric manufacturer data...")

    # Sample BTMA fabric manufacturer data structure
    sample_data = {
        'Manufacturer Name': [
            'ABM Industries Ltd.',
            'Apex Textile Mills Ltd.',
            'Beximco Textiles Ltd.',
            'Square Textiles Ltd.',
            'Pacific Textiles Ltd.',
            'Fakir Group',
            'Noman Group',
            'M.M. Textiles Ltd.',
            'H.R.Textiles',
            'DBL Group'
        ],
        'Address': [
            'House # 06, Road # 23, Gulshan-1, Dhaka-1212',
            '185, Nayabazsr, Narayanganj-1400',
            'Beximco Industrial Park, Dhaka-Barisal Road, Dhaka',
            'Square Centre, 274, Faiz Ahmed Faiz Road, Panthapath, Dhaka',
            'House # 08, Road # 02, Banani, Dhaka-1213',
            'Fakir Chamber, 49, Dilkusha C/A, Motijheel, Dhaka-1000',
            'Noman Centre, 273,/D, Bir Uttam CR Dutta Road, Dhaka-1205',
            'M.M. Tower, 28, Kemal Ataturk Avenue, Banani, Dhaka',
            'H.R. Tower, 30, Shaymoli, Dhaka',
            'DBL Centre, 27, Bijoy Nagar, Dhaka-1000'
        ],
        'Phone': [
            '+88 02 9882368',
            '+88 02 7646215',
            '+88 02 9005025',
            '+88 02 9120124',
            '+88 02 8851041',
            '+88 02 9562241',
            '+88 02 8612461',
            '+88 02 8953251',
            '+88 02 9141022',
            '+88 02 9123456'
        ],
        'Email': [
            'info@abmind.com',
            'contact@apex-textile.com',
            'info@beximco.com',
            'info@squaretextiles.com',
            'info@pacific-textiles.com',
            'info@fakirgroup.com',
            'contact@nomangroup.com',
            'info@mmtextiles.com',
            'info@hrtextiles.com',
            'info@dblgroup.com'
        ],
        'Website': [
            'www.abmind.com',
            'www.apex-textile.com',
            'www.beximco.com',
            'www.squaretextiles.com',
            'www.pacific-textiles.com',
            'www.fakirgroup.com',
            'www.nomangroup.com',
            'www.mmtextiles.com',
            'www.hrtextiles.com',
            'www.dblgroup.com'
        ],
        'Product Category': [
            'Woven Fabrics',
            'Knitted Fabrics',
            'Woven & Knitted',
            'Denim Fabrics',
            'Woven Fabrics',
            'Textile Processing',
            'Complete Textile Solution',
            'Fabrics & Garments',
            'Knit Fabrics',
            'Textile & Garments'
        ],
        'Key Products': [
            'Poplin, Twill, Oxford, Canvas',
            'Single Jersey, Double Jersey, Interlock',
            'Woven, Knit, Denim, Terry',
            'Denim, Comforters, Shirting',
            'Plain Weave, Twill, Satin',
            'Processing, Weaving, Knitting',
            'Spinning, Weaving, Processing, Garments',
            'Woven Shirtings, Suitings',
            'Pique, Rib, Lacoste',
            'Knit, Woven, Sweater, Garments'
        ],
        'BTMA Member': [
            'Yes',
            'Yes',
            'Yes',
            'Yes',
            'Yes',
            'Yes',
            'Yes',
            'Yes',
            'Yes',
            'Yes'
        ]
    }

    df = pd.DataFrame(sample_data)

    return df


def main():
    parser = argparse.ArgumentParser(
        description='BTMA Fabric Manufacturer Data Extractor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from default PDF
  python main.py

  # Extract with OCR for scanned PDF
  python main.py --ocr

  # Extract and parse with all features
  python main.py --parse --all-sheets --verbose

  # Use custom input/output
  python main.py --input custom.pdf --excel output.xlsx --csv output.csv

  # Test mode (create sample data)
  python main.py --test
        """
    )

    parser.add_argument('--input', default='B-Fabric-Manufacturer-of-BTMA_General.pdf',
                       help='Input PDF file path (default: B-Fabric-Manufacturer-of-BTMA_General.pdf)')
    parser.add_argument('--excel', default='btma_fabric_data.xlsx',
                       help='Excel output path (default: btma_fabric_data.xlsx)')
    parser.add_argument('--csv', default='btma_fabric_data.csv',
                       help='CSV output path (default: btma_fabric_data.csv)')
    parser.add_argument('--parse', action='store_true',
                       help='Parse structured data')
    parser.add_argument('--all-sheets', action='store_true',
                       help='Create multi-sheet Excel with parsed data')
    parser.add_argument('--ocr', action='store_true',
                       help='Enable OCR for scanned PDFs')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--test', action='store_true',
                       help='Create sample dataset for testing')

    args = parser.parse_args()

    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )
    logger = logging.getLogger(__name__)

    print("\n" + "="*60)
    print(" BTMA FABRIC MANUFACTURER DATA EXTRACTOR")
    print("="*60 + "\n")

    # Test mode: create sample data
    if args.test:
        print("Running in TEST MODE - creating sample dataset\n")
        import pandas as pd

        df = create_sample_data()

        # Save to Excel
        df.to_excel(args.excel, index=False)
        print(f"✓ Sample Excel created: {args.excel}")

        # Save to CSV
        df.to_csv(args.csv, index=False, encoding='utf-8-sig')
        print(f"✓ Sample CSV created: {args.csv}")

        # Create parsed multi-sheet if requested
        if args.all_sheets:
            from pdf_data_extractor.parser import BTMAParser
            parser_obj = BTMAParser()
            parser_obj.parsed_data = {
                'companies': df[['Manufacturer Name', 'Address', 'Phone', 'Email', 'Website']],
                'products': df[['Manufacturer Name', 'Product Category', 'Key Products']],
                'contacts': df[['Manufacturer Name', 'Phone', 'Email', 'Website']]
            }
            parser_obj.to_excel_multisheet('btma_sample_parsed.xlsx')
            print(f"✓ Sample parsed multi-sheet Excel: btma_sample_parsed.xlsx")

        print("\n" + "="*60)
        print(" Sample data generation completed!")
        print("="*60)
        return

    # Normal mode: process PDF
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found!")
        print("\nPlease ensure:")
        print("1. The PDF file exists in the current directory")
        print("2. You have the correct filename")
        print("3. You have read permissions for the file")
        print("\nOr run with --test to create sample data.")
        sys.exit(1)

    try:
        logger.info(f"Input: {args.input}")
        logger.info(f"Output Excel: {args.excel}")
        logger.info(f"Output CSV: {args.csv}")

        # Step 1: Extract data
        print("\n[1/3] Extracting data from PDF...")
        extractor = PDFExtractor(args.input, use_ocr=args.ocr)
        data = extractor.extract_all()

        print(f"  • Pages: {data['metadata']['total_pages']}")
        print(f"  • Tables found: {len(data['tables'])}")

        # Export to Excel
        print("\n[2/3] Exporting to Excel...")
        extractor.to_excel(args.excel)

        # Export to CSV
        print("\n[3/3] Exporting to CSV...")
        extractor.to_csv(args.csv)

        print(f"\n✓ Excel: {args.excel}")
        print(f"✓ CSV: {args.csv}")

        # Step 2: Parse structured data if requested
        if args.parse or args.all_sheets:
            print("\n[4/4] Parsing structured data...")
            parser = BTMAParser()
            parser.load_from_extractor(extractor)
            parser.parse_all()

            parsed_data = parser.get_all_parsed()
            for name, df in parsed_data.items():
                print(f"  • {name.title()}: {len(df)} records")

            if args.all_sheets:
                parsed_excel = Path(args.excel).stem + '_parsed.xlsx'
                parser.to_excel_multisheet(parsed_excel)
                print(f"\n✓ Parsed multi-sheet Excel: {parsed_excel}")

        print("\n" + "="*60)
        print(" Extraction & export completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        logger.error(f"\nError: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        print("\nTroubleshooting:")
        print("1. Ensure the PDF is not password protected")
        print("2. For scanned PDFs, use --ocr flag (requires pytesseract & pdf2image)")
        print("3. Try --verbose for detailed error messages")
        sys.exit(1)


if __name__ == '__main__':
    main()
