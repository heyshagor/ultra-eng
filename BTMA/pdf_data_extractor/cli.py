"""
Command Line Interface for PDF Data Extractor
"""

import argparse
import sys
import os
from pathlib import Path
from .extractor import PDFExtractor, extract_pdf_to_excel, extract_pdf_to_csv
from .parser import BTMAParser

def main():
    parser = argparse.ArgumentParser(
        description='BTMA Fabric Manufacturer PDF Data Extractor - Extract and manage PDF data to Excel/CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.pdf -o output.xlsx
  %(prog)s input.pdf -o output.csv --format csv
  %(prog)s input.pdf --parse --all-sheets
  %(prog)s input.pdf --ocr --verbose
        """
    )

    parser.add_argument('input', help='Input PDF file path')
    parser.add_argument('-o', '--output', help='Output file path (auto-generated if not specified)')
    parser.add_argument('--format', choices=['excel', 'csv'], default='excel',
                       help='Output format (default: excel)')
    parser.add_argument('--ocr', action='store_true',
                       help='Enable OCR for scanned/image PDFs (requires pytesseract & pdf2image)')
    parser.add_argument('--parse', action='store_true',
                       help='Parse data into structured format (companies, products, contacts)')
    parser.add_argument('--all-sheets', action='store_true',
                       help='Create multi-sheet Excel with parsed data (implies --parse)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0.0')

    args = parser.parse_args()

    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(levelname)s: %(message)s'
    )

    # Validate input file
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found!")
        sys.exit(1)

    # Generate output filename if not provided
    if not args.output:
        input_path = Path(args.input)
        if args.format == 'excel':
            args.output = f"{input_path.stem}_extracted.xlsx"
        else:
            args.output = f"{input_path.stem}_extracted.csv"

    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Processing: {args.input}")
        logger.info(f"Output: {args.output}")
        logger.info(f"Format: {args.format}")
        logger.info(f"OCR: {'Enabled' if args.ocr else 'Disabled'}")

        # Extract data
        if args.format == 'excel':
            output_path = extract_pdf_to_excel(args.input, args.output, use_ocr=args.ocr)
        else:
            output_path = extract_pdf_to_csv(args.input, args.output, use_ocr=args.ocr)

        print(f"\n✓ Extraction complete: {output_path}")

        # Parse data if requested
        if args.parse or args.all_sheets:
            logger.info("\nParsing structured data...")
            extractor = PDFExtractor(args.input, use_ocr=args.ocr)
            extractor.extract_all()

            parser = BTMAParser()
            parser.load_from_extractor(extractor)
            parser.parse_all()

            if args.all_sheets:
                parsed_output = f"{Path(args.output).stem}_parsed.xlsx"
                parser.to_excel_multisheet(parsed_output)
                print(f"✓ Parsed data (multi-sheet): {parsed_output}")
            else:
                # Export individual CSVs
                for name, df in parser.get_all_parsed().items():
                    csv_name = f"{Path(args.output).stem}_{name}.csv"
                    df.to_csv(csv_name, index=False, encoding='utf-8-sig')
                    print(f"✓ {name.title()} data: {csv_name}")

        print("\n" + "="*50)
        print("Processing completed successfully!")
        print("="*50)

    except Exception as e:
        logger.error(f"Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
