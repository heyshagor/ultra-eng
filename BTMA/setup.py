#!/usr/bin/env python3
"""
Setup script for BTMA PDF Data Extractor
Run: pip install -e .
"""

from setuptools import setup, find_packages
import os

# Read long description from README
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="btma-pdf-extractor",
    version="1.0.0",
    author="BTMA Data Team",
    description="Extract and manage BTMA fabric manufacturer data from PDF to Excel/CSV",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pdfplumber>=0.11.0",
        "pandas>=3.0.0",
        "openpyxl>=3.1.0",
    ],
    extras_require={
        "ocr": [
            "pytesseract>=0.3.10",
            "pdf2image>=1.17.0",
            "Pillow>=9.1.0"
        ]
    },
    entry_points={
        "console_scripts": [
            "btma-extract=pdf_data_extractor.cli:main",
            "btma-main=main:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Manufacturing",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Office/Business :: Financial",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    keywords="pdf extractor excel csv btma textile fabric manufacturer data",
    project_urls={
        "Bug Reports": "https://github.com/btma/pdf-extractor/issues",
        "Source": "https://github.com/btma/pdf-extractor",
    },
)
