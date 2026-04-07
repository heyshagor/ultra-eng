"""
Configuration settings for PDF Data Extractor
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.resolve()

# Default paths
DEFAULT_INPUT_PDF = "B-Fabric-Manufacturer-of-BTMA_General.pdf"
DEFAULT_EXCEL_OUTPUT = "btma_fabric_data.xlsx"
DEFAULT_CSV_OUTPUT = "btma_fabric_data.csv"

# OCR settings
OCR_ENABLED = False
TESSERACT_PATH = None  # Set to tesseract executable path if not in PATH
PDF2IMAGE_DPI = 200

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Data parsing settings
COMPANY_NAME_PATTERNS = [
    r'^[A-Z][A-Z\s\.&]+$',
    r'^[A-Z][a-zA-Z\s\.&]+(?:\s+Ltd\.?)?$',
]

# Email regex pattern
EMAIL_REGEX = r'[\w\.-]+@[\w\.-]+\.\w+'

# Phone regex pattern
PHONE_REGEX = r'(\+?88)?[\s\-]?[\d\s]{10,}'

# Company address keywords
ADDRESS_KEYWORDS = [
    'road', 'market', 'street', 'po box', 'ward', 'thana',
    'district', 'house', 'road no', 'shahid', 'sadar'
]

class Config:
    """Configuration container"""

    def __init__(self, config_dict: dict = None):
        self.config_dict = config_dict or {}
        self._load_from_env()

    def _load_from_env(self):
        """Load configuration from environment variables"""
        env_vars = {
            'OCR_ENABLED': 'OCR_ENABLED',
            'TESSERACT_PATH': 'TESSERACT_PATH',
            'LOG_LEVEL': 'LOG_LEVEL',
            'DEFAULT_INPUT_PDF': 'PDF_INPUT_PATH',
            'DEFAULT_EXCEL_OUTPUT': 'EXCEL_OUTPUT_PATH',
            'DEFAULT_CSV_OUTPUT': 'CSV_OUTPUT_PATH'
        }

        for attr, env_var in env_vars.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                if attr in ['OCR_ENABLED']:
                    value = value.lower() in ['true', '1', 'yes']
                setattr(self, attr, value)

    def __getattr__(self, name):
        if name in self.config_dict:
            return self.config_dict[name]
        return globals().get(name)

config = Config()
