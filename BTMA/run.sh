#!/bin/bash
# BTMA Data Extractor - Launcher Script
# Usage: ./run.sh [options]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/venv"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}  BTMA Fabric Manufacturer Data Extractor${NC}"
echo -e "${GREEN}==================================================${NC}"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${YELLOW}Installing dependencies...${NC}"
    source "$VENV_DIR/bin/activate"
    pip install -q -r "$SCRIPT_DIR/pdf_data_extractor/requirements.txt"
else
    source "$VENV_DIR/bin/activate"
fi

# Check if main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}Error: main.py not found in $SCRIPT_DIR${NC}"
    exit 1
fi

# Run with provided arguments
echo ""
python3 "$MAIN_SCRIPT" "$@"
EXIT_CODE=$?

echo ""
echo -e "${GREEN}==================================================${NC}"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}Completed successfully!${NC}"
else
    echo -e "${RED}Failed with exit code: $EXIT_CODE${NC}"
fi
echo -e "${GREEN}==================================================${NC}"

exit $EXIT_CODE
