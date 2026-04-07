.PHONY: help install test clean run run-ocr sample full full-ocr

# Default target
help:
	@echo "=================================================="
	@echo "BTMA Fabric Manufacturer Data Extractor"
	@echo "=================================================="
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  install      Install dependencies in venv"
	@echo "  test         Run test suite"
	@echo "  run          Extract from default PDF"
	@echo "  run-ocr      Extract with OCR enabled"
	@echo "  sample       Generate sample data only"
	@echo "  full         Full directory extraction (300+ entries)"
	@echo "  full-ocr     Full extraction with OCR (requires tesseract)"
	@echo "  clean        Remove generated files"
	@echo "  clean-all    Remove venv and all generated files"
	@echo ""

# Create virtual environment and install
install:
	@echo "Creating virtual environment and installing dependencies..."
	python3 -m venv venv
	@source venv/bin/activate && pip install -r pdf_data_extractor/requirements.txt
	@echo "Done. Activate with: source venv/bin/activate"

# Run tests
test:
	@source venv/bin/activate && python test_extractor.py

# Extract from default PDF (basic)
run:
	@source venv/bin/activate && python main.py

# Extract with OCR
run-ocr:
	@source venv/bin/activate && python main.py --ocr

# Generate sample data
sample:
	@source venv/bin/activate && python main.py --test

# Generate full sample dataset (320 entries with all fields)
full:
	@source venv/bin/activate && python generate_full_sample.py

# Full directory extraction from PDF with OCR
full-ocr:
	@source venv/bin/activate && python extract_full.py "B-Fabric-Manufacturer-of-BTMA_General.pdf" --ocr -v

# Clean generated files
clean:
	@echo "Removing output files..."
	rm -f btma_*.xlsx btma_*.csv demo_*.xlsx demo_*.csv *.csv *.xlsx full_*.csv full_*.xlsx full_*.txt
	rm -rf __pycache__ .pytest_cache /tmp/tmp*
	@echo "Output files removed"

# Deep clean (including venv)
clean-all: clean
	@echo "Removing virtual environment..."
	rm -rf venv
	@echo "Complete cleanup done"
